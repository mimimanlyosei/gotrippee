def test_demo_main_prints_route_summary_and_returns_zero(capsys):
    from gotrippee.demo import main

    exit_code = main()

    captured = capsys.readouterr()
    out = captured.out

    assert exit_code == 0

    # High-signal strings that prove the demo ran and printed something meaningful
    assert "GoTrippee Demo" in out
    assert "Total distance" in out
    assert "Total duration" in out
    assert "Legs:" in out
    assert "Why this order?" in out

    # Optional: ensure we show a return to start
    assert "Start" in out