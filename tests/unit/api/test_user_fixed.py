from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.user import get_user_client
from app.core.userClient import UserClient
from app.main import app
from app.models.user import CreateUserRequest, Role, User, UserStats


@pytest.fixture
def mock_user_client():
    """Create a mock user client."""
    return Mock(spec=UserClient)


@pytest.fixture
def client(mock_user_client):
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

    def test_get_roles(self, mock_user_client, client):
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

        response = client.get("/users/roles")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 3
        role_ids = [role["id"] for role in data["data"]]
        assert "SysAdmin" in role_ids
        assert "ClusterAdmin" in role_ids
        assert "Developer" in role_ids

    def test_get_user_stats(self, mock_user_client, client):
        """Test GET /users/stats endpoint."""
        mock_user_client.get_stats.return_value = UserStats(
            total=10,
            active=8,
            inactive=2,
            byRole={"Developer": 7, "ClusterAdmin": 2, "SysAdmin": 1},
        )

        response = client.get("/users/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 10
        assert data["data"]["active"] == 8
        assert data["data"]["inactive"] == 2

    def test_list_users(self, mock_user_client, client, sample_user):
        """Test GET /users endpoint."""
        mock_user_client.get_all.return_value = ([sample_user], 1)

        response = client.get("/users?page=1&limit=50")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data["data"]
        assert len(data["data"]["users"]) == 1
        assert data["data"]["users"][0]["email"] == "test@example.com"

    def test_create_user(
        self, mock_user_client, client, sample_create_request, sample_user
    ):
        """Test POST /users endpoint."""
        mock_user_client.email_exists.return_value = False
        mock_user_client.create.return_value = sample_user

        response = client.post("/users", json=sample_create_request.model_dump())

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == "test@example.com"
        assert "message" in data

    def test_get_user_by_id(self, mock_user_client, client, sample_user):
        """Test GET /users/{user_id} endpoint."""
        mock_user_client.get_by_id.return_value = sample_user

        response = client.get("/users/user123")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == "test@example.com"

    def test_get_user_by_id_not_found(self, mock_user_client, client):
        """Test GET /users/{user_id} endpoint when user doesn't exist."""
        mock_user_client.get_by_id.return_value = None

        response = client.get("/users/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "Not Found"
