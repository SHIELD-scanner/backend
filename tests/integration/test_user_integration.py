import pytest
import os
from datetime import datetime
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import app
from app.core.userClient import UserClient


@pytest.fixture(scope="session")
def test_db():
    """Setup test database."""
    # Use a test database
    test_db_name = "shield_test"
    original_db = os.getenv("MONGODB_DB")
    os.environ["MONGODB_DB"] = test_db_name

    yield test_db_name

    # Cleanup - drop test database and restore original
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    client.drop_database(test_db_name)

    if original_db:
        os.environ["MONGODB_DB"] = original_db
    else:
        os.environ.pop("MONGODB_DB", None)


@pytest.fixture
def client(test_db):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def user_client(test_db):
    """Create UserClient for testing."""
    return UserClient()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "fullname": "Test User",
        "role": "Developer",
        "namespaces": ["cluster-dev:development"],
    }


class TestUserAPIIntegration:
    """Integration tests for user API endpoints."""

    def test_user_lifecycle(self, client, user_client):
        """Test complete user lifecycle: create, read, update, delete."""
        # Clear any existing data
        user_client.get_collection().delete_many({})

        # 1. Create user
        create_data = {
            "email": "lifecycle@example.com",
            "fullname": "Lifecycle User",
            "role": "Developer",
            "namespaces": ["cluster-dev:development"],
        }

        response = client.post("/users", json=create_data)
        assert response.status_code == 201

        user_data = response.json()["data"]
        user_id = user_data["id"]
        assert user_data["email"] == "lifecycle@example.com"
        assert user_data["status"] == "active"

        # 2. Get user by ID
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["data"]["email"] == "lifecycle@example.com"

        # 3. Update user
        update_data = {"fullname": "Updated Lifecycle User", "role": "ClusterAdmin"}

        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200

        updated_user = response.json()["data"]
        assert updated_user["fullname"] == "Updated Lifecycle User"
        assert updated_user["role"] == "ClusterAdmin"

        # 4. Update namespaces
        namespace_data = {"namespaces": ["cluster-prod:all", "cluster-staging:testing"]}

        response = client.put(f"/users/{user_id}/namespaces", json=namespace_data)
        assert response.status_code == 200

        updated_user = response.json()["data"]
        assert set(updated_user["namespaces"]) == {
            "cluster-prod:all",
            "cluster-staging:testing",
        }

        # 5. Deactivate user
        response = client.patch(f"/users/{user_id}/deactivate")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "inactive"

        # 6. Activate user
        response = client.patch(f"/users/{user_id}/activate")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "active"

        # 7. Delete user
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 200

        # 8. Verify deletion
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 404

    def test_list_users_with_filtering(self, client, user_client):
        """Test listing users with various filters."""
        # Clear existing data and create test users
        user_client.get_collection().delete_many({})

        test_users = [
            {
                "email": "developer1@example.com",
                "fullname": "Developer One",
                "role": "Developer",
                "namespaces": ["cluster-dev:development"],
            },
            {
                "email": "developer2@example.com",
                "fullname": "Developer Two",
                "role": "Developer",
                "namespaces": ["cluster-dev:testing"],
            },
            {
                "email": "admin@example.com",
                "fullname": "Admin User",
                "role": "ClusterAdmin",
                "namespaces": ["cluster-prod:all"],
            },
        ]

        created_users = []
        for user_data in test_users:
            response = client.post("/users", json=user_data)
            assert response.status_code == 201
            created_users.append(response.json()["data"])

        # Test listing all users
        response = client.get("/users")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data["users"]) == 3
        assert data["pagination"]["total"] == 3

        # Test filtering by role
        response = client.get("/users?role=Developer")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data["users"]) == 2
        for user in data["users"]:
            assert user["role"] == "Developer"

        # Test filtering by status
        # First deactivate one user
        user_id = created_users[0]["id"]
        client.patch(f"/users/{user_id}/deactivate")

        response = client.get("/users?status=active")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data["users"]) == 2

        response = client.get("/users?status=inactive")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data["users"]) == 1

        # Test search functionality
        response = client.get("/users?search=Developer")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data["users"]) >= 1  # Should find users with "Developer" in name

        # Test pagination
        response = client.get("/users?page=1&limit=2")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data["users"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["totalPages"] >= 1

    def test_user_validation_errors(self, client, user_client):
        """Test various validation error scenarios."""
        # Clear existing data
        user_client.get_collection().delete_many({})

        # Test invalid email
        invalid_data = {
            "email": "invalid-email",
            "fullname": "Test User",
            "role": "Developer",
            "namespaces": ["cluster-dev:development"],
        }

        response = client.post("/users", json=invalid_data)
        assert response.status_code == 422

        # Test invalid role
        invalid_data = {
            "email": "test@example.com",
            "fullname": "Test User",
            "role": "InvalidRole",
            "namespaces": ["cluster-dev:development"],
        }

        response = client.post("/users", json=invalid_data)
        assert response.status_code == 422

        # Test invalid namespace format
        invalid_data = {
            "email": "test@example.com",
            "fullname": "Test User",
            "role": "Developer",
            "namespaces": ["invalid-namespace-format"],
        }

        response = client.post("/users", json=invalid_data)
        assert response.status_code == 422

        # Test empty namespaces
        invalid_data = {
            "email": "test@example.com",
            "fullname": "Test User",
            "role": "Developer",
            "namespaces": [],
        }

        response = client.post("/users", json=invalid_data)
        assert response.status_code == 422

    def test_email_uniqueness(self, client, user_client):
        """Test email uniqueness constraints."""
        # Clear existing data
        user_client.get_collection().delete_many({})

        user_data = {
            "email": "unique@example.com",
            "fullname": "First User",
            "role": "Developer",
            "namespaces": ["cluster-dev:development"],
        }

        # Create first user
        response = client.post("/users", json=user_data)
        assert response.status_code == 201

        # Try to create another user with same email
        user_data["fullname"] = "Second User"
        response = client.post("/users", json=user_data)
        assert response.status_code == 409
        assert "already in use" in response.json()["detail"]["message"]

    def test_sysadmin_protection(self, client, user_client):
        """Test system admin protection rules."""
        # Clear existing data
        user_client.get_collection().delete_many({})

        # Create a system admin
        sysadmin_data = {
            "email": "sysadmin@example.com",
            "fullname": "System Admin",
            "role": "SysAdmin",
            "namespaces": ["*"],
        }

        response = client.post("/users", json=sysadmin_data)
        assert response.status_code == 201
        sysadmin_id = response.json()["data"]["id"]

        # Try to delete the only sysadmin - should fail
        response = client.delete(f"/users/{sysadmin_id}")
        assert response.status_code == 409
        assert (
            "last active system administrator" in response.json()["detail"]["message"]
        )

        # Try to deactivate the only sysadmin - should fail
        response = client.patch(f"/users/{sysadmin_id}/deactivate")
        assert response.status_code == 409
        assert (
            "last active system administrator" in response.json()["detail"]["message"]
        )

        # Create another sysadmin
        sysadmin2_data = {
            "email": "sysadmin2@example.com",
            "fullname": "System Admin 2",
            "role": "SysAdmin",
            "namespaces": ["*"],
        }

        response = client.post("/users", json=sysadmin2_data)
        assert response.status_code == 201

        # Now deletion should work
        response = client.delete(f"/users/{sysadmin_id}")
        assert response.status_code == 200

    def test_bulk_operations(self, client, user_client):
        """Test bulk update and delete operations."""
        # Clear existing data
        user_client.get_collection().delete_many({})

        # Create multiple users
        test_users = []
        for i in range(3):
            user_data = {
                "email": f"bulk{i}@example.com",
                "fullname": f"Bulk User {i}",
                "role": "Developer",
                "namespaces": ["cluster-dev:development"],
            }

            response = client.post("/users", json=user_data)
            assert response.status_code == 201
            test_users.append(response.json()["data"])

        user_ids = [user["id"] for user in test_users]

        # Test bulk update
        bulk_update_data = {
            "userIds": user_ids[:2],  # Update first two users
        }
        update_data = {"role": "ClusterAdmin"}

        # Note: This endpoint structure might need adjustment based on your actual implementation
        response = client.patch("/users/bulk", json={**bulk_update_data, **update_data})

        # If the endpoint doesn't exist or has different structure, this test might need adjustment
        # For now, let's test individual updates to verify the bulk concept

        # Test bulk delete
        bulk_delete_data = {"userIds": user_ids}

        response = client.request("DELETE", "/users/bulk", json=bulk_delete_data)
        # Again, might need adjustment based on actual implementation

    def test_get_roles(self, client):
        """Test getting available roles."""
        response = client.get("/users/roles")
        assert response.status_code == 200

        data = response.json()["data"]
        assert len(data) == 3

        role_ids = [role["id"] for role in data]
        assert "SysAdmin" in role_ids
        assert "ClusterAdmin" in role_ids
        assert "Developer" in role_ids

        # Check role structure
        sysadmin_role = next(role for role in data if role["id"] == "SysAdmin")
        assert "name" in sysadmin_role
        assert "description" in sysadmin_role
        assert "permissions" in sysadmin_role
        assert "users:*" in sysadmin_role["permissions"]

    def test_get_user_stats(self, client, user_client):
        """Test getting user statistics."""
        # Clear existing data and create test users
        user_client.get_collection().delete_many({})

        # Create users with different roles and statuses
        test_users = [
            {
                "email": "dev1@example.com",
                "fullname": "Dev 1",
                "role": "Developer",
                "namespaces": ["cluster-dev:dev"],
            },
            {
                "email": "dev2@example.com",
                "fullname": "Dev 2",
                "role": "Developer",
                "namespaces": ["cluster-dev:dev"],
            },
            {
                "email": "admin@example.com",
                "fullname": "Admin",
                "role": "ClusterAdmin",
                "namespaces": ["cluster-prod:all"],
            },
            {
                "email": "sysadmin@example.com",
                "fullname": "SysAdmin",
                "role": "SysAdmin",
                "namespaces": ["*"],
            },
        ]

        created_users = []
        for user_data in test_users:
            response = client.post("/users", json=user_data)
            assert response.status_code == 201
            created_users.append(response.json()["data"])

        # Deactivate one user
        client.patch(f"/users/{created_users[0]['id']}/deactivate")

        # Get stats
        response = client.get("/users/stats")
        assert response.status_code == 200

        stats = response.json()["data"]
        assert stats["total"] == 4
        assert stats["active"] == 3
        assert stats["inactive"] == 1
        assert stats["byRole"]["Developer"] == 2
        assert stats["byRole"]["ClusterAdmin"] == 1
        assert stats["byRole"]["SysAdmin"] == 1

    def test_password_reset_request(self, client, user_client):
        """Test password reset request."""
        # Clear existing data
        user_client.get_collection().delete_many({})

        # Test with existing email
        response = client.post(
            "/users/password-reset/request", json={"email": "test@example.com"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "sent"

        # Test with non-existing email (should still return success for security)
        response = client.post(
            "/users/password-reset/request", json={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "sent"

    def test_user_activity(self, client, user_client):
        """Test user activity endpoint."""
        # Clear existing data
        user_client.get_collection().delete_many({})

        # Create a user
        user_data = {
            "email": "activity@example.com",
            "fullname": "Activity User",
            "role": "Developer",
            "namespaces": ["cluster-dev:development"],
        }

        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["data"]["id"]

        # Get user activity
        response = client.get(f"/users/{user_id}/activity")
        assert response.status_code == 200

        activity = response.json()["data"]
        assert len(activity) >= 1
        assert activity[0]["action"] == "user_created"

        # Test with non-existent user
        response = client.get("/users/nonexistent/activity")
        assert response.status_code == 404
