from __future__ import annotations

from collections.abc import Callable

import requests

from gotrippee.domain.models import Location

DistanceFn = Callable[[Location, Location], tuple[float,float]]


def osrm_distance_fn(
        *,
        base_url: str = "https://router.project-osrm.org",
        profile: str = "driving",
        timeout_seconds: float = 10.0,
) -> DistanceFn:
    base_url = base_url.rstrip("/")

    def _distance(a: Location, b: Location) -> tuple[float, float]:
        url = (
            f"{base_url}/route/v1/{profile}"
            f"{a.longitude},{a.latitude};{b.longitude},{b.latitude}"
        )

        resp = requests.get(url, params={"overview": "false"}, timeout=timeout_seconds)
        resp.raise_for_status()
        data = resp.json()

        routes = data.get("routes") or []
        if not routes:
            raise ValueError("OSRM returned no routes")
        
        meters = float(routes[0]["distance"])
        seconds = float(routes[0]["duration"])

        km = meters /1000.0
        minutes = seconds / 60.0
        return (km, minutes)
    
    return _distance