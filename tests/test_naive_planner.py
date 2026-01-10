from __future__ import annotations

from gotrippee.domain.models import Location
from gotrippee.planner.naive import order_stops_nearest_neighbour


def test_orders_stops_by_nearest_neighbour_from_first_stop():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)
    c = Location(name="C", latitude=2.0, longitude=2.0)

    # Distnaces from A: B is closer than C. From B: C is next.
    def distance_fn(start: Location, end: Location) -> tuple[float, float]:
        if start == a and end == b:
            return (5.0, 10.0)
        if start == a and end == c:
            return (20.0, 30.0)
        if start == b and end == c:
            return (7.0, 12.0)
        if start == b and end == a:
            return (5.0, 10.0)
        if start == c and end == a:
            return (20.0, 30.0)
        if start == c and end == b:
            return (7.0, 12.0)
        raise AssertionError("unexpected leg")

    ordered = order_stops_nearest_neighbour(stops=[a, c, b], distance_fn=distance_fn)

    assert ordered == [a, b, c]


def test_two_stops_returns_same_order():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)

    def distance_fn(start: Location, end: Location) -> tuple[float, float]:
        return (1.0, 2.0)

        ordered = order_stops_nearest_neighbour(stops=[a, b], distance_fn=distance_fn)

        assert ordered == [a, b]


def test_tie_breaker_is_deterministic_by_input_order():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)
    c = Location(name="C", latitude=2.0, longitude=2.0)

    # From A to B and A to C are equal distance => chose the one that
    # appears first in the remaining list
    def distance_fn(start: Location, end: Location) -> tuple[float, float]:
        if start == a and end in (b, c):
            return (10.0, 0.0)
        return (99.0, 0.0)

    ordered = order_stops_nearest_neighbour(stops=[a, c, b], distance_fn=distance_fn)

    # Remaining list after A is [c,b], tie => choose c first
    assert ordered == [a, c, b]
