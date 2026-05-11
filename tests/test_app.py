"""
Comprehensive test suite for the Mergington High School Activities API.
Tests are structured using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for each test."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stage performance, and theatrical productions",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["maya@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:45 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Test: GET /activities returns all activities
        
        Arrange: Create TestClient
        Act: Send GET request to /activities
        Assert: Verify status 200 and all activities are returned
        """
        # Arrange
        expected_activity_count = 9  # We have 9 activities
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == expected_activity_count
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
    
    def test_get_activities_has_correct_structure(self, client):
        """
        Test: GET /activities returns activities with correct structure
        
        Arrange: Create TestClient
        Act: Send GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_details in activities_data.items():
            for field in required_fields:
                assert field in activity_details, f"Missing {field} in {activity_name}"
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_includes_participants(self, client):
        """
        Test: GET /activities includes participants for each activity
        
        Arrange: Create TestClient
        Act: Send GET request to /activities
        Assert: Verify participants are populated
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        chess_club = activities_data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """
        Test: Successfully sign up a new student for an activity
        
        Arrange: Create TestClient and prepare new email
        Act: POST to signup endpoint with new email
        Assert: Verify status 200, message returned, and participant added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email in updated_activity["participants"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """
        Test: Sign up for activity with spaces in name
        
        Arrange: Create TestClient with activity name containing spaces
        Act: POST to signup endpoint with URL-encoded activity name
        Assert: Verify status 200 and participant added
        """
        # Arrange
        activity_name = "Programming Class"
        email = "coder@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email in updated_activity["participants"]
    
    def test_signup_activity_not_found(self, client):
        """
        Test: Attempt to sign up for non-existent activity
        
        Arrange: Create TestClient with non-existent activity name
        Act: POST to signup endpoint
        Assert: Verify status 404 and error detail
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_enrolled(self, client):
        """
        Test: Attempt to sign up when already enrolled
        
        Arrange: Create TestClient with existing participant
        Act: POST to signup endpoint with same email
        Assert: Verify status 400 and error detail
        """
        # Arrange
        activity_name = "Chess Club"
        already_enrolled_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": already_enrolled_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client):
        """
        Test: Multiple different students can sign up for same activity
        
        Arrange: Create TestClient and prepare multiple new emails
        Act: POST to signup endpoint multiple times with different emails
        Assert: Verify all students are added to participants
        """
        # Arrange
        activity_name = "Tennis Club"
        new_students = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Act
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        for email in new_students:
            assert email in updated_activity["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """
        Test: Successfully unregister an enrolled student
        
        Arrange: Create TestClient and identify enrolled participant
        Act: DELETE from unregister endpoint
        Assert: Verify status 200, message returned, and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Verify student is enrolled before unregistering
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email not in updated_activity["participants"]
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """
        Test: Unregister from activity with spaces in name
        
        Arrange: Create TestClient with space-containing activity name
        Act: DELETE from unregister endpoint with URL-encoded activity name
        Assert: Verify status 200 and participant removed
        """
        # Arrange
        activity_name = "Debate Team"
        email = "lucas@mergington.edu"  # Already enrolled
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email not in updated_activity["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """
        Test: Attempt to unregister from non-existent activity
        
        Arrange: Create TestClient with non-existent activity name
        Act: DELETE from unregister endpoint
        Assert: Verify status 404 and error detail
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_enrolled(self, client):
        """
        Test: Attempt to unregister when not enrolled
        
        Arrange: Create TestClient with student not enrolled in activity
        Act: DELETE from unregister endpoint
        Assert: Verify status 400 and error detail
        """
        # Arrange
        activity_name = "Chess Club"
        not_enrolled_email = "notstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": not_enrolled_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not enrolled" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client):
        """
        Test: Unregister then sign up again for same activity
        
        Arrange: Create TestClient with enrolled student
        Act: DELETE to unregister, then POST to sign up again
        Assert: Verify both operations succeed and student re-enrolled
        """
        # Arrange
        activity_name = "Art Studio"
        email = "isabella@mergington.edu"  # Already enrolled
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
        
        # Act - Sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Assert - Verify re-enrolled
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints"""
    
    def test_full_signup_and_unregister_flow(self, client):
        """
        Test: Complete flow of getting activities, signing up, and unregistering
        
        Arrange: Create TestClient
        Act: GET activities, POST signup, DELETE unregister
        Assert: Verify state changes at each step
        """
        # Arrange
        activity_name = "Programming Class"
        email = "complete_test@mergington.edu"
        
        # Act & Assert - Get activities
        response = client.get("/activities")
        assert response.status_code == 200
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Act & Assert - Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Act & Assert - Verify signup
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == initial_count + 1
        assert email in response.json()[activity_name]["participants"]
        
        # Act & Assert - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Act & Assert - Verify unregister
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == initial_count
        assert email not in response.json()[activity_name]["participants"]
