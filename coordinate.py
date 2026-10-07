# coordinates.py

import math


class Waypoint:
    """
    Represents a geographic location using latitude and longitude.
    """

    def __init__(self, latitude, longitude, name=None):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.name = name

    def __repr__(self):
        if self.name:
            return (
                f"Waypoint(name='{self.name}', "
                f"latitude={self.latitude}, "
                f"longitude={self.longitude})"
            )

        return (
            f"Waypoint(latitude={self.latitude}, "
            f"longitude={self.longitude})"
        )

    def distance_to(self, other):
        """
        Calculate the distance between this waypoint
        and another waypoint using the Haversine formula.

        Returns:
            Distance in kilometers.
        """

        earth_radius = 6371.0

        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)

        delta_lat = math.radians(
            other.latitude - self.latitude
        )

        delta_lon = math.radians(
            other.longitude - self.longitude
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        return earth_radius * c

    def bearing_to(self, other):
        """
        Calculate the initial bearing from this waypoint
        to another waypoint.

        Returns:
            Bearing in degrees from 0 to 360.
        """

        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)

        delta_lon = math.radians(
            other.longitude - self.longitude
        )

        x = (
            math.sin(delta_lon)
            * math.cos(lat2)
        )

        y = (
            math.cos(lat1) * math.sin(lat2)
            - math.sin(lat1)
            * math.cos(lat2)
            * math.cos(delta_lon)
        )

        bearing = math.degrees(
            math.atan2(x, y)
        )

        return (bearing + 360) % 360

    def move(self, distance_km, bearing_degrees):
        """
        Calculate a new waypoint after moving a specified
        distance in a specified direction.

        Args:
            distance_km: Distance to travel in kilometers.
            bearing_degrees: Direction of travel in degrees.

        Returns:
            A new Waypoint object.
        """

        earth_radius = 6371.0

        latitude = math.radians(self.latitude)
        longitude = math.radians(self.longitude)
        bearing = math.radians(bearing_degrees)

        angular_distance = distance_km / earth_radius

        new_latitude = math.asin(
            math.sin(latitude)
            * math.cos(angular_distance)
            + math.cos(latitude)
            * math.sin(angular_distance)
            * math.cos(bearing)
        )

        new_longitude = longitude + math.atan2(
            math.sin(bearing)
            * math.sin(angular_distance)
            * math.cos(latitude),
            math.cos(angular_distance)
            - math.sin(latitude)
            * math.sin(new_latitude)
        )

        new_latitude = math.degrees(new_latitude)
        new_longitude = math.degrees(new_longitude)

        # Normalize longitude to -180 to +180
        new_longitude = (
            new_longitude + 180
        ) % 360 - 180

        return Waypoint(
            new_latitude,
            new_longitude
        )


def calculate_distance(point_a, point_b):
    """
    Convenience function for calculating distance
    between two Waypoint objects.
    """

    return point_a.distance_to(point_b)


def calculate_bearing(point_a, point_b):
    """
    Convenience function for calculating the bearing
    between two Waypoint objects.
    """

    return point_a.bearing_to(point_b)


if __name__ == "__main__":

    # Example locations
    lagos = Waypoint(
        6.5244,
        3.3792,
        "Lagos"
    )

    abuja = Waypoint(
        9.0765,
        7.3986,
        "Abuja"
    )

    # Calculate distance
    distance = lagos.distance_to(abuja)

    print("Distance from Lagos to Abuja:")
    print(f"{distance:.2f} km")

    # Calculate bearing
    bearing = lagos.bearing_to(abuja)

    print("\nBearing from Lagos to Abuja:")
    print(f"{bearing:.2f} degrees")

    # Simulate movement
    new_position = lagos.move(
        distance_km=10,
        bearing_degrees=90
    )

    print("\nPosition after moving 10 km east:")
    print(new_position)