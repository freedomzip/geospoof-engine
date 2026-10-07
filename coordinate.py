"""coordinates.py - Coordinate objects, Haversine distance and movement maths.

Part of the GeoSpoof Engine (Group 8).
Owner: Alhassan Kabir
"""

import math

EARTH_RADIUS_M = 6_371_000  # mean Earth radius in metres


class InvalidCoordinateError(ValueError):
    """Raised when a latitude, longitude or bearing is out of range."""


class Coordinate:
    """A single point on Earth. Latitude and longitude are encapsulated:
    they can only be read through properties and can only be set to valid values."""

    def __init__(self, latitude, longitude):
        self.latitude = latitude    # goes through the setter (validation)
        self.longitude = longitude

    # ---------- encapsulated attributes ----------
    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise InvalidCoordinateError(f"Latitude must be a number, got {value!r}")
        if not -90.0 <= value <= 90.0 or math.isnan(value):
            raise InvalidCoordinateError(f"Latitude must be between -90 and 90, got {value}")
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise InvalidCoordinateError(f"Longitude must be a number, got {value!r}")
        if not -180.0 <= value <= 180.0 or math.isnan(value):
            raise InvalidCoordinateError(f"Longitude must be between -180 and 180, got {value}")
        self._longitude = value

    # ---------- geographic maths ----------
    def distance_to(self, other):
        """Great-circle distance to another Coordinate in metres (Haversine)."""
        self._check_other(other)
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return EARTH_RADIUS_M * c

    def bearing_to(self, other):
        """Initial compass bearing to another Coordinate, 0-360 degrees (0 = north)."""
        self._check_other(other)
        lat1, lat2 = math.radians(self.latitude), math.radians(other.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    def move(self, distance_m, bearing_deg):
        """Return a NEW Coordinate reached by travelling distance_m metres
        along bearing_deg from this point."""
        if distance_m < 0:
            raise InvalidCoordinateError("Distance cannot be negative")
        if not isinstance(bearing_deg, (int, float)) or math.isnan(bearing_deg):
            raise InvalidCoordinateError(f"Bearing must be a number, got {bearing_deg!r}")

        brg = math.radians(bearing_deg % 360)
        ang = distance_m / EARTH_RADIUS_M
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)

        lat2 = math.asin(math.sin(lat1) * math.cos(ang) +
                         math.cos(lat1) * math.sin(ang) * math.cos(brg))
        lon2 = lon1 + math.atan2(math.sin(brg) * math.sin(ang) * math.cos(lat1),
                                 math.cos(ang) - math.sin(lat1) * math.sin(lat2))

        lon_deg = (math.degrees(lon2) + 540) % 360 - 180  # wrap to -180..180
        return Coordinate(math.degrees(lat2), lon_deg)

    def interpolate(self, other, fraction):
        """Point a given fraction (0.0-1.0) of the way along the straight
        (great-circle) path to another Coordinate."""
        self._check_other(other)
        if not 0.0 <= fraction <= 1.0:
            raise InvalidCoordinateError("Fraction must be between 0 and 1")
        total = self.distance_to(other)
        if total == 0:
            return Coordinate(self.latitude, self.longitude)
        return self.move(total * fraction, self.bearing_to(other))

    # ---------- helpers ----------
    @staticmethod
    def _check_other(other):
        if not isinstance(other, Coordinate):
            raise TypeError("Expected a Coordinate object")

    def __eq__(self, other):
        return (isinstance(other, Coordinate)
                and math.isclose(self.latitude, other.latitude, abs_tol=1e-9)
                and math.isclose(self.longitude, other.longitude, abs_tol=1e-9))

    def __hash__(self):
        return hash((round(self.latitude, 9), round(self.longitude, 9)))

    def __repr__(self):
        return f"Coordinate(latitude={self.latitude:.6f}, longitude={self.longitude:.6f})"

    def __str__(self):
        return f"{self.latitude:.6f}, {self.longitude:.6f}"


class MovementMath:
    """Helpers the simulators use to turn a route into timed steps."""

    @staticmethod
    def build_path(start, end, speed_mps, interval_s=1.0):
        """Return a list of Coordinates from start to end, one every interval_s
        seconds, travelling at speed_mps (metres per second). Ends exactly on `end`."""
        if speed_mps <= 0:
            raise ValueError("Speed must be greater than zero")
        if interval_s <= 0:
            raise ValueError("Interval must be greater than zero")

        total = start.distance_to(end)
        step = speed_mps * interval_s
        if total == 0:
            return [start]

        steps = max(1, math.ceil(total / step))
        path = [start.interpolate(end, i / steps) for i in range(steps)]
        path.append(Coordinate(end.latitude, end.longitude))
        return path

    @staticmethod
    def path_length(points):
        """Total length in metres of a list of Coordinates."""
        return sum(a.distance_to(b) for a, b in zip(points, points[1:]))

    @staticmethod
    def travel_time(distance_m, speed_mps):
        """Seconds needed to cover distance_m at speed_mps."""
        if speed_mps <= 0:
            raise ValueError("Speed must be greater than zero")
        return distance_m / speed_mps


if __name__ == "__main__":
    abuja = Coordinate(9.0765, 7.3986)
    zaria = Coordinate(11.0855, 7.7199)
    print("Distance (km):", round(abuja.distance_to(zaria) / 1000, 1))
    print("Bearing:", round(abuja.bearing_to(zaria), 1))
    path = MovementMath.build_path(abuja, zaria, speed_mps=1.4, interval_s=600)
    print("Points:", len(path), "| first:", path[0], "| last:", path[-1])
    try:
        Coordinate(200, 0)
    except InvalidCoordinateError as err:
        print("Caught:", err)