from gotrippee.domain.models import Location, RoutePlan
from gotrippee.planner import plan_route


def test_plan_route_two_stops_creates_one_leg_and_zero_totals_for_now():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)

    result = plan_route(stops=[a, b])

    assert isinstance(result, RoutePlan)
    assert result.stops == [a, b]
    assert len(result.legs) == 1
    assert result.total_distance_km == 0.0
    assert result.total_duration_minutes == 0.0


def test_plan_route_uses_distance_fn_and_totals_match():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)
    c = Location(name="C", latitude=2.0, longitude=2.0)

    calls: list[tuple[Location, Location]] = []

    def fake_distance_fn(start: Location, end: Location) -> tuple[float, float]:
        calls.append((start, end))
        if start == a and end == b:
            return (10.0, 20.0)
        if start == b and end == c:
            return (5.5, 10.0)
        raise AssertionError("unexpected leg")

    result = plan_route(stops=[a, b, c], distance_fn=fake_distance_fn)

    assert calls == [(a, b), (b, c)]
    assert len(result.legs) == 2
    assert result.total_distance_km == 15.5
    assert result.total_duration_minutes == 30
