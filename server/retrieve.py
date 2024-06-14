import sys
import sqlite3
import os
import cv2
from datetime import datetime
          
def play_videos(filenames, directory):
    video_players = []  
    previous_end_time = None  
    
    try:
        for filename in filenames:
            filename = filename[0]
            print(filename)
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                cap = cv2.VideoCapture(filepath)
                if not cap.isOpened():
                    print(f"Error: Unable to open video '{filename}'")
                    continue
                
                start_time = 0  
                end_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  
                
                if previous_end_time is not None:
                    time_diff = start_time - previous_end_time
                    if time_diff > 6 or time_diff < 4:
                        print("new window")
                        cv2.destroyAllWindows()  
                
                video_players.append(cap)  
                previous_end_time = end_time  
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    cv2.imshow('Video Player', frame)
                    
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        break
                
                cap.release()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    
    finally:
        for cap in video_players:
            cap.release()
        cv2.destroyAllWindows()


def retrieve(date, time):
    # Filename (key for retrival)
    if(len(date)==0):
        print("Zero")
        date = datetime.today().strftime("%m-%d-%Y")
    FILE_NAME = f"{date}-{time.replace(':', '-')}-%.avi"
    DIRECTORY = '/Users/pearlnatalia/Desktop/car/output_videos'

    # Retrieivng data from database (all clips within that minute)
    conn = sqlite3.connect('/Users/pearlnatalia/Desktop/car/video_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM video_data WHERE filename LIKE ?', (FILE_NAME,))
    
    play_videos(cursor.fetchall(), DIRECTORY)
    conn.close()


# retrieving data from terminal
if len(sys.argv) >= 2:
    if len(sys.argv) == 2: # mm-dd-yyyy hh:mm
        date = "" 
        time = sys.argv[1]
    elif len(sys.argv) >= 3: # hh:mm
        date = sys.argv[1]
        time = sys.argv[2]        
    retrieve(date, time)