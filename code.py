# data_exporter.py
# This file turns simulated GPS points into a real GPX file
# Author: Solomon Daniel

import xml.etree.ElementTree as ET   # This helps us create XML (the language GPX uses)
from datetime import datetime       # To add the current time
import os                           # To get the full file path


class DataExporter:
    """
    This class has one main job:
    Take a list of GPS points and save them as a .gpx file
    """

    def __init__(self):
        # This runs when we create the object
        self.creator = "GeoSpoof Engine"   # Name that appears inside the GPX file

    def export_to_gpx(self, points, filename="simulated_track.gpx"):
        """
        Main function you will call.

        points   = list of dictionaries. Each dictionary must have "lat" and "lon"
                   Example: [{"lat": 6.52, "lon": 3.37}, {"lat": 6.53, "lon": 3.38}]
        filename = the name of the file you want to create
        """

        # ---------- Safety check ----------
        if not points:
            print("Error: No points given. Cannot create file.")
            return

        # ---------- 1. Create the root of the GPX file ----------
        # Every GPX file starts with a <gpx> tag
        root = ET.Element("gpx")
        root.set("version", "1.1")
        root.set("creator", self.creator)
        root.set("xmlns", "http://www.topografix.com/GPX/1/1")

        # ---------- 2. Add a simple name for the track ----------
        metadata = ET.SubElement(root, "metadata")
        name = ET.SubElement(metadata, "name")
        name.text = "GeoSpoof Simulated Track"

        # ---------- 3. Create the track structure ----------
        # GPX structure looks like this:
        # <gpx>
        #   <trk>
        #     <trkseg>
        #       <trkpt ...>
        #       <trkpt ...>
        track = ET.SubElement(root, "trk")
        track_name = ET.SubElement(track, "name")
        track_name.text = "Simulated Journey"

        segment = ET.SubElement(track, "trkseg")   # One segment that holds all points

        # ---------- 4. Add every GPS point ----------
        for point in points:
            # Create one track point
            trkpt = ET.SubElement(segment, "trkpt")
            trkpt.set("lat", str(point["lat"]))   # latitude
            trkpt.set("lon", str(point["lon"]))   # longitude

            # Optional: add elevation if it exists
            if "ele" in point:
                elevation = ET.SubElement(trkpt, "ele")
                elevation.text = str(point["ele"])

            # Optional: add time if it exists
            if "time" in point:
                time_tag = ET.SubElement(trkpt, "time")
                time_tag.text = str(point["time"])

        # ---------- 5. Save the file ----------
        # Turn the tree into an actual XML file
        tree = ET.ElementTree(root)

        # Make the XML look neat (nice indentation)
        try:
            ET.indent(tree, space="  ")
        except:
            pass   # Older Python versions don't have this, so we ignore the error

        # Write the file to disk
        tree.write(filename, encoding="utf-8", xml_declaration=True)

        # Tell the user where the file was saved
        full_path = os.path.abspath(filename)
        print("Success! GPX file saved at:")
        print(full_path)

        return full_path


# ============================================================
# TEST CODE - You can run this file directly to see it work
# ============================================================
if __name__ == "__main__":

    # Example GPS points (pretend these came from the simulation)
    sample_points = [
        {"lat": 6.5244, "lon": 3.3792, "ele": 40},   # Lagos
        {"lat": 6.5250, "lon": 3.3800, "ele": 41},
        {"lat": 6.5258, "lon": 3.3815, "ele": 42},
        {"lat": 6.5265, "lon": 3.3830, "ele": 43},
    ]

    # Create the exporter and save the file
    exporter = DataExporter()
    exporter.export_to_gpx(sample_points, "my_first_track.gpx")

    print("\nOpen the file 'my_first_track.gpx' in Google Earth or any map app to see the track.")
