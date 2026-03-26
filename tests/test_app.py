import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_activity(client):
    r = client.post("/activities/Chess Club/signup", params={"email": "test1@mergington.edu"})
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]
    assert "test1@mergington.edu" in activities["Chess Club"]["participants"]


def test_duplicate_signup_fails(client):
    client.post("/activities/Chess Club/signup", params={"email": "test2@mergington.edu"})
    r = client.post("/activities/Chess Club/signup", params={"email": "test2@mergington.edu"})
    assert r.status_code == 400
    assert "already signed up" in r.json()["detail"]


def test_remove_participant(client):
    client.post("/activities/Chess Club/signup", params={"email": "test3@mergington.edu"})
    r = client.delete("/activities/Chess Club/participants", params={"email": "test3@mergington.edu"})
    assert r.status_code == 200
    assert "Removed" in r.json()["message"]
    assert "test3@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant(client):
    r = client.delete("/activities/Chess Club/participants", params={"email": "nobody@mergington.edu"})
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]
