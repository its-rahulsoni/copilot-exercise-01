"""
Comprehensive test suite for the Mergington High School API.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Have activities in the database
        Act: Send GET request to /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_response_structure(self, client, reset_activities):
        """
        Arrange: Have activities in the database
        Act: Send GET request to /activities
        Assert: Verify response structure contains required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant(self, client, reset_activities):
        """
        Arrange: Have an activity with available spots
        Act: Sign up a new participant
        Assert: Verify participant is added to the activity
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
        assert email in activities[activity_name]["participants"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """
        Arrange: Have an activity with available spots
        Act: Sign up a new participant
        Assert: Verify response contains success message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Have a nonexistent activity name
        Act: Attempt to sign up for that activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "NonexistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """
        Arrange: Have a participant already signed up for an activity
        Act: Attempt to sign up the same participant again
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_full_activity_returns_400(self, client, reset_activities):
        """
        Arrange: Have an activity at max capacity
        Act: Attempt to sign up for that full activity
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Tennis Club"
        # Fill up Tennis Club to max (max_participants=10)
        for i in range(10):
            if f"student{i}@mergington.edu" not in activities[activity_name]["participants"]:
                activities[activity_name]["participants"].append(f"student{i}@mergington.edu")
        
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_remove_participant_removes_from_activity(self, client, reset_activities):
        """
        Arrange: Have a participant in an activity
        Act: Remove the participant from the activity
        Assert: Verify participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_participant_returns_success_message(self, client, reset_activities):
        """
        Arrange: Have a participant in an activity
        Act: Remove the participant from the activity
        Assert: Verify response contains success message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Have a nonexistent activity name
        Act: Attempt to remove a participant from that activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "NonexistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        """
        Arrange: Have a participant email not in an activity
        Act: Attempt to remove that participant from the activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]