import pytest

def test_osrm_distance_fn_converts_units_and_calls_expected_url(monkeypatch):
    from gotrippee.domain.models import Location
    from gotrippee.distance.osrm import osrm_distance_fn

    a = Location(name="A", latitude=51.5, longitude=-0.1)
    b = Location(name="B", latitude=51.6, longitude=-0.12)

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None
        
        def json(self):
            # 12,345 meters, 687 seconds
            return {"routes": [{"distance": 12345.0, "duration": 678.0}]}
        
    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse()
    
    import gotrippee.distance.osrm as osrm_mod
    monkeypatch.setattr(osrm_mod.requests, "get", fake_get)

    distance_fn = osrm_distance_fn(base_url="https://router.project-osrm.org", profile="driving")
    km, mins = distance_fn(a, b)

    assert "route/v1/driving" in captured["url"]
    # OSRM expects lon, lat; lon, lat
    assert "-0.1,51.5;-0.12,51.6" in captured["url"]

    assert km == 12.345
    assert mins == 11.3 # 678 / 60


def test_osrm_distance_fn_raises_if_no_routes(monkeypatch):
    from gotrippee.domain.models import Location
    from gotrippee.distance.osrm import osrm_distance_fn

    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)

    class FakeResponse:
        def raise_for_status(self):
            return None
        
        def json(self):
            return {"routes": []}
        
    def fake_get(url, params=None, timeout=None):
        return FakeResponse()
    
    import gotrippee.distance.osrm as osrm_mod
    monkeypatch.setattr(osrm_mod.requests, "get", fake_get)

    distance_fn = osrm_distance_fn()
    with pytest.raises(ValueError, match="OSRM.*no routes|no routes"):
        distance_fn(a, b)