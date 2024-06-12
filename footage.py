import cv2
import sqlite3
import time

# Connect to SQLite database
conn = sqlite3.connect('video_metadata.db')
c = conn.cursor()

# Create table to store video metadata
c.execute('''CREATE TABLE IF NOT EXISTS video_metadata
             (timestamp REAL)''')

# Function to capture video
def capture_video():
    # Open camera
    cap = cv2.VideoCapture(0)
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    
    start_time = time.time()
    
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if ret:
            # Write the frame
            out.write(frame)
            
            # Display the resulting frame
            cv2.imshow('frame', frame)
            
            # Check for termination
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    
    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Store metadata in database
    c.execute("INSERT INTO video_metadata (timestamp) VALUES (?)", (start_time,))
    conn.commit()
    
    print("Video duration:", duration)
    
    # Read the recorded video and play it back
    playback_cap = cv2.VideoCapture('output.avi')
    while playback_cap.isOpened():
        ret, frame = playback_cap.read()
        if ret:
            cv2.imshow('Playback', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    playback_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_video()
    conn.close()
