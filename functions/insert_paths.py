import pandas as pd
import folium

# Read the coordinates from path.txt
coordinates = []
m = folium.Map(
    location=[43.6,-79.3], 
    zoom_start=12
)

long_prev = ""
lat_prev = ""

with open('path.txt', 'r') as file:
    for line in file:
        # Split the line by ', ' to separate latitude, longitude, and timestamp        
        parts = line.strip().split(', ')
        if len(parts) >= 2:
            lat = float(parts[0])
            long = float(parts[1])
            if(long_prev and lat_prev and long_prev==long and lat_prev==lat):
                continue

            coordinates.append({'lat': lat, 'long': long})
            long_prev = long
            lat_prev = lat

# Add points to the map
for coord in coordinates:
    folium.Marker([coord['lat'], coord['long']]).add_to(m)

# Save the map to an HTML file
m.save('map.html')
