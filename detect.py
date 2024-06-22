import argparse
import os
from roboflow import Roboflow
import supervision as sv
import numpy as np
import cv2
import tempfile

def extract_frames(filename):
    
    video_path = "/Users/pearlnatalia/Desktop/car/test_images/"
    frame_path = "/Users/pearlnatalia/Desktop/car/output_frames/"
    INTERVAL = 0.5

    cap = cv2.VideoCapture(video_path + filename + ".mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap = cv2.VideoCapture(video_path+filename+".mp4")
    frame_count = 0
    frame_num = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % (INTERVAL * int(cap.get(cv2.CAP_PROP_FPS))) == 0:
            output_path = frame_path + filename+"_frames"
            os.makedirs(frame_path + filename+"_frames", exist_ok=True)
            cv2.imwrite(output_path + "/%d.png" % frame_num, frame)
            frame_num+=1
        frame_count += 1
    cap.release() 
    return fps

def frames_to_video(filename, fps):
    input_frame_folder = "/Users/pearlnatalia/Desktop/car/output_frames/" + filename + "_frames"
    output_video_path = "/Users/pearlnatalia/Desktop/car/output_videos/" + filename + ".mp4"
    frame_files = sorted([os.path.join(input_frame_folder, f) for f in os.listdir(input_frame_folder) if f.endswith('.png')])
    frame = cv2.imread(frame_files[0])
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs as well, e.g., 'XVID', 'MJPG', 'DIVX'
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        video_writer.write(frame)

    video_writer.release()


def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("input_video_path", type=str)
    args = parser.parse_args()
    filename = args.input_video_path.rsplit('.', 1)[0]
    
    #Video --> frames
    fps = extract_frames(filename)

    # Initialize Roboflow with the API key
    rf = Roboflow(api_key="hFw578qvMHkY4axNMAyC")
    project = rf.workspace().project("traffic-light-detection-h8cvg")
    model = project.version(2).model

    # Define the callback function for the slicer
    def callback(image: np.ndarray) -> sv.Detections:
        # Save the image temporarily
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            cv2.imwrite(f.name, image)
            # Get predictions from the model
            result = model.predict(f.name, confidence=1, overlap=50).json()

        # Convert Roboflow result to Supervision Detections
        detections = sv.Detections.from_roboflow(result)
        return detections


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

        # Print detections
        print(detections)

        output_path = input_path+"/"+frame
        cv2.imwrite(output_path, annotated_frame)

        frames_to_video(filename, fps)



    # # Display the annotated image (optional)
    # sv.plot_image(image=annotated_frame, size=(16, 16))

if __name__ == "__main__":
    main()
