import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    main._inflight = 0
    client.delete("/workouts")
    yield
    main._inflight = 0
    client.delete("/workouts")


def test_parallelism_limit_and_retry_timeout_behavior(monkeypatch):
    orig_max = main._MAX_INFLIGHT
    try:
        monkeypatch.setattr(main, "_MAX_INFLIGHT", 2)
        main._inflight = main._MAX_INFLIGHT

        payload = {
            "date": "2024-01-01",
            "duration_min": 30,
            "notes": "ok",
        }
        r = client.post("/workouts", json=payload)
        assert r.status_code == 429
        assert "too many concurrent requests" in r.json()["detail"].lower()
    finally:
        main._inflight = 0
        monkeypatch.setattr(main, "_MAX_INFLIGHT", orig_max)

    calls = {"n": 0}

    def flaky_read():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("transient failure")
        return []

    def fake_retry_read(fn, *, attempts, base_delay, max_delay, budget_left):
        last_exc = None
        for i in range(attempts):
            if budget_left():
                break
            try:
                return fn()
            except Exception as e:
                last_exc = e
                delay = min(max_delay, base_delay * (2**i))
                if not budget_left():
                    main.time.sleep(delay)
        if last_exc:
            raise last_exc

    def noop_sleep(_secs):
        pass

    monkeypatch.setattr(main, "retry_read", fake_retry_read)
    monkeypatch.setattr(main.time, "sleep", noop_sleep)

    class FakeScalars:
        def all(self):
            return flaky_read()

    class FakeResult:
        def scalars(self):
            return FakeScalars()

    def fake_execute(_self, _stmt):
        return FakeResult()

    from sqlalchemy.orm import Session

    monkeypatch.setattr(Session, "execute", fake_execute, raising=True)

    r2 = client.get("/workouts")
    assert r2.status_code == 200
    assert r2.json() == []
    assert calls["n"] == 3

    calls_timeout = {"n": 0}

    def always_slow_and_failing():
        calls_timeout["n"] += 1
        raise RuntimeError("still failing")

    def fake_retry_read_timeout(fn, *, attempts, base_delay, max_delay, budget_left):
        last_exc = None
        for i in range(attempts):
            if budget_left():
                break
            try:
                return fn()
            except Exception as e:
                last_exc = e
                main.time.sleep(0.5)
        if last_exc:
            raise last_exc

    monkeypatch.setattr(main, "retry_read", fake_retry_read_timeout)

    now = {"t": 0.0}

    def fake_monotonic():
        return now["t"]

    def sleep_advances(secs):
        now["t"] += secs

    monkeypatch.setattr(main.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(main.time, "sleep", sleep_advances)

    def fake_execute_timeout(_self, _stmt):
        return FakeResultTimeout()

    class FakeScalarsTimeout:
        def all(self):
            return always_slow_and_failing()

    class FakeResultTimeout:
        def scalars(self):
            return FakeScalarsTimeout()

    monkeypatch.setattr(Session, "execute", fake_execute_timeout, raising=True)

    r3 = client.get("/workouts")
    assert r3.status_code == 500
    assert "failed to" in r3.json()["detail"].lower()
