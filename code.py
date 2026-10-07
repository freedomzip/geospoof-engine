# data_exporter.py
# This program takes GPS points and saves them as a GPX file
# Author: Solomon Daniel

import xml.etree.ElementTree as ET   # Tool that helps us create XML/GPX files
import os                           # Tool that helps us work with files


class DataExporter:
    """This class is responsible for creating and saving the GPX file"""

    def __init__(self):
        # This runs when we create the object
        self.creator = "GeoSpoof Engine"   # Name that will appear inside the GPX file

    def export_to_gpx(self, points, filename="simulated_track.gpx"):
        """
        This is the main function.
        It receives a list of GPS points and saves them into a GPX file.
        """

        # Check if there are any points
        if not points:
            print("No points to save.")
            return

        # Create the main container of the GPX file
        root = ET.Element("gpx", version="1.1", creator="GeoSpoof Engine")

        # Create a track (the journey)
        track = ET.SubElement(root, "trk")

        # Create a segment inside the track (where all points will be stored)
        segment = ET.SubElement(track, "trkseg")

        # Go through each GPS point one by one
        for point in points:
            # Create one track point
            trkpt = ET.SubElement(segment, "trkpt", 
                                  lat=str(point["lat"]), 
                                  lon=str(point["lon"]))

            # If the point has elevation, add it
            if "ele" in point:
                elevation = ET.SubElement(trkpt, "ele")
                elevation.text = str(point["ele"])

        # Turn everything into a full XML document
        tree = ET.ElementTree(root)

        # Save the file on the computer
        tree.write(filename, encoding="utf-8", xml_declaration=True)

        # Tell the user that the file was saved successfully
        print(f"File saved successfully: {filename}")

        return filename


# ==================== TEST SECTION ====================
# This part only runs when you run this file directly
if __name__ == "__main__":

    # Sample GPS points for testing
    sample_points = [
        {"lat": 6.5244, "lon": 3.3792, "ele": 40},
        {"lat": 6.5250, "lon": 3.3800, "ele": 41},
        {"lat": 6.5258, "lon": 3.3815, "ele": 42},
        {"lat": 6.5265, "lon": 3.3830, "ele": 43},
    ]

    # Create the exporter and save the file
    exporter = DataExporter()
    exporter.export_to_gpx(sample_points, "my_first_track.gpx")
