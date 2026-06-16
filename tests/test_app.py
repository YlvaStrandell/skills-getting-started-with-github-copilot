"""Tests for the Mergington High School API.

Uses the Arrange-Act-Assert pattern for clarity and maintainability.
"""

import copy

import pytest
from fastapi.testclient import TestClient
from src import app as app_module

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before each test."""
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield


@pytest.fixture
def client():
    """Create a FastAPI TestClient for the app."""
    return TestClient(app_module.app)


def test_get_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_success(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activity_response = client.get("/activities")
    activity_data = activity_response.json()[activity_name]
    assert email in activity_data["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_delete_participant_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activity_response = client.get("/activities")
    activity_data = activity_response.json()[activity_name]
    assert email not in activity_data["participants"]


def test_delete_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
