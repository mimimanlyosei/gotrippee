from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Location:
    name: str
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"latitude must be between -90 and 90, got {self.latitude}")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"longitude must be between -180 and 180, go {self.longitude}")


@dataclass(frozen=True, slots=True)
class Leg:
    start: Location
    end: Location
    distance_km: float
    duration_minutes: float

    def __post_init__(self) -> None:
        if self.distance_km < 0:
            raise ValueError(f"distance_km must be >= 0, got {self.distance_km}")

        if self.duration_minutes < 0:
            raise ValueError(f"duration_minutes musr be >= 0, got {self.duration_minutes}")


@dataclass(frozen=True, slots=True)
class RoutePlan:
    stops: Sequence[Location]
    legs: Sequence[Leg]
    total_distance_km: float
    total_duration_minutes: float

    def __post_init__(self) -> None:
        expected_legs = max(len(self.stops) - 1, 0)
        if len(self.legs) != expected_legs:
            raise ValueError(
                f"legs must be exactly stops - 1 (expected {expected_legs}, got {len(self.legs)})"
            )

        sum_distance = sum(leg.distance_km for leg in self.legs)
        sum_duration = sum(leg.duration_minutes for leg in self.legs)

        if not math.isclose(self.total_distance_km, sum_distance, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(
                f"total_distance_km must equal sum of leg distances "
                f"({sum_distance}), got {self.total_distance_km}"
            )

        if not math.isclose(self.total_duration_minutes, sum_duration, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(
                f"total_duration_minutes must equal sum of leg durations "
                f"({sum_duration}), got {self.total_duration_minutes}"
            )
