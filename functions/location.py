import os, time, folium, csv, requests, numpy as np
from dotenv import load_dotenv
from pyicloud import PyiCloudService
from database import update_database, get_database_value
from math import pi
from sklearn.linear_model import LinearRegression



def load_api():
    load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
    iCloud_user = os.getenv("iCloud_user")
    iCloud_pass = os.getenv("iCloud_pass")
    api = PyiCloudService(iCloud_user, iCloud_pass)
    return api


def get_device():
    devices = load_api().devices
    for device in devices:
        if device.get('deviceClass') == 'iPhone': 
            return device


def update_map(map, latitude, longitude):
    folium.Marker([latitude, longitude]).add_to(map)
    map.save('/Users/pearlnatalia/Desktop/car/geolocation/map.html')


def get_csv_value(row):
    csv_path = "/Users/pearlnatalia/desktop/car/geolocation/red-light-cameras.csv"
    with open(csv_path, mode='r') as file:
        csv_reader = csv.reader(file)
        return list(csv_reader)[row]


def get_street_name(api_key, lat, long):
    url = f"https://revgeocode.search.hereapi.com/v1/revgeocode?at={lat},{long}&apiKey={api_key}"

    response = requests.get(url)
    if(response.status_code == 200):
        data = response.json()
        if('street' in data['items'][0]['address']):
            return data['items'][0]['address']['street']
    return None


