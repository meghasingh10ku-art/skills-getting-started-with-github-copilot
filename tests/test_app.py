import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity data before each test."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activity_list(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    expected_url = f"/activities/{encoded_activity}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(expected_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_participant_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Programming Class"
    email = "unknown@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_for_missing_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_missing_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
