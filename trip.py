"""
trip.py
-------
Composition: a Trip owns an ordered collection of Waypoint objects and
exposes route-level operations (total distance, leg-by-leg breakdown).
spoofer_engine.py consumes a Trip to know where to simulate movement to.
"""

from __future__ import annotations
from coordinates import Waypoint, haversine_distance_m, initial_bearing_deg


class Trip:
    """
    An ordered route made up of two or more Waypoints.
    """

    def __init__(self, waypoints: list[Waypoint] | None = None) -> None:
        self.waypoints: list[Waypoint] = waypoints or []

    def add_waypoint(self, waypoint: Waypoint) -> None:
        """Append a Waypoint to the end of the route."""
        self.waypoints.append(waypoint)

    def total_distance_m(self) -> float:
        """Sum of great-circle distances across every consecutive pair of waypoints."""
        if len(self.waypoints) < 2:
            return 0.0

        total = 0.0
        for i in range(len(self.waypoints) - 1):
            total += haversine_distance_m(self.waypoints[i], self.waypoints[i + 1])
        return total

    def legs(self) -> list[tuple[Waypoint, Waypoint, float, float]]:
        """
        Break the trip into legs.

        Returns a list of (start_waypoint, end_waypoint, distance_m, bearing_deg)
        tuples, one per consecutive pair of waypoints. spoofer_engine.py
        iterates over this to generate simulated movement leg by leg.

        Raises ValueError if the trip has fewer than 2 waypoints, since a
        route needs at least a start and an end to have any legs.
        """
        if len(self.waypoints) < 2:
            raise ValueError(
                f"Trip needs at least 2 waypoints to have legs, has {len(self.waypoints)}"
            )

        result = []
        for i in range(len(self.waypoints) - 1):
            start = self.waypoints[i]
            end = self.waypoints[i + 1]
            distance = haversine_distance_m(start, end)
            bearing = initial_bearing_deg(start, end)
            result.append((start, end, distance, bearing))
        return result

    def __len__(self) -> int:
        return len(self.waypoints)

    def __iter__(self):
        return iter(self.waypoints)

    def __str__(self) -> str:
        if not self.waypoints:
            return "Trip(empty)"
        names = " -> ".join(str(wp) for wp in self.waypoints)
        return f"Trip({names}, total={self.total_distance_m() / 1000:.1f} km)"


if __name__ == "__main__":
    # Quick manual sanity check -- run `python trip.py` directly.
    # Using national capitals so the route crosses country borders --
    # useful for demoing geofencing / region-based use cases later.
    nigeria = Waypoint(9.0765, 7.3986, label="Nigeria (Abuja)")
    ghana = Waypoint(5.6037, -0.1870, label="Ghana (Accra)")
    ivory_coast = Waypoint(5.3600, -4.0083, label="Ivory Coast (Abidjan)")

    trip = Trip([nigeria, ghana, ivory_coast])
    print(trip)
    print(f"Number of legs: {len(trip.legs())}")

    for start, end, distance, bearing in trip.legs():
        print(
            f"  {start.label} -> {end.label}: "
            f"{distance / 1000:.1f} km, bearing {bearing:.1f} deg"
        )