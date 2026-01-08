import pytest

from gotrippee.domain.models import Leg, Location, RoutePlan

# Tests for Location


def test_location_valid_creates():
    loc = Location(name="IKEA Wembley", latitude=51.552, longitude=-0.296)
    assert loc.name == "IKEA Wembley"


def test_location_invalid_latitude_raises():
    with pytest.raises(ValueError):
        Location(name="Bad Lat", latitude=999.0, longitude=0.0)


def test_location_invalid_longditude_raises():
    with pytest.raises(ValueError):
        Location(name="Bad Lon", latitude=0.0, longitude=999.0)


# Tests for Leg


def test_leg_validation_creates():
    start = Location(name="Start", latitude=0.0, longitude=0.0)
    end = Location(name="End", latitude=1.0, longitude=1.0)

    leg = Leg(start=start, end=end, distance_km=10.5, duration_minutes=25.0)

    assert leg.start == start
    assert leg.end == end
    assert leg.distance_km == 10.5
    assert leg.duration_minutes == 25.0


def test_leg_negative_distance_raises():
    start = Location(name="start", latitude=0.0, longitude=0.0)
    end = Location(name="End", latitude=1.0, longitude=1.0)

    with pytest.raises(ValueError):
        Leg(start=start, end=end, distance_km=-1.0, duration_minutes=10.0)


def test_leg_negative_duration_raises():
    start = Location(name="start", latitude=0.0, longitude=0.0)
    end = Location(name="End", latitude=1.0, longitude=1.0)

    with pytest.raises(ValueError):
        Leg(start=start, end=end, distance_km=-1.0, duration_minutes=10.0)


# Tests for RoutePlan


def test_routeplan_valid_creates_and_totals_match():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)
    c = Location(name="C", latitude=2.0, longitude=2.0)

    leg1 = Leg(start=a, end=b, distance_km=10.0, duration_minutes=20.0)
    leg2 = Leg(start=b, end=c, distance_km=5.5, duration_minutes=10.0)

    plan = RoutePlan(
        stops=[a, b, c], legs=[leg1, leg2], total_distance_km=15.5, total_duration_minutes=30
    )

    assert plan.total_distance_km == 15.5
    assert plan.total_duration_minutes == 30.0
    assert len(plan.legs) == 2
    assert len(plan.stops) == 3

    def test_routeplan_legs_must_be_stops_minus_one():
        a = Location(name="A", latitude=0.0, longitude=0.0)
        b = Location(name="B", latitude=1.0, longitude=1.0)

        leg = Leg(start=a, end=b, distance_km=1.0, duration_minutes=1.0)

        # stops=2 implies legs must be 1, so this should fail
        with pytest.raises(ValueError):
            RoutePlan(
                stops=[a, b],
                legs=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
            )

        # stops=1 implies legs must be 0, so this should fail
        with pytest.raises(ValueError):
            RoutePlan(
                stops=[a],
                legs=[leg],
                total_distance_km=1.0,
                total_duration_minutes=1.0,
            )


def test_routeplan_totals_must_equal_sum_of_legs():
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)

    leg = Leg(start=a, end=b, distance_km=10.0, duration_minutes=20.0)

    with pytest.raises(ValueError):
        RoutePlan(
            stops=[a, b],
            legs=[leg],
            total_distance_km=999.0,  # wrong on purpose
            total_duration_minutes=20.0,
        )

    with pytest.raises(ValueError):
        RoutePlan(
            stops=[a, b],
            legs=[leg],
            total_distance_km=10.0,
            total_duration_minutes=999.0,  # wrong on purpose
        )
