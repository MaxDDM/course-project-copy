from datetime import date

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_workout_rejects_notes_with_union():
    client.delete("/workouts")
    payload = {
        "date": date.today().isoformat(),
        "duration_min": 30,
        "notes": "nice session UNION SELECT password FROM users",
    }
    resp = client.post("/workouts", json=payload)

    assert resp.status_code == 400
    assert "contains disallowed patterns" in resp.json()["detail"]


def test_create_set_rejects_exercise_with_drop():
    client.delete("/workouts")
    workout_payload = {
        "date": date.today().isoformat(),
        "duration_min": 45,
        "notes": "leg day",
    }
    w_resp = client.post("/workouts", json=workout_payload)
    assert w_resp.status_code == 201
    workout_id = w_resp.json()["id"]

    set_payload = {
        "exercise": "bench; DROP TABLE workouts;--",
        "reps": 5,
        "weight_kg": "100",
    }
    s_resp = client.post(f"/workouts/{workout_id}/sets", json=set_payload)

    assert s_resp.status_code == 400
    assert "contains disallowed patterns" in s_resp.json()["detail"]


def test_create_set_rejects_weight_with_exec_and_long_string_limit():
    client.delete("/workouts")
    workout_payload = {
        "date": date.today().isoformat(),
        "duration_min": 20,
        "notes": "ok",
    }
    w_resp = client.post("/workouts", json=workout_payload)
    assert w_resp.status_code == 201
    workout_id = w_resp.json()["id"]

    set_payload_exec = {
        "exercise": "squat",
        "reps": 3,
        "weight_kg": "exec xp_cmdshell('whoami')",
    }
    s_resp1 = client.post(f"/workouts/{workout_id}/sets", json=set_payload_exec)
    assert s_resp1.status_code == 400
    assert "contains disallowed patterns" in s_resp1.json()["detail"]

    long_str = "a" * 1001
    set_payload_long = {"exercise": "deadlift", "reps": 1, "weight_kg": long_str}
    s_resp2 = client.post(f"/workouts/{workout_id}/sets", json=set_payload_long)
    assert s_resp2.status_code == 400
    assert "is too long" in s_resp2.json()["detail"]
