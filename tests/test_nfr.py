from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_nfr_01_get_workouts_returns_list():
    import statistics
    import time

    N = 200
    times = []
    for _ in range(N):
        start = time.perf_counter()
        resp = client.get("/workouts")
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        assert resp.status_code == 200
    p95 = statistics.quantiles(times, n=100)[94]
    assert p95 <= 250


def test_nfr_02_create_workout_returns_created():
    client.delete("/workouts")
    N = 200
    count = 0
    for i in range(1, N + 1):
        payload = {
            "id": i,
            "date": "2025-01-01",
            "duration_min": 30,
            "notes": "Test workout",
        }
        resp = client.post("/workouts", json=payload)
        assert resp.status_code == 201
        if resp.status_code == 201:
            count += 1
    assert count / 200 >= 0.99


def test_nfr_03_set_binding_and_errors():
    client.delete("/workouts")
    workout_payload = {
        "id": 201,
        "date": "2025-01-01",
        "duration_min": 30,
        "notes": "Test workout",
    }
    resp = client.post("/workouts", json=workout_payload)
    assert resp.status_code == 201
    set_payload = {
        "id": 100,
        "workout_id": 201,
        "exercise": "Push-ups",
        "reps": 15,
        "weight_kg": "45.0",
    }
    resp = client.post("/workouts/201/sets", json=set_payload)
    assert resp.status_code == 201
    assert resp.json() == set_payload

    resp = client.post(
        "/workouts/999/sets",
        json={
            "id": 101,
            "workout_id": 999,
            "exercise": "Push-ups",
            "reps": 15,
            "weight_kg": "45.0",
        },
    )
    assert resp.status_code == 404

    resp = client.post(
        "/workouts/202/sets",
        json={
            "id": 102,
            "exercise": "Push-ups",
            "reps": 15,
            "weight_kg": "45.0",
        },
    )
    assert resp.status_code == 404

    resp = client.post("/workouts/201/sets", json=set_payload)
    assert resp.status_code == 400
