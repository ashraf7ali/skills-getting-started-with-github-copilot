from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of the initial participants and restore after each test
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    for k, v in original.items():
        activities[k]["participants"] = v[:]


def test_get_activities():
    client = TestClient(app)
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Ensure not already registered
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]

    # Sign up
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert f"Signed up {email}" in res.json().get("message", "")

    # Now participant should be present
    res = client.get("/activities")
    assert email in res.json()[activity]["participants"]

    # Unregister
    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 200
    assert f"Unregistered {email}" in res.json().get("message", "")

    # Confirm removed
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]
