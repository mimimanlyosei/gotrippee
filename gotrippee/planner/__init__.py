from __future__ import annotations

from collections.abc import Callable, Sequence

from gotrippee.domain.models import Leg, Location, RoutePlan

DistanceFn = Callable[[Location, Location], tuple[float, float]]


def plan_route(*, stops: Sequence[Location], distance_fn: DistanceFn | None = None) -> RoutePlan:
    if len(stops) < 2:
        raise ValueError("stops must contain at least 2 locations")

    def default_distance_fn(start: Location, end: Location) -> tuple[float, float]:
        # Ticket 002 default: deterministic but “dumb”.
        return (0.0, 0.0)

    distance_fn = distance_fn or default_distance_fn

    legs: list[Leg] = []
    total_distance = 0.0
    total_duration = 0.0

    for start, end in zip(stops, stops[1:], strict=False):
        distance_km, duration_minutes = distance_fn(start, end)
        legs.append(
            Leg(
                start=start,
                end=end,
                distance_km=distance_km,
                duration_minutes=duration_minutes,
            )
        )
        total_distance += distance_km
        total_duration += duration_minutes

    return RoutePlan(
        stops=list(stops),
        legs=legs,
        total_distance_km=total_distance,
        total_duration_minutes=total_duration,
    )
