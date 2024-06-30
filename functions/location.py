import os, time, folium, csv, requests
from dotenv import load_dotenv
from pyicloud import PyiCloudService

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
        return intersection + ", " + region
    else:
        print("No red light cameras near", current_street)
        return None


def get_coordinates():
    try:
        # Updating map
        file_path = "/Users/pearlnatalia/Desktop/car/geolocation/path.txt"
        INTERVAL = 1
        device = get_device()
        map = folium.Map(
            location=[device.location()['latitude'], 
            device.location()['longitude']], 
            zoom_start=12
        )

        while True:
            location = device.location()
            if location:
                current_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
                latitude = location['latitude']
                longitude = location['longitude']
                with open(file_path, 'a') as file:
                    return latitude, longitude #remove, only for test purposes
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
    lat, long = get_coordinates()
    get_red_light_camera(lat, long)

if __name__ == "__main__":
    main()