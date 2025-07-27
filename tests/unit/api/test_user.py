from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.user import get_user_client
from app.core.userClient import UserClient
from app.main import app
from app.models.user import (
    CreateUserRequest,
    PasswordResetRequest,
    Role,
    UpdateNamespacesRequest,
    UpdateUserRequest,
    User,
    UserStats,
)


@pytest.fixture
def mock_user_client():
    """Create a mock user client."""
    return Mock(spec=UserClient)


@pytest.fixture
def test_client(mock_user_client):
    """Create test client with dependency override."""
    app.dependency_overrides[get_user_client] = lambda: mock_user_client
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id="user123",
        email="test@example.com",
        fullname="Test User",
        role="Developer",
        namespaces=["cluster-dev:development"],
        createdAt=datetime.now(UTC),
        lastLogin=None,
        status="active",
        mfaEnabled=False,
        oktaIntegration=False,
    )


@pytest.fixture
def sample_create_request():
    """Sample create user request."""
    return CreateUserRequest(
        email="newuser@example.com",
        fullname="New User",
        role="Developer",
        namespaces=["cluster-dev:development"],
    )


class TestUserAPI:

    """Test cases for user API endpoints."""

    def test_get_roles(self, test_client, mock_user_client):
        """Test GET /users/roles endpoint."""
        # Return the actual role structure that the endpoint expects
        mock_user_client.get_roles.return_value = [
            Role(
                id="SysAdmin",
                name="System Administrator",
                description="Full system access and user management",
                permissions=[
                    "users:*",
                    "clusters:*",
                    "namespaces:*",
                    "system:*",
                    "vulnerabilities:*",
                    "sbom:*",
                    "secrets:*",
                ],
            ),
            Role(
                id="ClusterAdmin",
                name="Cluster Administrator",
                description="Cluster-wide access across all namespaces",
                permissions=[
                    "namespaces:*",
                    "vulnerabilities:*",
                    "sbom:*",
                    "secrets:*",
                ],
            ),
            Role(
                id="Developer",
                name="Developer",
                description="Namespace-level access",
                permissions=["namespaces:assigned"],
            ),
        ]

        response = test_client.get("/users/roles")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        # Since the real implementation returns 3 roles, let's test for that
        assert len(data["data"]) == 3
        role_ids = [role["id"] for role in data["data"]]
        assert "SysAdmin" in role_ids
        assert "ClusterAdmin" in role_ids
        assert "Developer" in role_ids

    def test_get_user_stats(self, test_client, mock_user_client):
        """Test GET /users/stats endpoint."""
        mock_user_client.get_stats.return_value = UserStats(
            total=10,
            active=8,
            inactive=2,
            byRole={"Developer": 7, "ClusterAdmin": 2, "SysAdmin": 1},
        )

        response = test_client.get("/users/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 10
        assert data["data"]["active"] == 8
        assert data["data"]["inactive"] == 2

    def test_list_users(self, test_client, mock_user_client, sample_user):
        """Test GET /users endpoint."""
        mock_user_client.get_all.return_value = ([sample_user], 1)

        response = test_client.get("/users?page=1&limit=50")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data["data"]
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0]["email"] == "test@example.com"

    def test_list_users_with_filters(self, test_client, mock_user_client, sample_user):
        """Test GET /users endpoint with filters."""
        mock_user_client.get_all.return_value = ([sample_user], 1)

        response = test_client.get("/users?role=Developer&status=active&search=test")

        assert response.status_code == 200
        mock_user_client.get_all.assert_called_once_with(
            role="Developer",
            namespace=None,
            status="active",
            search="test",
            page=1,
            limit=50,
        )

    def test_get_user_by_id(self, test_client, mock_user_client, sample_user):
        """Test GET /users/{user_id} endpoint."""
        mock_user_client.get_by_id.return_value = sample_user

        response = test_client.get("/users/user123")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "user123"
        assert data["data"]["email"] == "test@example.com"

    def test_get_user_by_id_not_found(self, test_client, mock_user_client):
        """Test GET /users/{user_id} endpoint when user not found."""
        mock_user_client.get_by_id.return_value = None

        response = test_client.get("/users/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "Not Found"

    def test_create_user(self, test_client, mock_user_client, sample_user, sample_create_request):
        """Test POST /users endpoint."""
        mock_user_client.email_exists.return_value = False
        mock_user_client.create.return_value = sample_user

        response = test_client.post("/users", json=sample_create_request.model_dump())

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == "user123"
        assert data["data"]["email"] == "test@example.com"
        assert "message" in data

    def test_create_user_email_conflict(self, test_client, mock_user_client, sample_create_request):
        """Test POST /users endpoint with email conflict."""
        mock_user_client.email_exists.return_value = True

        response = test_client.post("/users", json=sample_create_request.model_dump())

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "Conflict"

    def test_update_user(self, test_client, mock_user_client, sample_user):
        """Test PUT /users/{user_id} endpoint."""
        updated_user = sample_user.model_copy()
        updated_user.fullname = "Updated Name"
        mock_user_client.get_by_id.return_value = sample_user
        mock_user_client.email_exists.return_value = False
        mock_user_client.update.return_value = updated_user

        update_request = UpdateUserRequest(fullname="Updated Name")
        response = test_client.put(
            "/users/user123", json=update_request.model_dump(exclude_unset=True)
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["fullname"] == "Updated Name"
        assert "message" in data

    def test_update_user_not_found(self, test_client, mock_user_client):
        """Test PUT /users/{user_id} endpoint when user not found."""
        mock_user_client.get_by_id.return_value = None

        update_request = UpdateUserRequest(fullname="Updated Name")
        response = test_client.put(
            "/users/nonexistent", json=update_request.model_dump(exclude_unset=True)
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "Not Found"

    def test_delete_user(self, test_client, mock_user_client, sample_user):
        """Test DELETE /users/{user_id} endpoint."""
        mock_user_client.get_by_id.return_value = sample_user
        mock_user_client.delete.return_value = True

        response = test_client.delete("/users/user123")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == "user123"
        assert data["data"]["status"] == "deleted"
        assert "message" in data

    def test_delete_last_sysadmin(self, test_client, mock_user_client):
        """Test DELETE /users/{user_id} endpoint for last sysadmin."""
        sysadmin_user = User(
            id="user123",
            email="admin@example.com",
            fullname="Admin User",
            role="SysAdmin",
            namespaces=["cluster-dev:development"],
            createdAt=datetime.now(UTC),
            status="active",
            mfaEnabled=False,
            oktaIntegration=False,
        )
        mock_user_client.get_by_id.return_value = sysadmin_user
        mock_user_client.count_active_sysadmins.return_value = 1

        response = test_client.delete("/users/user123")

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "Conflict"

    def test_activate_user(self, test_client, mock_user_client, sample_user):
        """Test PATCH /users/{user_id}/activate endpoint."""
        activated_user = sample_user.model_copy()
        activated_user.status = "active"
        mock_user_client.activate_user.return_value = activated_user

        response = test_client.patch("/users/user123/activate")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "active"
        assert "message" in data

    def test_deactivate_user(self, test_client, mock_user_client, sample_user):
        """Test PATCH /users/{user_id}/deactivate endpoint."""
        deactivated_user = sample_user.model_copy()
        deactivated_user.status = "inactive"
        mock_user_client.get_by_id.return_value = sample_user
        mock_user_client.count_active_sysadmins.return_value = 2
        mock_user_client.deactivate_user.return_value = deactivated_user

        response = test_client.patch("/users/user123/deactivate")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "inactive"
        assert "message" in data

    def test_update_user_namespaces(self, test_client, mock_user_client, sample_user):
        """Test PUT /users/{user_id}/namespaces endpoint."""
        updated_user = sample_user.model_copy()
        updated_user.namespaces = ["cluster-dev:production"]
        mock_user_client.update_namespaces.return_value = updated_user

        namespace_request = UpdateNamespacesRequest(namespaces=["cluster-dev:production"])
        response = test_client.put(
            "/users/user123/namespaces", json=namespace_request.model_dump()
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["namespaces"] == ["cluster-dev:production"]
        assert "message" in data

    def test_create_user_validation_error(self, test_client, mock_user_client):
        """Test POST /users endpoint with validation error."""
        # Create an invalid request without required fields
        invalid_request = {"email": "invalid-email"}

        response = test_client.post("/users", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_user_model_namespace_validation(self, sample_user):
        """Test User model namespace validation."""
        # Test valid namespace format
        user_data = sample_user.model_dump()
        user_data["namespaces"] = ["cluster-dev:namespace"]
        user = User(**user_data)
        assert user.namespaces == ["cluster-dev:namespace"]

        # Test multiple namespaces
        user_data["namespaces"] = [
            "cluster-dev:namespace1",
            "cluster-prod:namespace2",
        ]
        user = User(**user_data)
        assert len(user.namespaces) == 2

        # Test that empty namespaces raise validation error
        user_data = sample_user.model_dump()
        user_data["namespaces"] = []
        with pytest.raises(ValueError):  # Should raise validation error
            User(**user_data)

    def test_password_reset_request(self, test_client, mock_user_client):
        """Test POST /users/password-reset/request endpoint."""
        reset_request = PasswordResetRequest(email="test@example.com")
        mock_user_client.get_by_email.return_value = None  # User not found

        response = test_client.post(
            "/users/password-reset/request", json=reset_request.model_dump()
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "sent"
        assert data["data"]["email"] == "test@example.com"
        assert "message" in data

    def test_get_user_activity(self, test_client, mock_user_client, sample_user):
        """Test GET /users/{user_id}/activity endpoint."""
        mock_user_client.get_by_id.return_value = sample_user
        mock_activity = [
            {
                "action": "login",
                "timestamp": datetime.now(UTC),
                "details": {"ip": "192.168.1.1"},
            }
        ]
        mock_user_client.get_user_activity.return_value = mock_activity

        response = test_client.get("/users/user123/activity")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["action"] == "login"
