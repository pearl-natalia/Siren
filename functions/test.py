import numpy as np, requests
from math import atan2, pi
from location import get_driving_distance, format_address

def detect_turn_direction(latitudes, longitudes, curr_lat, curr_long):
    print(latitudes)
    latitudes = np.array([-79.56662031, -79.56673638, -79.56676419, -79.56695097, -79.56745079])
    print(latitudes)
    print(longitudes)
    longitudes = np.array([43.84366746, 43.8436075, 43.84360026, 43.84356218, 43.84346069])
    print(longitudes)

    slope_best_fit = np.polyfit(longitudes, latitudes, 1)[0]
    angle_best_fit = atan2(1, slope_best_fit)
    
    dx = curr_long - longitudes[-1]
    dy = curr_lat - latitudes[-1]
    angle_direction = atan2(dy, dx)
    radians = angle_best_fit - angle_direction
    if (radians < 0): radians += 2*pi # clockwise angle
    if (radians > pi): radians = 2*pi - radians
 
    RANGE = pi/3 
    if (pi/4 - RANGE <= radians <= pi/4 + RANGE): return "right"
    elif (3*pi/4 - RANGE <= radians <= 3*pi/4 + RANGE): return "left"
    else: return "straight"


def detect_turn(curr_lat, curr_long, file_path, curr_street, api_key):
    prev_longs = np.array([]) # x-val   
    prev_lats = np.array([]) # y-val
    file = open(file_path, 'r')
    paths = file.readlines()
    file.close()
    index = -2

    while(abs(index)<=len(paths)):
        path = paths[index]
        prev_lat, prev_long = path.split(', ')[0], path.split(', ')[1]

        if(path.split(', ')[3].split('Street: ')[1].replace("\n", "")!=curr_street or get_driving_distance(api_key, str(curr_lat)+','+str(curr_long), str(prev_lat)+','+str(prev_long))>150):
            break # different street or too far away
        if(prev_lat!=paths[index+1].split(', ')[0] and prev_long!=paths[index+1].split(', ')[1]):
            prev_longs = np.append(prev_longs, float(prev_long.strip()))
            prev_lats = np.append(prev_lats, float(prev_lat.strip()))
        index-=1
    return detect_turn_direction(prev_lats, prev_longs, curr_lat, curr_long)

def get_street_name(api_key, lat, long):
    url = f"https://revgeocode.search.hereapi.com/v1/revgeocode?at={lat},{long}&apiKey={api_key}"

    response = requests.get(url)
    if(response.status_code == 200):
        data = response.json()
        if('street' in data['items'][0]['address']):
            return format_address(data['items'][0]['address']['street'])
    return None

def main():
    API_KEY='rJ-Wj137nD7vwny820vqxVYksY10k2_VUETBIwjjHEU'
    FILE_PATH = '/Users/pearlnatalia/Desktop/car/functions/test.txt'
    lat, long = 43.843875, -79.566703
    print('Turn:', detect_turn(43.843972064427, -79.56667251243482, FILE_PATH, 'Major MacKenzie Drive', API_KEY))

if __name__ == "__main__":
    main()
