import argparse, os, supervision as sv, numpy as np
import cv2, tempfile, time, sqlite3, tempfile
from roboflow import Roboflow
from supervision import Detections


def saturate_image(frame):
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    s = cv2.multiply(s, 1.5)
    s = np.clip(s, 0, 255).astype(np.uint8)
    hsv_image = cv2.merge([h, s, v])
    frame = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    return frame


def extract_frames(filename):
    video_path = "/Users/pearlnatalia/Desktop/car/footage/"
    frame_path = "/Users/pearlnatalia/Desktop/car/output_frames/"
    database_path = "/Users/pearlnatalia/Desktop/car/data/" + filename + ".db"

    INTERVAL = 0.3  # interval in seconds

    cap = cv2.VideoCapture(video_path + filename + ".mp4")
    frame_num = 1
    start_time = time.time()
    next_frame_time = start_time + INTERVAL  

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        if current_time >= next_frame_time:
            insert_in_database(database_path, "timestamp", current_time-start_time, filename)
            frame = saturate_image(frame)

            # saving image
            output_path = frame_path + filename + "_frames"
            os.makedirs(output_path, exist_ok=True)
            frame_file_path = os.path.join(output_path, f"{frame_num}.JPEG")
            cv2.imwrite(frame_file_path, frame)

            # Marking timestamp

            # elapsed_time = current_time - start_time
            # hours, rem = divmod(elapsed_time, 3600)
            # minutes, seconds = divmod(rem, 60)
            # formatted_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

            # exif_dict = {"Exif": {piexif.ExifIFD.DateTimeOriginal: formatted_time.encode('utf-8')}}
            # exif_bytes = piexif.dump(exif_dict)
            # piexif.insert(exif_bytes, frame_file_path)

            # Update the next frame capture time
            next_frame_time += INTERVAL
            frame_num += 1
    cap.release()


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

    detections.xyxy, detections.class_id = detect_bike_bus_lights(filtered_detections, filtered_classes) 
    if(detections.xyxy):
        detections.xyxy, detections.class_id = order_positions(detections.xyxy, detections.class_id)
    
    return detections
      

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

    for i in range(1, len(positions)):
        if(positions[i][1]<=positions[i-1][3]):
            filtered_positions.append(positions[i])
            filtered_classes.append(classes[i])
    
    return filtered_positions, filtered_classes


# sort lights from left to right
def order_positions(filtered_positions, filtered_classes):
    combined = list(zip(filtered_positions, filtered_classes))
    combined = sorted(combined, key=lambda x: x[0][0])
    filtered_positions, filtered_classes = zip(*combined)
    filtered_positions, filtered_classes = list(filtered_positions), list(filtered_classes)
    return filtered_positions, filtered_classes


def create_database(filename):
    conn = sqlite3.connect("/Users/pearlnatalia/Desktop/car/data/" + filename + ".db")
    cursor = conn.cursor()
    cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {filename} (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                coordinates TEXT,
                stop_signs BOOLEAN DEFAULT 0,
                traffic_colours TEXT
            )
        ''')
    conn.commit()
    conn.close()


def insert_in_database(path, field, value, table):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {table} ({field})
        VALUES (?)
    ''', (value,))
    conn.commit()
    conn.close()


def update_database(path, field, value, record_id, table):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE {table} 
        SET {field} = ?
        WHERE id = ?
    ''', (value, record_id))
    conn.commit()
    conn.close()
   

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_video_path", type=str)
    args = parser.parse_args()
    filename = args.input_video_path.rsplit('.', 1)[0]
    stop_sign = False
    frame_path = "/Users/pearlnatalia/Desktop/car/output_frames/"+filename+"_frames/"
    database_path = "/Users/pearlnatalia/Desktop/car/data/" + filename + ".db"

    # Video --> frames
    create_database(filename)
    extract_frames(filename)

    # API
    rf = Roboflow(api_key="hFw578qvMHkY4axNMAyC")
    traffic_project = rf.workspace().project("traffic-light-detection-h8cvg")
    traffic_model = traffic_project.version(2).model
    stop_project = rf.workspace().project("stop-sign-detection-1")
    stop_model = stop_project.version(1).model

    def traffic_callback(image: np.ndarray) -> sv.Detections:
        with tempfile.NamedTemporaryFile(suffix=".JPEG") as f:
            cv2.imwrite(f.name, image)
            result = traffic_model.predict(f.name, confidence=15, overlap=1).json()
        detections = Detections.from_inference(result)
        return detections
    
    for frame in os.listdir(frame_path):
        if(frame==".DS_Store"): continue
        output_path = frame_path+"/"+frame
        image = cv2.imread(os.path.join(frame_path, frame_path+frame))

        # stop sign
        result = stop_model.predict(frame_path+frame, confidence=40, overlap=1).json()
        labels = [item["class"] for item in result["predictions"]]
        detections = sv.Detections.from_roboflow(result)
        label_annotator = sv.LabelAnnotator()
        box_annotator = sv.BoxAnnotator()
        annotated_frame = box_annotator.annotate(
            scene=image, detections=detections)
        annotated_frame = label_annotator.annotate(
            scene=annotated_frame, detections=detections, labels=labels)
        if(detections['xyxy'] is not None): stop_sign = 1
        
        # traffic light present
        else:
            slicer = sv.InferenceSlicer(callback=traffic_callback)
            detections = filter_detections(slicer(image=image), frame_path+frame)
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
            update_database(database_path, "traffic_colours", lights, frame.rsplit('.', 1)[0], filename)
        
        update_database(database_path, "stop_signs", stop_sign, frame.rsplit('.', 1)[0], filename) 
        cv2.imwrite(output_path, annotated_frame)


if __name__ == "__main__":
    main()
