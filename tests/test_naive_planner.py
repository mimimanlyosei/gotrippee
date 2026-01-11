from __future__ import annotations

from gotrippee.planner.naive import plan_route_naive, order_stops_nearest_neighbour
from gotrippee.domain.models import Location, RoutePlan

from unittest.mock import Mock

import gotrippee.planner.naive as naive_mod



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


def test_plan_route_naive_orders_stops_then_call_plan_route(monkeypatch):
    # --- Arrange---
    start = "START"
    stops = ["B", "A", "C"] # deliberately not ordered

    distance_fn = lambda a, b: 1 # not used by this test directly

    expected_ordered_stops = ["A", "B", "C"]
    sentinel_plan = object()

    calls = {
        "order": [],
        "plan": [],
    }

    def fake_order_stops_nearest_neighbour(*, stops, distance_fn):
        calls["order"].append(
            {"stops": list(stops), "distance_fn": distance_fn}
        )
        return expected_ordered_stops
    
    def fake_plan_route(*, stops, distance_fn):
        calls["plan"].append(
            {"stops": list(stops), "distance_fn": distance_fn}
        )
        return sentinel_plan
    
    # Patch the functions on the module under test
    monkeypatch.setattr(naive_mod, "order_stops_nearest_neighbour", fake_order_stops_nearest_neighbour)
    monkeypatch.setattr(naive_mod, "plan_route", fake_plan_route)

    # --- Act ---
    result = naive_mod.plan_route_naive(start=start, stops=stops, distance_fn=distance_fn)

    # --- Assert ---
    assert result is sentinel_plan

    assert len(calls["order"]) == 1
    assert calls["order"][0]["stops"] == stops
    assert calls["order"][0]["distance_fn"] is distance_fn

    assert len(calls["plan"]) == 1
    assert calls["plan"][0]["stops"] == [start, *expected_ordered_stops]
    assert calls["plan"][0]["distance_fn"] is distance_fn


def test_plan_route_naive_returns_routeplan_and_uses_nn_ordering():
    # Arrange: keep it tiny & deterministic
    stops = [
        Location(name="Start", latitude=0.0, longitude=0.0),
        Location(name="A", latitude=1.0, longitude=1.0),
        Location(name="B", latitude=2.0, longitude=2.0)
    ]
    
    start = stops[0]
    to_visit = stops[1:]

    # Use your real distance_fn from Ticket 002 tests if you have one,
    # or use simple dertministic fucntion (eg., manhattan distance):
    def distance_fn(a: Location, b: Location) -> tuple[float, float]:
        distance_km = abs(a.latitude - b.latitude) + abs(a.longitude - b.longitude)
        duration_minutes = 0.0
        return distance_km, duration_minutes

    expected = order_stops_nearest_neighbour(stops=to_visit, distance_fn=distance_fn)

    # --- Act ---
    plan = plan_route_naive(start=start, stops=to_visit, distance_fn=distance_fn)

    # ---Assert---
    assert isinstance(plan, RoutePlan)
    assert plan.stops == [start, *expected] # <-- adjust attribute name if RoutePlan stores stops differently



    # Ticket 005 - Round Trip

def test_plan_route_naive_round_trip_delegates_ordering_and_planning(monkeypatch):
    # --- Arrange ---
    from unittest.mock import Mock
    from gotrippee.domain.models import Location, RoutePlan
    import gotrippee.planner.naive as naive_planner

    start = Location(name="Start", latitude=0.0, longitude=0.0)
    a = Location(name="A", latitude=1.0, longitude=1.0)
    b = Location(name="B", latitude=2.0, longitude=2.0)
    c = Location(name="C", latitude=3.0, longitude=3.0)
    stops = [a, b, c]

    distance_fn = Mock()

    ordered = [b, a, c]

    order_mock = Mock(return_value=ordered)
    plan_mock = Mock()

    monkeypatch.setattr(naive_planner, "order_stops_nearest_neighbour", order_mock)
    monkeypatch.setattr(naive_planner, "plan_route", plan_mock)

    expected_plan = Mock()
    plan_mock.return_value = expected_plan

    # ---Act---
    result = naive_planner.plan_route_naive_round_trip(
        start=start,
        stops=stops,
        distance_fn=distance_fn,
    )

    # --- Assert ---
    order_mock.assert_called_once_with(stops=stops, distance_fn=distance_fn)
    plan_mock.assert_called_once_with(
        stops=[start, *ordered, start],
        distance_fn=distance_fn,
    )
    assert result is expected_plan



def test_plan_route_naive_round_trip_with_no_stops_plans_just_start(monkeypatch):
    from unittest.mock import Mock
    from gotrippee.domain.models import Location
    import gotrippee.planner.naive as naive_planner

    start = Location(name="Start", latitude=0.0, longitude=0.0)
    distance_fn = Mock()

    order_mock = Mock()
    plan_mock = Mock()

    monkeypatch.setattr(naive_planner, "order_stops_nearest_neighbour", order_mock)
    monkeypatch.setattr(naive_planner, "plan_route", plan_mock)

    expected_plan = Mock()
    plan_mock.return_value = expected_plan
    
    result = naive_planner.plan_route_naive_round_trip(
        start=start,
        stops=[],
        distance_fn=distance_fn,
    )


    order_mock.assert_not_called()
    plan_mock.assert_called_once_with(stops=[start], distance_fn=distance_fn)
    assert result is expected_plan



def test_plan_route_naive_round_trip_integration_returns_to_start():
    from gotrippee.domain.models import Location
    from gotrippee.planner.naive import plan_route_naive_round_trip

    start = Location(name="Start", latitude=0.0, longitude=0.0)
    a = Location(name="A", latitude=1.0, longitude=1.0)
    b = Location(name="B", latitude=2.0, longitude=2.0)

    # Deterministic distance: use a simple lookup table
    pairs = {
        (start, a): (10.0, 10.0),
        (start, b): (5.0, 5.0),
        (a, b): (2.0, 2.0),
        (b, a): (2.0, 2.0),
        (a, start): (10.0, 10.0),
        (b, start): (5.0, 5.0),
    }

    def distance_fn(x, y):
        # Make symmetric fallback if your table isn’t fully populated
        if (x, y) in pairs:
            return pairs[(x, y)]
        if (y, x) in pairs:
            return pairs[(y, x)]
        raise KeyError((x, y))

    plan = plan_route_naive_round_trip(start=start, stops=[a, b], distance_fn=distance_fn)

    # Assertions: adapt to your actual RoutePlan structure
    assert plan.legs[0].start == start
    assert plan.legs[-1].end == start
    assert len(plan.legs) == 3  # 2 stops => 3 legs in a round trip