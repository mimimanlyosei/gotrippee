def test_cached_distance_fn_caches_repeated_calls_for_the_same_pair():
    from gotrippee.domain.models import Location
    from gotrippee.distance.cache import cached_distance_fn

    calls = {"n": 0}

    def base_distance_fn(a, b):
        calls["n"] += 1
        return (1.23, 4.56)
    
    a = Location(name="A", latitude=1.0, longitude=2.0)
    b = Location(name="B", latitude=3.0, longitude=4.0)

    cached = cached_distance_fn(base_distance_fn)

    assert cached(a, b) == (1.23, 4.56)
    assert cached(a, b) == (1.23, 4.56)
    assert calls["n"] == 1


def test_cached_distance_fn_treats_reverese_pair_as_same_key():
    from gotrippee.domain.models import Location
    from gotrippee.distance.cache import cached_distance_fn

    calls = {"n": 0}

    def base_distance_fn(a, b):
        calls["n"] += 1
        return (7.0, 8.0)
    
    a = Location(name="A", latitude=10.0, longitude=20.0)
    b = Location(name="B", latitude=30.0, longitude=40.0)

    cached = cached_distance_fn(base_distance_fn)

    assert cached(a, b) == (7.0, 8.0)
    assert cached(a, b) == (7.0, 8.0)
    assert calls["n"] == 1


def test_cached_distance_fn_does_not_mix_different_pairs():
    from gotrippee.domain.models import Location
    from gotrippee.distance.cache import cached_distance_fn

    calls = {"n": 0}

    def base_distance_fn(a, b):
        calls["n"] += 1
        return (float(calls["n"]), 0.0)
    
    a = Location(name="A", latitude=0.0, longitude=0.0)
    b = Location(name="B", latitude=1.0, longitude=1.0)
    c = Location(name="C", latitude=2.0, longitude=2.0)


    cached = cached_distance_fn(base_distance_fn)

    assert cached(a, b)[0] == 1.0
    assert cached(a, c)[0] == 2.0
    assert calls["n"] == 2