from __future__ import annotations

from collections.abc import Callable

from gotrippee.domain.models import Location

DistanceFN = Callable[[Location, Location], tuple[float, float]]


def cached_distance_fn(distance_fn: DistanceFN) -> DistanceFN:
    cache: dict[
        tuple[tuple[float, float], tuple[float, float]],
        tuple[float, float],
    ] = {}

    def key_for(a: Location, b: Location) -> tuple[tuple[float, float], tuple[float, float]]:
        p1 = (a.latitude, a.longitude)
        p2 = (b.latitude, b.longitude)
        #symmetry: (a,b) == (b,a)
        return (p1, p2) if p1 <= p2 else (p2, p1)
    
    def _distance(a: Location, b: Location) -> tuple[float, float]:
        key = key_for(a, b)
        if key in cache:
            return cache[key]
        value = distance_fn(a, b)
        cache[key] = value
        return value
    
    return _distance