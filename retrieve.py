import cv2
import numpy as np
import os
import time

# Function to generate filename based on current date and time
def generate_filename():
    now = time.localtime()
    return time.strftime("%m-%d-%Y-%H-%M-%S", now) + '.avi'

FILE_OUTPUT_DIR = 'output_videos'
VIDEO_INTERVAL = 60
os.makedirs(FILE_OUTPUT_DIR, exist_ok=True)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Unable to open video capture.")
    exit()
currentFrame = 0

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)   
out = None
start_time = time.time()

while(cap.isOpened()):
    ret, frame = cap.read()

    if ret == True:
        frame = cv2.flip(frame, 1)
        cv2.imshow('frame', frame)

        current_time = time.time()
        if current_time - start_time >= VIDEO_INTERVAL or out is None:
            if out is not None:
                out.release()  # Release the previous video writer
            filename = generate_filename()
            filepath = os.path.join(FILE_OUTPUT_DIR, filename)
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPEG codec
            out = cv2.VideoWriter(filepath, fourcc, 20.0, (int(width), int(height)))
            if not out.isOpened():
                print("Error: Unable to open video writer.")
                break
            start_time = current_time

        out.write(frame)

    else: break
    if cv2.waitKey(1) & 0xFF == ord('q'): break
    currentFrame += 1

cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
