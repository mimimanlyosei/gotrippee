from __future__ import annotations

from collections.abc import Callable, Sequence

from gotrippee.domain.models import Location

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
        best_distance = distance_fn(current, remaining[0])[0]

        for idx in range(1, len(remaining)):
            d = distance_fn(current, remaining[idx])[0]
            # Tie breaker: keep earlier in remaining list
            # (so only update on stricklt smaller)
            if d < best_distance:
                best_distance = d
                best_idx = idx

        ordered.append(remaining.pop(best_idx))

    return ordered
