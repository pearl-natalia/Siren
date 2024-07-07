import numpy as np, requests
from math import atan2, pi
from location import get_driving_distance, format_address
from sklearn.linear_model import LinearRegression
from inference_sdk import InferenceHTTPClient
import cv2
import argparse, os, supervision as sv, numpy as np, \
    cv2, tempfile, time, tempfile
from roboflow import Roboflow
from supervision import Detections
from dotenv import load_dotenv
from database import create_database, insert_in_database, update_database
from inference_sdk import InferenceHTTPClient

from detect import saturate_image


import supervision as sv

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
    if (pi/2 - RANGE <= radians <= pi/2 + RANGE): return "right", radians
    elif (3*pi/2 - RANGE <= radians <= 3*pi/2 + RANGE): return "left", radians
    else: return "straight", radians

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
            prev_longs = np.append(np.array([ float(prev_long.strip())]), prev_longs)
            prev_lats = np.append(np.array([ float(prev_lat.strip())]), prev_lats)
        index-=1
    print(prev_lats)
    return detect_turn_direction(prev_lats, prev_longs, curr_lat, curr_long)

def get_street_name(api_key, lat, long):
    url = f"https://revgeocode.search.hereapi.com/v1/revgeocode?at={lat},{long}&apiKey={api_key}"

    response = requests.get(url)
    if(response.status_code == 200):
        data = response.json()
        if('street' in data['items'][0]['address']):
            return format_address(data['items'][0]['address']['street'])
    return None


def detect_no_right_turn_sign(API_KEY, frame_path):
    CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
    )
    result = CLIENT.infer(frame_path, model_id="right-turn-sign-detection/1", confidence = 0.8)

    print(result)
    return result


def detect_turn_sign(API_KEY, frame_path, max_height, min_height):
    API_KEY = Roboflow(os.getenv("API_KEY"))
    turn_project = API_KEY.workspace().project("right-turn-sign-detection")
    turn_model = turn_project.version(1).model
    image = saturate_image(cv2.imread(frame_path))

    result = turn_model.predict(frame_path, confidence=30, overlap=2).json()
    labels = [item["class"] for item in result["predictions"]]
    detections = sv.Detections.from_roboflow(result)
   

    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()
    annotated_frame = box_annotator.annotate(
        scene=image, detections=detections)
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=detections, labels=labels)
    if(detections['xyxy'] is not None): stop_sign = 1
    print(detections)

    right_turn_restriction = False

    for detection in detections.xyxy:
        if(detection[1]>=max_height and detection[3]<=min_height):
            right_turn_restriction = True
            print(detection)
            break
    
    print('Turn restictions:', right_turn_restriction)
    cv2.imshow('Annotated Image', annotated_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    API_KEY='hFw578qvMHkY4axNMAyC'
    frame = '/Users/pearlnatalia/Desktop/car/output_frames/turn.png'
    detect_turn_sign(API_KEY, frame, 66, 240)
    
    # print('Turn:', detect_turn(43.843972064427, -79.56667251243482, FILE_PATH, 'Major MacKenzie Drive', API_KEY))

if __name__ == "__main__":
    main()
