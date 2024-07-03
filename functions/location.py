import os, time, folium, csv, requests, math
from dotenv import load_dotenv
from pyicloud import PyiCloudService
from detect import update_database
import numpy as np
import matplotlib.pyplot as plt

def load_api():
    # Load environment variables from .env file
    load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
    iCloud_user = os.getenv("iCloud_user")
    iCloud_pass = os.getenv("iCloud_pass")

    # Initialize iCloud api
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

def get_rows(long):
    long = int(long * 10)/10 #floor function to 1 decimal place
    if(long == -79.1):
        return 2, 8
    elif (long == -79.2):
        return 7, 48
    elif (long == -79.3):
        return 47, 101
    elif (long == -79.4):
        return 100, 158
    elif (long == -79.5):
        return 157, 206
    elif (long == -79.6):
        return 205, 227
    elif (long == -79.7):
        return 226, 251
    elif (long == -79.8):
        return 250, 267
    elif (long <= -80.1 and long >= -80.3):
        return 266, 272
    else:
        return 0, 0

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
        return data['items'][0]['address']['street']
    return None

def get_driving_distance(api_key, red_coordinate, current_coordinate):    
    base_url = "https://router.hereapi.com/v8/routes"
    params = {
        "transportMode": "car",
        "origin": current_coordinate,
        "destination": red_coordinate,
        "return": "summary",
        "apiKey": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['routes'][0]['sections'][0]['summary']['length']
    return -1

def format_address(current_street):
    if(current_street is None): return None
    replacements = {
        " N": " North", " E": " East", " S": " South", " W": " West",
        " Rd": " Road", " St": " Street", " Av": " Avenue",
        " Blvd": " Boulevard", " Dr": " Drive"
    }
    # spaces if in middle of sentence
    replacements_with_spaces = {f" {k} ": f" {v} " for k, v in replacements.items()}
    for abbreviation, full in replacements_with_spaces.items():
        current_street = current_street.replace(abbreviation, full)
    # no spaces if at end of sentence
    for abbreviation, full in replacements.items():
        if current_street.endswith(abbreviation):
            current_street = current_street[:-len(abbreviation)] + full
    return current_street


def get_red_light_camera(lat, long):  
    start, end = get_rows(long)
    if(start==0 and end==0): # not in dataset
        return None
    
    red_intersection, red_region = "", ""
    red_lat, red_long = 0.0, 0.0
    distance = -1
    intersection, region = "", ""

    # reverse geocoding api
    load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
    API_KEY = os.getenv("HERE_API_KEY")
   
    current_street = format_address(get_street_name(API_KEY, lat, long))
    if(current_street is None): return None
    
    for row in range(start-1, end+1):
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
        return None

def get_time_difference(prev_time, curr_time):
    prev_h, prev_m, prev_s = map(int, prev_time)
    curr_h, curr_m, curr_s = map(int, curr_time)
    
    prev_total_seconds = prev_h * 3600 + prev_m * 60 + prev_s
    curr_total_seconds = curr_h * 3600 + curr_m * 60 + 4
    
    return abs(prev_total_seconds - curr_total_seconds)



def get_speed(cur_lat, cur_long, file_path, curr_time):
    prev_lat, prev_long = 0.0, 0.0
    boolean = False
    curr_time = curr_time.split(':')
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if lines:
            line = lines[-1].strip()
            prev_lat, prev_long = line.strip().split(', ')[0], line.strip().split(', ')[1]
            prev_time = line.split("Time: ")[-1].strip().split(':')
            time_difference = get_time_difference(prev_time, curr_time)
            
            if(time_difference <= 60): # prev location = recorded less than a minute ago
                # reverse geocoding api
                load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
                api_key = os.getenv("HERE_API_KEY")

                distance = get_driving_distance(api_key, str(cur_lat)+","+str(cur_long), str(prev_lat)+","+str(prev_long))
                if(distance<0): distance=0
                speed = round(distance/time_difference*3.6) # m/s --> km/h
                print(speed)
                speed_limit, boolean = is_speeding(str(cur_lat), str(cur_long), api_key, speed)
                return round(speed, 2), speed_limit, boolean 
    return 0.0, 0.0, boolean

def is_speeding(lat, long, api_key, speed):
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
        data = response.json()
        speed_limit = int(data['response']['route'][0]['leg'][0]['link'][0]['attributes']['SPEED_LIMITS_FCN'][0]['FROM_REF_SPEED_LIMIT'])
        if(speed_limit):
            print(f"Speed limit: {speed_limit} km/h")
            if(speed-speed_limit>=5): # if going 5 km/h over
                return speed_limit, True          
    return speed_limit, False

def acute_angle_between_lines(slope1, slope2):
    if slope1 is None or slope2 is None:
        return 90.0 
    
    # Calculate the angle between two lines defined by their slopes
    angle_rad = abs(math.atan(abs((slope2 - slope1) / (1 + slope1 * slope2))))
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    return angle_deg
        
def get_coordinates(filename, record_id):
    try:
        # Updating map
        file_path = "/Users/pearlnatalia/Desktop/car/geolocation/path.txt"
        database_path =  "/Users/pearlnatalia/Desktop/car/data/" + filename + ".db"
        INTERVAL = 3
        device = get_device()
        map = folium.Map(
            location=[device.location()['latitude'], 
            device.location()['longitude']], 
            zoom_start=12
        )

        prev_street, current_street = "", ""
        trajectory_lat = []
        trajectory_long = []

        while True:
            location = device.location()
            if location:

                if(current_street):
                    prev_street = current_street

                current_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
                latitude = location['latitude']
                longitude = location['longitude']
                speed, speed_limit, boolean = get_speed(latitude, longitude, file_path, current_time)
                red_light_camera, current_street = get_red_light_camera(latitude, longitude)

                if((prev_street and prev_street==current_street) or (prev_street is None)):
                    trajectory_lat.append(latitude)
                    trajectory_long.append(longitude)
                else:
                    #line of best fit
                    trajectory_lat = np.array(trajectory_lat)
                    trajectory_long = np.array(trajectory_long)
                    slope_best_fit, intercept = np.polyfit(trajectory_long, trajectory_lat, 1)
                    fit_latitudes = slope_best_fit * trajectory_long + intercept
                    plt.scatter(trajectory_long, trajectory_lat, color='blue', label='Original data')
                    plt.plot(trajectory_lat, fit_latitudes, color='red', label='Line of best fit')
                    plt.show()


                    #equation between coor on prev street and coor on current street
                    if trajectory_long[-1]-longitude != 0:
                        m = (trajectory_lat[-1]-latitude) / (trajectory_long[-1]-longitude)
                    else:
                        m = None #vertical lines

                    
                    
                    




                update_database(database_path, "coordinates", latitude+","+longitude, record_id, filename)
                update_database(database_path, "street", current_street, record_id, filename)
                update_database(database_path, "speed", speed, record_id, filename)
                update_database(database_path, "speed_limit", speed_limit, record_id, filename)
                update_database(database_path, "is_speeding", boolean, record_id, filename)
                if(red_light_camera is None):
                    red_light_camera = "None"
                update_database(database_path, "red_light_camera", red_light_camera, record_id, filename)

                
                with open(file_path, 'a') as file:
                    
                    file.write(f"{latitude}, {longitude}, Time: {current_time}\n")
                    update_map(map, latitude, longitude)
                    
            else:
                with open(file_path, 'a') as file:
                    file.write("Can't fetch coordinates.\n")

            # Update location every INTERVAL seconds
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Stopping updates.")

def main():
    filename = "traffic_video.db"
    with open('/Users/pearlnatalia/desktop/car/geolocation/path.txt', 'r') as file:
        lines = file.readlines()
    record_id = len(lines)
    get_coordinates(filename, record_id)
    

if __name__ == "__main__":
    # test it out between diving among interval or timestamp (whichever is more accurate)
    # get_speed(43.845020794421096, -79.56710257678063, '/Users/pearlnatalia/desktop/car/geolocation/path.txt', '19:55:00')
    main()