from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_r9_no_sets_after_workout_deletion():
    client.delete("/workouts")
    payload = {
        "id": 300,
        "date": "2025-01-01",
        "duration_min": 30,
        "notes": "Test workout",
    }
    resp = client.post("/workouts", json=payload)
    assert resp.status_code == 201, f"Создание тренировки не удалось: {resp.text}"

    set1 = {
        "id": 301,
        "workout_id": 300,
        "exercise": "Push-ups",
        "reps": 15,
        "weight_kg": "45.0",
    }
    set2 = {
        "id": 302,
        "workout_id": 300,
        "exercise": "Push-ups",
        "reps": 16,
        "weight_kg": "46.0",
    }
    resp = client.post("/workouts/300/sets", json=set1)
    assert resp.status_code == 201
    resp = client.post("/workouts/300/sets", json=set2)
    assert resp.status_code == 201

    resp = client.get("/workouts")
    data = resp.json()
    assert isinstance(data, list)
    trainingsCount = len(data)

    resp = client.delete("/workouts/300")
    assert resp.status_code == 204

    resp = client.get("/workouts")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) + 1 == trainingsCount

    resp = client.get("/workouts/300/sets")
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 0
    else:
        assert resp.status_code in (404, 410)
