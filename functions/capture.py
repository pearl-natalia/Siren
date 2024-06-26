import cv2
import numpy as np
import os
import time
import sqlite3

# Generate filename based on current date and time
def generate_filename(start_time):
    return time.strftime("%m-%d-%Y-%H-%M-%S", start_time) + '.avi'

#creating a database
conn = sqlite3.connect('/Users/pearlnatalia/Desktop/car/video_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS video_data (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

def store_in_database(filename):
    cursor.execute('''
        INSERT INTO video_data (filename) VALUES (?)
    ''', (filename,))
    conn.commit()

FILE_OUTPUT_DIR = 'footage'
VIDEO_INTERVAL = 5
os.makedirs(FILE_OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(0) # 0 for iPhone, 1 for Mac webcam

if not cap.isOpened():
    print("Error: Unable to open video capture.")
    exit()

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)   
out = None
start_time = time.time()

while(cap.isOpened()):
    ret, frame = cap.read()

    if ret == True:
        cv2.imshow('frame', frame)

        current_time = time.time()
        if current_time - start_time >= VIDEO_INTERVAL or out is None:
            if out is not None:
                out.release()  
            start_time = time.time()  # Update start_time when starting a new recording
            filename = generate_filename(time.localtime(start_time))
            store_in_database(filename)
            filepath = os.path.join(FILE_OUTPUT_DIR, filename)
            fourcc = cv2.VideoWriter_fourcc(*'MJPG') 
            out = cv2.VideoWriter(filepath, fourcc, 20.0, (int(width), int(height)))
            if not out.isOpened():
                print("Error: Unable to open video writer.")
                break

        out.write(frame)

    else:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()