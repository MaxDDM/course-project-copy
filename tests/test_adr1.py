from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def setup_function():
    client.delete("/workouts")
    client.post("/workouts", json={"id": 1, "date": "2025-01-01", "duration_min": 60})


def test_create_set_with_weight_string():
    payload = {
        "id": 1,
        "exercise": "Squat",
        "reps": 5,
        "weight_kg": "100 kg",
    }
    r = client.post("/workouts/1/sets", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert isinstance(body.get("weight_kg"), str)
    assert body["weight_kg"] == "100 kg"
