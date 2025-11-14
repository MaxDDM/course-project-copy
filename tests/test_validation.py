from datetime import date

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_positive_checks_for_create_workout_get_sets_create_set():
    client.delete("/workouts")
    resp = client.post(
        "/workouts",
        json={
            "date": date.today().isoformat(),
            "duration_min": 0,
        },
    )
    assert resp.status_code == 400
    assert "duration_min must be a positive" in resp.json()["detail"]

    resp = client.post(
        "/workouts",
        json={
            "id": 0,
            "date": date.today().isoformat(),
            "duration_min": 30,
        },
    )
    assert resp.status_code == 400
    assert "Workout id must be a positive" in resp.json()["detail"]

    resp = client.post(
        "/workouts",
        json={
            "date": date.today().isoformat(),
            "duration_min": 30,
        },
    )
    assert resp.status_code == 201
    w_id = resp.json()["id"]

    resp = client.get("/workouts/0/sets")
    assert resp.status_code == 400
    assert "workout_id must be a positive" in resp.json()["detail"]

    resp = client.post(
        "/workouts/0/sets",
        json={"exercise": "Squat", "reps": 10},
    )
    assert resp.status_code == 400
    assert "workout_id must be a positive" in resp.json()["detail"]

    resp = client.post(
        f"/workouts/{w_id}/sets",
        json={"exercise": "Bench", "reps": 0},
    )
    assert resp.status_code == 400
    assert "reps must be a positive" in resp.json()["detail"]

    resp = client.post(
        f"/workouts/{w_id}/sets",
        json={"id": -5, "exercise": "Bench", "reps": 8},
    )
    assert resp.status_code == 400
    assert "Set id must be a positive" in resp.json()["detail"]

    resp = client.post(
        f"/workouts/{w_id}/sets",
        json={"exercise": "Bench", "reps": 8, "weight_kg": "60"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0 and body["workout_id"] == w_id


def test_delete_workout_positive_workout_id_check():
    client.delete("/workouts")
    resp = client.delete("/workouts/0")
    assert resp.status_code == 400
    assert "workout_id must be a positive" in resp.json()["detail"]

    resp = client.post(
        "/workouts",
        json={
            "date": date.today().isoformat(),
            "duration_min": 25,
        },
    )
    assert resp.status_code == 201
    w_id = resp.json()["id"]

    resp = client.delete(f"/workouts/{w_id}")

    assert resp.status_code == 204
