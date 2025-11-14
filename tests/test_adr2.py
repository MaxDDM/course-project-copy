from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_payload_workout_id_must_match_url():
    client.delete("/workouts")
    client.post("/workouts", json={"id": 1, "date": "2025-01-02", "duration_min": 45})

    payload = {
        "id": 10,
        "exercise": "Bench",
        "reps": 8,
        "weight_kg": "80",
    }
    r = client.post("/workouts/99/sets", json=payload)
    assert r.status_code == 404
