"""
coordinates.py
--------------
Owner: Alhassan Kabir

Defines the core geographic data object (Waypoint) and the distance/bearing
math every other module depends on. Nothing else in the project should
re-implement this math -- import and use these functions instead.
"""

from __future__ import annotations
from dataclasses import dataclass
import math

# Mean radius of the Earth in meters (WGS-84 mean radius, good enough for simulation purposes)
EARTH_RADIUS_M = 6_371_000.0


@dataclass
class Waypoint:
    """
    A single geographic point.

    Attributes:
        latitude: Decimal degrees, -90 to 90.
        longitude: Decimal degrees, -180 to 180.
        label: Optional human-readable name (e.g. "Warehouse A"), useful for
               logging and for telemetry/GPX export later.
    """
    latitude: float
    longitude: float
    label: str | None = None

    def __post_init__(self) -> None:
        # Encapsulation: validate on construction so no invalid Waypoint
        # can ever exist downstream. Raise, don't silently clamp -- callers
        # (validation.py / api_client.py) are responsible for catching this.
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"latitude out of range: {self.latitude}")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"longitude out of range: {self.longitude}")

    def as_tuple(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)

    def __str__(self) -> str:
        name = f"{self.label} " if self.label else ""
        return f"{name}({self.latitude:.6f}, {self.longitude:.6f})"


def haversine_distance_m(a: Waypoint, b: Waypoint) -> float:
    """
    Great-circle distance between two Waypoints, in meters.

    This is the standard Haversine formula -- accurate enough for simulated
    GPS tracks (it assumes a spherical Earth, which introduces well under
    0.5% error at the distances this project deals with).
    """
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(min(1.0, math.sqrt(h)))  # clamp to guard float rounding past 1.0
    return EARTH_RADIUS_M * c


def initial_bearing_deg(a: Waypoint, b: Waypoint) -> float:
    """
    Initial compass bearing (degrees, 0-360, 0 = North) to travel from
    Waypoint a to Waypoint b along the great-circle path.

    Used by spoofer_engine.py to figure out which direction to "move" the
    simulated position at each timestep.
    """
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def destination_point(start: Waypoint, bearing_deg: float, distance_m: float) -> Waypoint:
    """
    Given a starting Waypoint, a bearing (degrees), and a distance (meters),
    compute the resulting Waypoint. This is what lets spoofer_engine.py
    "move" a simulated position step by step along a route instead of just
    interpolating in a straight line on a flat projection.
    """
    angular_distance = distance_m / EARTH_RADIUS_M
    bearing = math.radians(bearing_deg)

    lat1 = math.radians(start.latitude)
    lon1 = math.radians(start.longitude)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2),
    )

    return Waypoint(latitude=math.degrees(lat2), longitude=math.degrees(lon2))


if __name__ == "__main__":
    # Quick manual sanity check -- run `python coordinates.py` directly.
    # Lagos, Nigeria -> Abuja, Nigeria (straight-line distance ~526 km;
    # road distance is ~750 km, but this function computes great-circle distance)
    lagos = Waypoint(6.5244, 3.3792, label="Lagos")
    abuja = Waypoint(9.0765, 7.3986, label="Abuja")

    dist_km = haversine_distance_m(lagos, abuja) / 1000
    bearing = initial_bearing_deg(lagos, abuja)

    print(f"{lagos} -> {abuja}")
    print(f"Distance: {dist_km:.1f} km")
    print(f"Initial bearing: {bearing:.1f} degrees")