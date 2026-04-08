
import pytest
import httpx
from fastapi import status
from src.app import app, activities

@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

@pytest.mark.asyncio
async def test_signup_and_unregister():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity_name = "Chess Club"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act: signup
        response_signup = await ac.post(f"/activities/{activity_name}/signup?email={test_email}")
        # Assert: signup
        assert response_signup.status_code == status.HTTP_200_OK
        assert test_email in activities[activity_name]["participants"]

        # Act: duplicate signup
        response_dup = await ac.post(f"/activities/{activity_name}/signup?email={test_email}")
        # Assert: duplicate signup
        assert response_dup.status_code == status.HTTP_400_BAD_REQUEST
        assert response_dup.json()["detail"] == "Student already signed up for this activity"

        # Act: unregister
        response_unreg = await ac.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        # Assert: unregister
        assert response_unreg.status_code == status.HTTP_200_OK
        assert test_email not in activities[activity_name]["participants"]

        # Act: unregister again (should fail)
        response_unreg2 = await ac.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        # Assert: unregister again
        assert response_unreg2.status_code == status.HTTP_400_BAD_REQUEST
        assert response_unreg2.json()["detail"] == "Student is not registered for this activity"
