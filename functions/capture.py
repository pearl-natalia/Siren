import cv2
import numpy as np
import os
import time
import sqlite3
from location import INTERVAL

# Generate filename based on current date and time
def generate_filename(start_time):
    return str(time.strftime("%m-%d-%Y-%H-%M-%S", start_time)) + '.mp4'

start_time = time.time()
filename = generate_filename(time.localtime(start_time)).replace('-', '_')
tablename = filename.split('.mp4')[0]

#creating a database
conn = sqlite3.connect('../data/'+tablename+'.db')
cursor = conn.cursor()
cursor.execute(f''' 
    CREATE TABLE IF NOT EXISTS "{tablename}" (
    id INTEGER PRIMARY KEY,
    tablename TEXT,
    
    video_timestamp TEXT,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    coordinates TEXT,
    street TEXT,
    
    stop_sign BOOLEAN DEFAULT 0,
    ran_stop_sign BOOLEAN DEFAULT 0,
    
    traffic_colours TEXT,
    red_light_camera TEXT,
    ran_red_light BOOLEAN DEFAULT 0,
    
    speed DEFAULT 0,
    speed_limit DEFAULT 0,
    is_speeding BOOLEAN DEFAULT 0,

    turn BOOLEAN DEFAULT 0,
    turn_restriction BOOLEAN DEFAULT 0,

    acceleration DEFAULT 0,
    crash BOOLEAN DEFAULT 0,

    fines TEXT DEFAULT 'none'

    )''')
conn.commit()


def store_in_database(tablename):
    cursor.execute(f'''
        INSERT INTO "{tablename}" (tablename) VALUES (?)
    ''', (tablename,))
    conn.commit()



cap = cv2.VideoCapture(0) # 0 for iPhone, 1 for Mac webcam

if not cap.isOpened():
    print("Error: Unable to open video capture.")
    exit()


os.makedirs('../footage/', exist_ok=True)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)   
out = None


while(cap.isOpened()):
    ret, frame = cap.read()

    if ret == True:
        cv2.imshow('frame', frame)

        current_time = time.time()
        if current_time - start_time >= INTERVAL or out is None:
            if out is not None:
                out.release()  
            start_time = time.time()  # Update start_time when starting a new recording
            

            store_in_database(tablename)
            filepath = os.path.join('../footage', filename)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
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