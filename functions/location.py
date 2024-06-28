import os, time, folium
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
                    file.write(f"{latitude}, {longitude}, Time: {current_time}\n")
                    update_map(map, latitude, longitude)
                    
            else:
                with open(file_path, 'a') as file:
                    file.write("Can't fetch coordinates.\n")

            # Update location every INTERVAL seconds
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Stopping updates.")