import folium
import folium.plugins
import webbrowser

import folium

# Read in the GPS coordinates from the txt file
with open('telemetry.txt', 'r') as file:
    lines = file.readlines()
    gps_coordinates = [line.split(", ")[:2] for line in lines]



# Parse the latitude and longitude coordinates
latitudes = []
longitudes = []
for coordinate in gps_coordinates:
    latitude, longitude = coordinate[0].strip().split(',')
    latitudes.append(float(latitude))
    longitudes.append(float(longitude))

# for i in range(0, len(gps_coordinates), 10):
#     coordinate = gps_coordinates[i]
#     latitude, longitude = coordinate[0].strip().split(',')
#     latitudes.append(float(latitude))
#     longitudes.append(float(longitude))

# Set the center of the map to the first coordinate in the list
map_center = [latitudes[0], longitudes[0]]

# Create a map object
m = folium.Map(location=map_center, zoom_start=25)

# Create a polyline object using the latitude and longitude coordinates
coordinates = list(zip(latitudes, longitudes))
# path = folium.PolyLine(locations=coordinates, weight=5, arrowstyle='-|>', color='blue')
path = folium.plugins.AntPath(locations=coordinates, weight=5, color='#FF0000', delay=1000, dash_array=[10, 100], reverse=True)


# Add the path to the map
path.add_to(m)

# Add a marker for the LOI coordinates, if available
with open('commands.txt', 'r') as file:
    for line in file:
        fields = line.strip().split(', ')
        if len(fields) == 6 and fields[2] == 'LOI':
            latitude, longitude = fields[3:5]
            folium.Marker(location=[float(latitude), float(longitude)], 
                          icon=folium.Icon(color='yellow', icon='star')).add_to(m)
            print("LOI")

# Save the map as an HTML file
m.save('map.html')

# Open the map in a web browser
webbrowser.open('map.html')


