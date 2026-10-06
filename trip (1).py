import json
import math


class TripError(Exception):
    pass


class Waypoint:
    def __init__(self, latitude, longitude, name=""):
        self.set_coordinates(latitude, longitude)
        self.name = name

    def set_coordinates(self, latitude, longitude):
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            raise TripError("Latitude and longitude must be numbers.")
        if not -90 <= latitude <= 90:
            raise TripError("Latitude must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise TripError("Longitude must be between -180 and 180.")
        self._latitude = latitude
        self._longitude = longitude

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    def distance_to(self, other):
        r = 6371
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlat = lat2 - lat1
        dlon = math.radians(other.longitude - self.longitude)
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * r * math.asin(math.sqrt(a))

    def to_dict(self):
        return {"name": self.name, "latitude": self.latitude, "longitude": self.longitude}

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class Trip:
    def __init__(self, name="My Trip"):
        self.name = name
        self.waypoints = []

    def add_waypoint(self, waypoint):
        if not isinstance(waypoint, Waypoint):
            raise TripError("Only Waypoint objects can be added.")
        self.waypoints.append(waypoint)

    def remove_waypoint(self, index):
        try:
            return self.waypoints.pop(index)
        except IndexError:
            raise TripError("Waypoint index out of range.")

    def reverse_route(self):
        self.waypoints.reverse()

    def get_legs(self):
        if len(self.waypoints) < 2:
            raise TripError("A trip needs at least 2 waypoints.")
        legs = []
        for i in range(len(self.waypoints) - 1):
            start = self.waypoints[i]
            end = self.waypoints[i + 1]
            legs.append((start, end, start.distance_to(end)))
        return legs

    def total_distance(self):
        return sum(leg[2] for leg in self.get_legs())

    def export(self, exporter, filepath):
        exporter.export(self.waypoints, filepath)

    def save(self, filepath):
        data = {"name": self.name, "waypoints": [w.to_dict() for w in self.waypoints]}
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            raise TripError("Could not save file.")

    @classmethod
    def load(cls, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            trip = cls(data["name"])
            for w in data["waypoints"]:
                trip.add_waypoint(Waypoint(w["latitude"], w["longitude"], w["name"]))
            return trip
        except FileNotFoundError:
            raise TripError("File not found.")
        except (json.JSONDecodeError, KeyError):
            raise TripError("File is not a valid trip file.")


if __name__ == "__main__":
    trip = Trip("Lagos Trip")
    trip.add_waypoint(Waypoint(6.5244, 3.3792, "Lagos Island"))
    trip.add_waypoint(Waypoint(6.4474, 3.3903, "Victoria Island"))
    trip.add_waypoint(Waypoint(6.4698, 3.5852, "Lekki"))

    for start, end, km in trip.get_legs():
        print(f"{start.name} -> {end.name}: {km:.2f} km")
    print(f"Total: {trip.total_distance():.2f} km")

    try:
        Waypoint(95, 0)
    except TripError as e:
        print("Error:", e)
        
        git clone <https://github.com/freedomzip/geospoof-engine.git>
        cd <freedomzip>
