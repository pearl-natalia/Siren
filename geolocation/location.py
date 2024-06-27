import os, time, folium
from dotenv import load_dotenv
from pyicloud import PyiCloudService

# Load environment variables from .env file
load_dotenv(dotenv_path="/Users/pearlnatalia/Desktop/car/.env")
iCloud_user = os.getenv("iCloud_user")
iCloud_pass = os.getenv("iCloud_pass")

# Initialize iCloud api
api = PyiCloudService(iCloud_user, iCloud_pass)
file_path = "/Users/pearlnatalia/Desktop/car/geolocation/path.txt"

def get_device():
    devices = api.devices
    for device in devices:
        if device.get('deviceClass') == 'iPhone':
            return device

# Updating map
INTERVAL = 0.5
device = get_device()
map = folium.Map(
    location=[device.location()['latitude'], 
    device.location()['longitude']], 
    zoom_start=12
)
                               
def update_map(latitude, longitude):
    folium.Marker([latitude, longitude]).add_to(map)
    map.save('map.html')

try:
    while True:
        location = device.location()
        if location:
            current_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
            latitude = location['latitude']
            longitude = location['longitude']
            with open(file_path, 'a') as file:
                file.write(f"{latitude}, {longitude}, Time: {current_time}\n")
                update_map(latitude, longitude)
        else:
            with open(file_path, 'a') as file:
                file.write("Can't fetch coordinates.\n")

        # Update location every INTERVAL seconds
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Stopping updates.")