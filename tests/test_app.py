import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset the in-memory activities state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_payload(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in payload
    assert "description" in payload[expected_activity]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    new_email = "zara@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
    response_payload = response.json()

    # Assert
    assert response.status_code == 200
    assert response_payload["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")
    response_payload = response.json()

    # Assert
    assert response.status_code == 400
    assert response_payload["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={participant_email}"
    )
    response_payload = response.json()

    # Assert
    assert response.status_code == 200
    assert response_payload["message"] == f"Unregistered {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "notfound@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={missing_email}"
    )
    response_payload = response.json()

    # Assert
    assert response.status_code == 404
    assert response_payload["detail"] == "Participant not found"


def test_root_redirects_to_index(client):
    # Arrange / Act
    response = client.get("/", allow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"
