import supervision as sv, numpy as np, cv2, tempfile
from database import update_row_database
from supervision import Detections
from inference_sdk import InferenceHTTPClient

def filter_detections(detections, frame_path):
    mask = detections.xyxy[:, 0] != 0
    filtered_xyxy = detections.xyxy[mask]
    filtered_class_id = detections.class_id[mask]
    detections = sv.Detections(xyxy=filtered_xyxy, class_id=filtered_class_id)
    filtered_detections = []
    filtered_classes = []
    for i in range(len(detections.xyxy)):
        if(detect_colour(detections.xyxy[i], frame_path, detections.class_id[i])):
            filtered_detections.append(detections.xyxy[i])
            filtered_classes.append(detections.class_id[i])
    detections.xyxy = filtered_detections
    detections.class_id = filtered_classes

    if(len(detections.xyxy)==0):
        return None, None, None

    detections.xyxy, detections.class_id, max_height, min_height = detect_bike_bus_lights(filtered_detections, filtered_classes) 
    if(detections.xyxy):
        detections.xyxy, detections.class_id = order_positions(detections.xyxy, detections.class_id)
    
    return detections, max_height, min_height
      

def detect_colour(coordinates, frame_path, colour):
    x_min, y_min, x_max, y_max = coordinates
    image = cv2.imread(frame_path, cv2.IMREAD_COLOR)
    image = image[int(y_min):int(y_max), int(x_min):int(x_max)]
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if(colour==0):
        green_lower = np.array([30, 50, 50])
        green_upper = np.array([90, 255, 255])
        mask_green = cv2.inRange(hsv_image, green_lower, green_upper)
        green_present = np.any(mask_green)
        return green_present
    elif(colour==1):
        yellow_lower = np.array([15, 100, 100])
        yellow_upper = np.array([35, 255, 255])
        mask_yellow = cv2.inRange(hsv_image, yellow_lower, yellow_upper)
        yellow_present = np.any(mask_yellow)
        return yellow_present
    else:
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 100, 100])
        red_upper2 = np.array([180, 255, 255])
        mask_red1 = cv2.inRange(hsv_image, red_lower1, red_upper1)
        mask_red2 = cv2.inRange(hsv_image, red_lower2, red_upper2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        red_present = np.any(mask_red)
        return red_present 


def detect_bike_bus_lights(positions, classes):
    positions = sorted(positions, key=lambda sub_array: sub_array[3])
    filtered_positions = []
    filtered_classes = []
    if(positions):
        filtered_positions.append(positions[0])
        filtered_classes.append(classes[0])

    max_height = positions[0][1]
    for i in range(1, len(positions)):
        if(positions[i][1]<=positions[i-1][3]):
            filtered_positions.append(positions[i])
            filtered_classes.append(classes[i])
        if(positions[i][1]<max_height):
            max_height=positions[i][1]
    
    return filtered_positions, filtered_classes, max_height, positions[-1][1]


# sort lights from left to right
def order_positions(filtered_positions, filtered_classes):
    combined = list(zip(filtered_positions, filtered_classes))
    combined = sorted(combined, key=lambda x: x[0][0])
    filtered_positions, filtered_classes = zip(*combined)
    filtered_positions, filtered_classes = list(filtered_positions), list(filtered_classes)
    return filtered_positions, filtered_classes

def detect_no_right_turn_sign(API_KEY, frame):
    CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
    )
    CLIENT.infer(frame, model_id="right-turn-sign-detection/1")


def detect(current_time, number, stop_model, traffic_model, turn_model):
    stop_sign = False
    frame_path = "../output_frames/"+current_time+"/"+number+".png"

    def traffic_callback(image: np.ndarray) -> sv.Detections:
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            cv2.imwrite(f.name, image)
            result = traffic_model.predict(f.name, confidence=15, overlap=1).json()
        detections = Detections.from_inference(result)
        return detections
    
    image = cv2.imread(frame_path)

    # stop sign
    result = stop_model.predict(frame_path, confidence=40, overlap=1).json()
    if(len(result['predictions'])!=0 and 'stop-sign-vandalized' not in result['predictions'] \
        and 'stop-sign-fake' not in result['predictions'] ):
        labels = [item["class"] for item in result["predictions"]]
        detections = sv.Detections.from_roboflow(result)
        label_annotator = sv.LabelAnnotator()
        box_annotator = sv.BoxAnnotator()
        annotated_frame = box_annotator.annotate(
            scene=image, detections=detections)
        annotated_frame = label_annotator.annotate(
            scene=annotated_frame, detections=detections, labels=labels)
        stop_sign = 1
    # traffic light present
    else:
        slicer = sv.InferenceSlicer(callback=traffic_callback)
        if(slicer(image=image).xyxy.shape[0] == 0): #no detections
            return
        
        detections, max_height, min_height = filter_detections(slicer(image=image), frame_path)
        if(detections==None):
            return
        classes = ["green", "off", "red", "yellow"]
        prediction_num = len(detections.xyxy)
        box_annotator = sv.BoxAnnotator()
        annotated_frame = box_annotator.annotate(
            scene=image.copy(),
            detections=detections,
            labels=[classes[detections.class_id[i]] for i in range(prediction_num)])
        lights = ""
        for d in detections.class_id:
            lights = lights + str(d) + " "
        lights = lights.strip()

        # no right turn
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
        right_turn_restriction = False

        for detection in detections.xyxy:
            if(detection[1]>=max_height and detection[3]<=min_height):
                right_turn_restriction = True
                break

        update_row_database("turn_restriction", right_turn_restriction, number, current_time)
        update_row_database("traffic_colours", lights, number, current_time)
    
    update_row_database("stop_sign", stop_sign, number, current_time) 
    cv2.imwrite(frame_path, annotated_frame)