import cv2

# Open the video file for reading
cap = cv2.VideoCapture('output.avi')

# Check if the video file was successfully opened
if not cap.isOpened():
    print("Error: Could not open video file")
    exit()

# Read and display each frame of the video
while True:
    ret, frame = cap.read()
    if ret:
        # Display the frame
        cv2.imshow('Video', frame)
        # Wait for a specific delay (in milliseconds)
        # Press 'q' to exit the video playback
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        # End of the video
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()