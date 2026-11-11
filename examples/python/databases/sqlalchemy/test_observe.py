from demo_observe import run


def test_observed_commit_and_insert():
    name, commits, inserts, elapsed = run()
    assert name == "alice"
    assert commits == ["committed"]
    assert inserts == ["alice"]
    assert len(elapsed) >= 2
    assert all(value >= 0 for value in elapsed)
