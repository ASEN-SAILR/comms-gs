import sys
import folium
import folium.plugins
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a layout
        layout = QVBoxLayout()
        self.create_map()
        # Create a QWebEngineView widget and set the HTML map as its content
        self.map_view = QWebEngineView()
        self.map_view.setHtml(open('map.html').read())

        # Add the map view to the layout
        layout.addWidget(self.map_view)

        # Set the layout for the widget
        self.setLayout(layout)

    def create_map(self):
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

        # Set the center of the map to the first coordinate in the list
        map_center = [latitudes[0], longitudes[0]]

        # Create a map object
        m = folium.Map(location=map_center, zoom_start=20)

        # Create a polyline object using the latitude and longitude coordinates
        coordinates = list(zip(latitudes, longitudes))
        path = folium.plugins.AntPath(locations=coordinates, weight=5, color='blue', delay=1000, dash_array=[10, 100], reverse=True)
        

        # Add the path to the map
        path.add_to(m)

        # Add a marker for the LOI coordinates, if available
        with open('commands.txt', 'r') as file:
            for line in file:
                fields = line.strip().split(', ')
                if len(fields) == 6 and fields[2] == 'LOI':
                    latitude, longitude = fields[3:5]
                    folium.Marker(location=[float(latitude), float(longitude)], 
                                icon=folium.Icon(color='red', icon='star')).add_to(m)

        # Save the map as an HTML file
        m.save('map.html')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MapWidget()
    widget.show()
    sys.exit(app.exec())
