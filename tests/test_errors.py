from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_empty_workouts():
    client.delete("/workouts")
    resp = client.get("/workouts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data == []


def test_create_workout():
    client.delete("/workouts")
    payload = {
        "id": 1,
        "date": "2025-01-01",
        "duration_min": 30,
        "notes": "Test workout",
    }
    resp = client.post("/workouts", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert (
        data["id"] == payload["id"]
        and data["date"] == payload["date"]
        and data["duration_min"] == payload["duration_min"]
        and data["notes"] == payload["notes"]
    )


def test_create_set_for_existing_workout():
    client.delete("/workouts")
    workout_payload = {"id": 1, "date": "2025-01-02", "duration_min": 45}
    client.post("/workouts", json=workout_payload)

    set_payload = {
        "id": 10,
        "workout_id": 1,
        "exercise": "Push-ups",
        "reps": 15,
        "weight_kg": None,
    }
    resp = client.post("/workouts/1/sets", json=set_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert (
        data["id"] == set_payload["id"]
        and data["workout_id"] == set_payload["workout_id"]
        and data["exercise"] == set_payload["exercise"]
        and data["reps"] == set_payload["reps"]
    )
