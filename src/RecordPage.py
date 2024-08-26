import cv2
import os
import time

def main():
    print('here')
    cap = cv2.VideoCapture(0)  # 0 for default camera
    if not cap.isOpened():
        print("Error: Unable to open video capture.")
        exit()

    # Ensure the directory exists
    output_dir = './footage'
    os.makedirs(output_dir, exist_ok=True)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Include a file extension in the filepath
    filepath = os.path.join(output_dir, "test_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, 20.0, (width, height))

    if not out.isOpened():
        print("Error: Unable to open video writer.")
        cap.release()
        exit()

    frame_path = output_dir
    frame_count = 1
    INTERVAL = 5
    start_time = time.time()

    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret:
            frame = cv2.flip(frame, 1)  # remove mirroring
            cv2.imshow('frame', frame)

            # Write frame to video file
            out.write(frame)

            # Save frame as PNG every INTERVAL seconds
            current_time = time.time()
            if current_time - start_time >= INTERVAL or frame_count == 1:
                cv2.imwrite(os.path.join(frame_path, f"{frame_count}.png"), frame)
                frame_count += 1
                start_time = current_time

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
