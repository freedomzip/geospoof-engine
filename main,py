"""
main.py
-------
Owner: Freedom Ojomah (coordination / integration)

Command-line entry point that ties every module together. Written against
the current interfaces of all modules -- the parts that depend on
validation.py, api_client.py, spoofer_engine.py, and data_exporter.py are
wrapped so this file runs cleanly even before those are finished, and will
start working for real as each teammate pushes their module.
"""

from trip import Trip
from coordinates import Waypoint

# These imports will start doing real work once each owner finishes their
# module. Until then, calling into them below raises NotImplementedError,
# which main() catches and reports clearly instead of crashing.
from spoofer_engine import WalkSimulator, DroneSimulator
from data_exporter import export_to_gpx
from api_client import geocode_place, ApiError
from validation import ValidationError


PROFILE_CHOICES = {
    "walk": WalkSimulator,
    "drone": DroneSimulator,
}


def build_trip_from_place_names(place_names: list[str]) -> Trip:
    """
    Resolve a list of place names into a Trip, using api_client.geocode_place().

    Any single place that fails to geocode is reported and skipped rather
    than crashing the whole run -- a bad place name shouldn't lose the rest
    of the route.
    """
    trip = Trip()
    for name in place_names:
        try:
            waypoint = geocode_place(name)
        except ApiError as exc:
            print(f"  [skipped] Could not resolve '{name}': {exc}")
            continue
        except ValidationError as exc:
            print(f"  [skipped] Invalid input '{name}': {exc}")
            continue
        trip.add_waypoint(waypoint)
        print(f"  [ok] {name} -> {waypoint}")
    return trip


def build_trip_from_coordinates(waypoints: list[Waypoint]) -> Trip:
    """Build a Trip directly from already-known Waypoints -- no API calls."""
    return Trip(waypoints)


def choose_profile(profile_name: str):
    """Look up the simulator class for a profile name ('walk' or 'drone')."""
    try:
        return PROFILE_CHOICES[profile_name.lower()]
    except KeyError:
        valid = ", ".join(PROFILE_CHOICES)
        raise ValueError(f"Unknown profile '{profile_name}'. Choose from: {valid}")


def run_simulation(trip: Trip, profile_name: str, output_path: str) -> None:
    """
    Run a full simulation: build the simulator, generate telemetry,
    export to GPX, and print a summary.
    """
    if len(trip) < 2:
        print("Need at least 2 waypoints to simulate a route. Aborting.")
        return

    simulator_cls = choose_profile(profile_name)
    simulator = simulator_cls(trip)

    print(f"\nSimulating with {simulator_cls.__name__}...")
    try:
        telemetry = simulator.run()
    except NotImplementedError:
        print(
            "  spoofer_engine.py hasn't been implemented yet (BaseSpoofer.run()) "
            "-- nothing to export until that's done."
        )
        return

    try:
        export_to_gpx(telemetry, output_path)
    except OSError as exc:
        print(f"  Failed to write output file: {exc}")
        return
    except NotImplementedError:
        print("  data_exporter.py hasn't been implemented yet -- telemetry generated but not saved.")
        return

    distance_km = trip.total_distance_m() / 1000
    duration_s = telemetry[-1].timestamp_s if telemetry else 0
    print(f"  Route distance: {distance_km:.1f} km")
    print(f"  Simulated duration: {duration_s:.0f} s ({duration_s / 60:.1f} min)")
    print(f"  Telemetry points: {len(telemetry)}")
    print(f"  Output written to: {output_path}")


def main() -> None:
    print("=== GeoSpoof Engine ===\n")

    # --- Example run using hardcoded waypoints (always works, no API needed) ---
    # Swap this block for build_trip_from_place_names([...]) once
    # api_client.py / validation.py are finished and you want to take
    # free-text place names instead.
    print("Building route from hardcoded waypoints...")
    nigeria = Waypoint(9.0765, 7.3986, label="Nigeria (Abuja)")
    ghana = Waypoint(5.6037, -0.1870, label="Ghana (Accra)")
    trip = build_trip_from_coordinates([nigeria, ghana])
    print(f"  Route: {trip}")

    run_simulation(trip, profile_name="drone", output_path="output.gpx")


if __name__ == "__main__":
    main()