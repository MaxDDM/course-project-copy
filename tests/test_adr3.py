from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_bulk_create_workouts_unique_and_duplicate_rejection():
    client.delete("/workouts")
    for i in range(1, 101):
        r = client.post(
            "/workouts", json={"id": i, "date": "2025-01-01", "duration_min": 30}
        )
        assert r.status_code == 201
    r_dup = client.post(
        "/workouts", json={"id": 50, "date": "2025-01-01", "duration_min": 30}
    )
    assert r_dup.status_code == 400
