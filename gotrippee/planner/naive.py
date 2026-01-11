from __future__ import annotations

from collections.abc import Callable, Sequence

from gotrippee.domain.models import Location

from . import plan_route

DistanceFn = Callable[[Location, Location], tuple[float, float]]


def order_stops_nearest_neighbour(
    *,
    stops: Sequence[Location],
    distance_fn: DistanceFn,
) -> list[Location]:
    if len(stops) < 2:
        raise ValueError("stops must contain at least 2 locations")

    ordered: list[Location] = [stops[0]]
    remaining: list[Location] = list(stops[1:])

    while remaining:
        current = ordered[-1]

        best_idx = 0
        best_distance, _ = distance_fn(current, remaining[0])

        for idx in range(1, len(remaining)):
            d, _ = distance_fn(current, remaining[idx])
            # Tie breaker: keep earlier in remaining list
            # (so only update on stricklt smaller)
            if d < best_distance:
                best_distance = d
                best_idx = idx

        ordered.append(remaining.pop(best_idx))

    return ordered

def plan_route_naive(*, start, stops, distance_fn=None):
    ordered_stops = order_stops_nearest_neighbour(
        stops=stops,
        distance_fn=distance_fn,
    )
    return plan_route(
        stops=[start, *ordered_stops],
        distance_fn=distance_fn,
    )

def plan_route_naive_round_trip(
        *,
        start: Location,
        stops: Sequence[Location],
        distance_fn: DistanceFn,
) -> RoutePlan:
    """
    Naive planner that orders stops using nearest-neighbour and returns to start.
    - If stops is empty, returns a plan with just [start] (0 legs).
    """
    if not stops:
        return plan_route(stops=[start], distance_fn=distance_fn)
    
    ordered = order_stops_nearest_neighbour(stops=stops, distance_fn=distance_fn)
    return plan_route(stops=[start, *ordered, start], distance_fn=distance_fn)