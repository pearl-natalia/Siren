# Siren

Siren is a smart dash cam that uses computer vision and geolocation data to monitor driving behavior, track route history, and detect road violations directly on your mobile device. It generates geospatial insights to alert drivers about speeding, red light cameras, and other violations, promoting safer driving habits. These analytics can contribute to more precise insurance assessments, potentially reducing premiums over time, and assist in determining fault in case of accidents.

<p align="center">
<img src="https://github.com/pearl-natalia/crash/assets/145855287/aefa20ef-6356-4344-b718-a9b3cf3c6a23" alt="Screenshot 2024-07-08 at 10 11 00 PM" width="30%">
</p>

### Traffic Light & Stop Sign Detection

The process begins with autonomously processing dashcam footage, segmenting it into frames every 3 seconds for efficient image analysis.
By finely tuning YOLOv8, traffic lights are detected in each frame while filtering out irrelevant signals like bus or bike lights using a custom algorithm. The closest traffic light, identified by its lowest y-position in the frame, serves as the reference point. To note, aligned traffic lights overlap in position. These detections are then ordered from highest to lowest to eliminate non-overlapping signals and focus on relevant traffic lights within designated areas. Using HSV (hue, saturation, value) analysis within these regions, the system determines the current state of each traffic light (green, amber, red).

<p align="center">
<img width="60%" alt="Screenshot 2024-07-08 at 10 22 01 PM" src="https://github.com/pearl-natalia/crash/assets/145855287/5777477c-3765-4afa-bd4c-d94e34c1cbce">
</p>

When a traffic light is detected, the frame is further processed using another CNN to identify 'no right turn' prohibition signs to track illegal right turns. If no traffic lights are detected, the system checks for stop signs instead. Once all detections are complete, the data is stored in a SQLite database along with real-time metrics and video timestamps for playback purposes.

<p align="center">
<img width="25%" alt="Screenshot 2024-07-08 at 10 25 54 PM" src="https://github.com/pearl-natalia/crash/assets/145855287/35ea0efb-ffa2-43ed-91ec-803c6560f32d">
</p>

### Geographical Data

Simultaneously, in a separate thread, geographical data is captured to analyze driving behavior and track the vehicle's route. Using iCloud, the application receives GPS location data from the iPhone.

<p align="center">
<img width="30%" alt="Screenshot 2024-07-08 at 10 28 56 PM" src="https://github.com/pearl-natalia/crash/assets/145855287/0770c5ba-dd0e-4814-81e9-6e8d680bf66d">
</p>

**Rolling Stop Signs**<br>
If a stop sign is identified, the vehicle's movement is tracked for up to 200 meters following the initial detection. To ensure precision, the interval for capturing GPS coordinates is reduced to every second. Utilizing these coordinates, the system verifies whether a complete stop is executed, based on consistency across at least two instances (with a 1-second interval between each). Utilizing these coordinates, the system verifies if the coordinates remain identical across at least two instances (with a 3-second interval between each) to identify a full stop.
<br><br>

**Speed**<br>
Dividing the distance traveled by several intervals (approximately every 12 seconds) provides an average speed estimate. The HERE Maps API is used to retrieve speed limits specific to the current location. This allows for real-time detection of speeding, triggering warnings when exceeding limits by 10 km/h and sending a special alert if exceeding by 40 km/h (potentially leading to vehicle impoundment). In 40 km/h zones, the system displays a speeding warning emphasizing the likelihood of being in a school or community zone, where fines and demerit points are typically higher.<br><br>

**Nearby Red Light Cameras**<br>
The geographic locations of all red light camera intersections in major regions such as York, Toronto, Peel, Halton, Ottawa, Hamilton, and Guelph are publicly accessible on city and regional websites across southern Ontario. Through reverse geocoding, the system determines the specific street a vehicle is on based on its coordinates. Integrated with driver routing data, it identifies if a vehicle is approaching any road connected to a red light camera intersection within 300m of a driving route.<br>
These warnings aim to prevent a $325 fine for running a red light caught by the camera and discourage speeding through yellow lights.
When the distance to the intersection begins to increase over two frames, indicating that the vehicle is moving away, the warning is removed. The use of a driver routing API ensures accurate calculations of driving distances between coordinates A and B, which is essential as geographical distance may not accurately reflect the distance driven.

<p align="center">
<img width="678" alt="Screenshot 2024-07-08 at 10 32 04 PM" src="https://github.com/pearl-natalia/crash/assets/145855287/cb880468-d3c4-4f8e-9d3c-7f8caa7c6e89">
</p>

**Turn Detections**<br>
Using reverse geocoding, the system monitors the driver's current street, comparing it with the previous frame to detect any street name changes indicating a potential turn. A linear regression model calculates the average initial heading before the turn, followed by creating a direction vector from the last coordinate on the previous road to the current one. By measuring the clockwise angle of this vector relative to the line of best fit, the system identifies whether a left turn (π/6 - 5π/6), a right turn (7π/6 - 11π/6), or a straight path has been taken.
<br>
Continuing angle checking up to 100 meters from the initial street change ensures accurate detection, even near intersections where street names may change abruptly, clarifying straight path versus turn detections.
<br>

<p align="center">
<img width="1417" alt="Screenshot 2024-07-08 at 10 35 44 PM" src="https://github.com/pearl-natalia/crash/assets/145855287/853b2dd7-0303-46dc-98c0-5f2eccaef8a4"](https://github.com/pearl-natalia/crash/assets/145855287/af708d81-c388-493c-8426-af4459558648">
</p>

**Traffic signal**<br>
The leftmost traffic light always indicates left turns, whether it's a designated left-turn light or a standard one. The rightmost light corresponds to right turns and straight paths. When a turn is detected and the last frame with a traffic light shows it as red, the system checks for a complete stop made before the turn (consistency of coordinates over two frames on the previous street). For left turns, it verifies that the leftmost traffic light was not red before the turn. Additionally, if the speed exceeds 5 km/h and the last frame showed a red light, the system flags that timestamp as a potential instance of running a red light.
