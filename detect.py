import argparse
import os
from roboflow import Roboflow
import supervision as sv
import numpy as np
import cv2
import tempfile
import piexif
import subprocess
import json
from datetime import datetime
import ffmpeg
import time



def extract_frames(filename):
    video_path = "/Users/pearlnatalia/Desktop/car/test_images/"
    frame_path = "/Users/pearlnatalia/Desktop/car/output_frames/"
    INTERVAL = 0.5  # interval in seconds

    cap = cv2.VideoCapture(video_path + filename + ".mp4")
    frame_num = 1
    start_time = time.time()
    next_frame_time = start_time + INTERVAL  # next time to capture a frame

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        # Check if it's time to save the next frame
        if current_time >= next_frame_time:
            output_path = frame_path + filename + "_frames"
            os.makedirs(output_path, exist_ok=True)
            frame_file_path = os.path.join(output_path, f"{frame_num}.JPEG")
            cv2.imwrite(frame_file_path, frame)

            # Marking timestamp
            elapsed_time = current_time - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            formatted_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

            exif_dict = {"Exif": {piexif.ExifIFD.DateTimeOriginal: formatted_time.encode('utf-8')}}
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, frame_file_path)
            
            # Accessing the DateTimeOriginal tag for verification
            exif_data = piexif.load(frame_file_path)
            if "Exif" in exif_data:
                exif_exif = exif_data["Exif"]
                if piexif.ExifIFD.DateTimeOriginal in exif_exif:
                    datetime_original = exif_exif[piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                    print("DateTimeOriginal:", datetime_original)

            # Update the next frame capture time
            next_frame_time += INTERVAL
            frame_num += 1

    cap.release()


def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("input_video_path", type=str)
    args = parser.parse_args()
    filename = args.input_video_path.rsplit('.', 1)[0]
    
    #Video --> frames
    extract_frames(filename)

    # Initialize Roboflow with the API key
    rf = Roboflow(api_key="hFw578qvMHkY4axNMAyC")
    project = rf.workspace().project("traffic-light-detection-h8cvg")
    model = project.version(2).model

    # Define the callback function for the slicer
    def callback(image: np.ndarray) -> sv.Detections:
        # Save the image temporarily
        with tempfile.NamedTemporaryFile(suffix=".JPEG") as f:
            cv2.imwrite(f.name, image)
            # Get predictions from the model
            result = model.predict(f.name, confidence=1, overlap=50).json()

        # Convert Roboflow result to Supervision Detections
        detections = sv.Detections.from_roboflow(result)
        return detections

    def get_video_creation_time(video_path):
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path], capture_output=True)
        if result.returncode == 0:
            metadata = json.loads(result.stdout.decode('utf-8'))
            if 'format' in metadata and 'tags' in metadata['format'] and 'creation_time' in metadata['format']['tags']:
                creation_time = metadata['format']['tags']['creation_time']
                return creation_time
            else:
                print("Creation time not found in metadata.")
        else:
            print("Error running ffprobe:", result.stderr.decode('utf-8'))

        return None

    video_creation_time = get_video_creation_time("/Users/pearlnatalia/Desktop/car/test_images" + filename + ".mp4")
   
    input_path = "/Users/pearlnatalia/Desktop/car/output_frames/"+filename+"_frames/"
    for frame in os.listdir(input_path):
        if(frame==".DS_Store"):
            continue
        image = cv2.imread(os.path.join(input_path, input_path+frame))

        # Read the input image
        if image is None:
            raise ValueError("Image not found or unable to load.", input_path+frame)

        # Initialize the slicer
        slicer = sv.InferenceSlicer(callback=callback)

        # Get detections from the slicer
        detections = slicer(image=image)

        # Define the classes as per the Roboflow model
        classes = ["green", "yellow", "red"]

        # Count the number of detections
        prediction_num = len(detections.xyxy)

        # Initialize the box annotator
        box_annotator = sv.BoxAnnotator()

        # Annotate the frame with detection results
        annotated_frame = box_annotator.annotate(
            scene=image.copy(),
            detections=detections,
            labels=[classes[detections.class_id[i]] for i in range(prediction_num)],
        )

        # adding annotations to video        
        exif_data = piexif.load(input_path+"file")
        if "Exif" in exif_data:
                exif_exif = exif_data["Exif"]
                if piexif.ExifIFD.DateTimeOriginal in exif_exif:
                    date_time = exif_exif[piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        
                    


                    
        # Print detections
        print(detections)
        print(frame)

        output_path = input_path+"/"+frame
        cv2.imwrite(output_path, annotated_frame)


if __name__ == "__main__":
    main()
