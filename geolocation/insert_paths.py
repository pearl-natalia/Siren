import pandas as pd
import folium

# Read the coordinates from path.txt
coordinates = []
m = folium.Map(
    location=[43.6,-79.3], 
    zoom_start=12
)

with open('geolocation/path.txt', 'r') as file:
    for line in file:
        # Split the line by ', ' to separate latitude, longitude, and timestamp
        parts = line.strip().split(', ')
        if len(parts) >= 2:
            lat = float(parts[0])
            long = float(parts[1])
            coordinates.append({'lat': lat, 'long': long})

# Add points to the map
for coord in coordinates:
    folium.Marker([coord['lat'], coord['long']]).add_to(m)

# Save the map to an HTML file
m.save('geolocation/map.html')
