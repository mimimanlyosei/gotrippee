from __future__ import annotations

from collections.abc import Callable, Sequence

from gotrippee.domain.models import Location, RoutePlan

from . import plan_route

DistanceFn = Callable[[Location, Location], tuple[float, float]]


def _validate_start_and_stops(*, start: Location, stops: Sequence[Location]) -> None:
    # Start must not appear in stops (by equality)
    if any(s == start for s in stops):
        raise ValueError("start must not appear in stops")
    
    # Duplicate stop names (MVP-friendly)
    names = [s.name for s in stops]
    if len(set(names)) != len(names):
        raise ValueError("duplicate stop names are not allowed")



def order_stops_nearest_neighbour(
    *,
    stops: Sequence[Location],
    distance_fn: DistanceFn,
) -> list[Location]:
    if len(stops) < 2:
        return list(stops)

    ordered: list[Location] = [stops[0]]
    remaining: list[Location] = list(stops[1:])

    while remaining:
        current = ordered[-1]

        best_idx = 0
        best_distance, _ = distance_fn(current, remaining[0])

        for idx in range(1, len(remaining)):
            d, _ = distance_fn(current, remaining[idx])
            # Tie breaker: keep earlier in remaining list
            # (so only update on strickly smaller)
            if d < best_distance:
                best_distance = d
                best_idx = idx

        ordered.append(remaining.pop(best_idx))

    return ordered

def plan_route_naive(
        *,
        start: Location,
        stops: Sequence[Location],
        distance_fn: DistanceFn,
        ) -> RoutePlan:
    _validate_start_and_stops(start=start, stops=stops)
    
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
    _validate_start_and_stops(start=start, stops=stops)
    
    if not stops:
        return plan_route(stops=[start], distance_fn=distance_fn)
    
    ordered = order_stops_nearest_neighbour(stops=stops, distance_fn=distance_fn)
    return plan_route(stops=[start, *ordered, start], distance_fn=distance_fn)