def get_driving_distance(api_key, target_coordinate, current_coordinate):    
    base_url = "https://router.hereapi.com/v8/routes"
    params = {
        "transportMode": "car",
        "origin": current_coordinate,
        "destination": target_coordinate,
        "return": "summary",
        "apiKey": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['routes'][0]['sections'][0]['summary']['length']
    return -1


def format_address(current_street):
    if current_street is None:
        return None
    long_form = {
        " N": " North", " E": " East", " S": " South", " W": " West",
        " Rd": " Road", " St": " Street", " Av": " Avenue",
        " Blvd": " Boulevard", " Dr": " Drive" 
    }
    for abbreviation, full in long_form.items(): # abbreviations with spaces
        current_street = current_street.replace(abbreviation + " ", full + " ")
    for abbreviation, full in long_form.items(): # abbreviations without spaces
        if current_street.endswith(abbreviation):
            current_street = current_street[:-len(abbreviation)] + full
    return current_street


def get_red_light_camera(lat, long):  
    if(long<-81 or long>-74): # not in dataset
        return None
    
    red_intersection, red_region = "", ""
    red_lat, red_long = 0.0, 0.0
    distance = -1
    intersection, region = "", ""

    # reverse geocoding api
    load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
    API_KEY = os.getenv("HERE_API_KEY")
    ENTRY_COUNT = 408
   
    current_street = format_address(get_street_name(API_KEY, lat, long))
    if(current_street is None): return None
    for row in range(2, ENTRY_COUNT):
        values = get_csv_value(row)
        red_intersection, red_lat, red_long, red_region = values[0], values[1], values[2], values[3]
        if (current_street in red_intersection):
            temp_distance = get_driving_distance(API_KEY, str(red_lat)+","+str(red_long), str(lat)+","+str(long))
            if(distance==-1 and temp_distance<=200):
                distance = temp_distance
                intersection = red_intersection
                region = red_region
            elif(temp_distance<distance):
                distance = temp_distance
                intersection = red_intersection
                region = red_region

    if(intersection and distance!=-1):
        print("Red light camera approaching in", distance, "m at", intersection)
        return intersection + ", " + region, current_street
    else:
        print("No red light cameras near", current_street), current_street
        return None, current_street


def get_time_difference(prev_time, curr_time):
    prev_h, prev_m, prev_s = map(int, prev_time)
    curr_h, curr_m, curr_s = map(int, curr_time)
    prev_total_seconds = prev_h * 3600 + prev_m * 60 + prev_s
    curr_total_seconds = curr_h * 3600 + curr_m * 60 + curr_s
    return abs(prev_total_seconds - curr_total_seconds)


def detect_speeding(lat, long, api_key, speed):
    base_url = "https://routematching.hereapi.com/v8/match/routelinks"
    params = {
        "apikey": api_key,
        "waypoint0": lat+","+long,
        "mode": "fastest;car",
        "routeMatch": "1",
        "attributes": "SPEED_LIMITS_FCn(*)"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()['response']['route'][0]['leg'][0]['link'][0]['attributes']['SPEED_LIMITS_FCN'][0]
        speed_limit = int(data['TO_REF_SPEED_LIMIT'])
        if(speed_limit==0):
            speed_limit = int(data['FROM_REF_SPEED_LIMIT'])
            
        if(speed_limit):
            print(f"Speed limit: {speed_limit} km/h")
            if(speed-speed_limit>=5): # if going 5 km/h over
                return speed_limit, True          
    return speed_limit, False
    

def get_speed_info(cur_lat, cur_long, file_path, curr_time):
    prev_lat, prev_long = 0.0, 0.0
    boolean = False
    curr_time = curr_time.split(':')
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if lines:
            line = lines[-1].strip()
            prev_lat, prev_long = line.strip().split(', ')[0], line.strip().split(', ')[1]
            prev_time = line.split(', ')[2].split('Time: ')[1].split(':')
            time_difference = get_time_difference(prev_time, curr_time)
            
            if(time_difference <= 60): # prev location = recorded less than a minute ago
                # reverse geocoding api
                load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
                api_key = os.getenv("HERE_API_KEY")
                distance = get_driving_distance(api_key, str(cur_lat)+","+str(cur_long), str(prev_lat)+","+str(prev_long))
                if(distance<0): distance=0
                speed = round(distance/time_difference*3.6) # m/s --> km/h
                print('Speed:', speed, 'km/h')
                speed_limit, boolean = detect_speeding(str(cur_lat), str(cur_long), api_key, speed)
                return round(speed, 2), speed_limit, boolean 
    return 0.0, 0.0, boolean


def get_coordinates(device, map):
    location = device.location()
    if location:
        current_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        latitude, longitude = location['latitude'], location['longitude']
        print('Coordinates: ' + str(latitude) + ', ' + str(longitude)) #TEST
        update_map(map, latitude, longitude)
        return latitude, longitude, current_time
    return None, None, current_time


def turn_angle(v1, v2):
    angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
    angle_deg = np.degrees(angle)
    if angle_deg < 0: angle_deg += 360
    return angle_deg


def detect_turn_direction(latitudes, longitudes, curr_lat, curr_long):
    # Linear regression for line of best fit
    latitudes_reshaped = latitudes.reshape(-1, 1)
    reg = LinearRegression()
    reg.fit(latitudes_reshaped, longitudes)

    first_point_in_fit = [latitudes[0], reg.predict(latitudes_reshaped)[0]]
    last_point_in_fit = [latitudes[-1], reg.predict(latitudes_reshaped)[-1]]
    direction_segment1 = np.array(last_point_in_fit) - np.array(first_point_in_fit)
    direction_segment2 = np.array([curr_lat, curr_long]) - np.array(last_point_in_fit)

    angle = turn_angle(direction_segment1, direction_segment2)
    radians = np.radians(angle) % (2*pi)
    RANGE = pi/3
    if (pi/2 - RANGE <= radians <= pi/2 + RANGE): return "right"
    elif (3*pi/2 - RANGE <= radians <= 3*pi/2 + RANGE): return "left"
    else: return "straight"


def detect_turn(curr_lat, curr_long, file_path, database_path, curr_street, api_key, filename):
    prev_longs = np.array([]) # x-val   
    prev_lats = np.array([]) # y-val
    file = open(file_path, 'r')
    paths = file.readlines()
    file.close()
    index = -2
    right_turn_restriction = False

    while(abs(index)<=len(paths)):
        path = paths[index]
        prev_lat, prev_long = path.split(', ')[0], path.split(', ')[1]

        if(path.split(', ')[3].split('Street: ')[1].replace("\n", "")!=curr_street or get_driving_distance(api_key, str(curr_lat)+','+str(curr_long), str(prev_lat)+','+str(prev_long))>150):
            break # different street or too far away
        if(prev_lat!=paths[index+1].split(', ')[0] and prev_long!=paths[index+1].split(', ')[1]):
            prev_longs = np.append(np.array([ float(prev_long.strip())]), prev_longs)
            prev_lats = np.append(np.array([ float(prev_lat.strip())]), prev_lats)
        
        database_turn_restriction = get_database_value(database_path, filename, index, "turn_restriction")
        if(right_turn_restriction==False and database_turn_restriction):
            right_turn_restriction = database_turn_restriction
         
        index-=1
    direction = detect_turn_direction(prev_lats, prev_longs, curr_lat, curr_long)
    print("Turn:", direction, right_turn_restriction)
    return direction, right_turn_restriction


def main(filename):
    load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
    API_KEY = os.getenv("HERE_API_KEY")
    file_path = "/Users/pearlnatalia/Desktop/car/geolocation/path.txt"
    database_path =  "/Users/pearlnatalia/Desktop/car/data/" + filename + ".db"
    prev_street, curr_street, turn = "", "", ""
    intersection = False
    prev_lat, prev_long = None, None
    
    # for coordinates
    device = get_device()
    INTERVAL = 3
    map = folium.Map(
        location=[device.location()['latitude'], 
        device.location()['longitude']], 
        zoom_start=12
    )

    try:
        while True:
            if(curr_street):
                prev_street = curr_street

            latitude, longitude, current_time = get_coordinates(device, map)
            if(get_street_name(API_KEY, latitude, longitude) is None):
                continue
            
            speed, speed_limit, boolean = get_speed_info(latitude, longitude, file_path, current_time)
            red_light_camera, curr_street = get_red_light_camera(latitude, longitude)
        
            with open(file_path, 'a') as file:
                file.write(f"{latitude}, {longitude}, Time: {current_time}, Street: {curr_street}\n")

            # stop checking for turn after 200m from intersection
            if(intersection and prev_lat, prev_long and get_driving_distance(API_KEY, \
                str(latitude)+","+str(longitude), str(prev_lat)+","+str(prev_long))>200): 
                intersection = False

            # detecting intersection
            if(intersection==False and prev_street and prev_street!=curr_street):
                intersection = True
                prev_lat, prev_long = latitude, longitude
            
            if(intersection): #detecting turn
                turn, restriction = detect_turn(latitude, longitude, file_path, database_path, curr_street, API_KEY)
                if(restriction!=False and turn == 'right'):
                    print('Right Turn Violation')

            #updating database:
            # update_database(database_path, "coordinates", latitude+","+longitude, record_id, filename)
            # update_database(database_path, "street", curr_street, record_id, filename)
            # update_database(database_path, "speed", speed, record_id, filename)
            # update_database(database_path, "speed_limit", speed_limit, record_id, filename)
            # update_database(database_path, "is_speeding", boolean, record_id, filename)
            # if(red_light_camera is None):
            #     red_light_camera = "None"
            # update_database(database_path, "red_light_camera", red_light_camera, record_id, filename)

            print('\n')
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Stopping updates.")
    

if __name__ == "__main__":
    filename = "traffic_video.db"
    main(filename)