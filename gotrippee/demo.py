from __future__ import annotations

from typing import Dict, Tuple

from gotrippee.domain.models import Location
from gotrippee.planner.naive import plan_route_naive_round_trip


def _demo_distance_fn(pairs: Dict[Tuple[str, str], Tuple[float,float]]):
    def distance_fn(a: Location, b: Location) -> Tuple[float, float]:
        key = (a.name, b.name)
        if key in pairs:
            return pairs[key]
        rev = (b.name, a.name)
        if rev in pairs:
            return pairs[rev]
        raise KeyError(key)
    
    return distance_fn


def main() -> int:
    print("GoTrippee Demo")
    print("============")

    start = Location(name="Start", latitude=0.0, longitude=0.0)
    a = Location(name="A", latitude=1.0, longitude=1.0)
    b = Location(name="B", latitude=2.0, longitude=2.0)
    c = Location(name="C", latitude=3.0, longitude=3.0)

    pairs = {
        ("Start", "A"): (10.0, 12.0),
        ("Start", "B"): (5.0, 7.0),
        ("Start", "C"): (8.0, 9.0),
        ("A", "B"): (2.0, 3.0),
        ("A", "C"): (4.0, 5.0),
        ("B", "C"): (3.0, 4.0),
    }
    distance_fn = _demo_distance_fn(pairs)

    plan = plan_route_naive_round_trip(
        start=start,
        stops=[a, b, c],
        distance_fn=distance_fn,
    )

    print(f"Total distance: {plan.total_distance_km:.1f} km")
    print(f"Total duration: {plan.total_duration_minutes:.0f} mins")
    print("Legs:")

    for i, leg in enumerate(plan.legs, start=1):
        print(
            f"{i}. {leg.start.name} -> {leg.end.name} "
            f"({leg.distance_km:.1f} km, {leg.duration_minutes:.0f} mins)"
        )

    return 0

if __name__ == "__man__":
    raise SystemExit(main())

    