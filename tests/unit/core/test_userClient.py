import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from app.core.userClient import UserClient
from app.models.user import User, Role, UserStats


class TestUserClient:
    """Test cases for UserClient."""

    def setup_method(self):
        """Setup test data."""
        self.sample_user_data = {
            "id": "user123",
            "email": "test@example.com",
            "fullname": "Test User",
            "role": "Developer",
            "namespaces": ["cluster-dev:development"],
            "createdAt": datetime.utcnow(),
            "lastLogin": None,
            "status": "active",
            "mfaEnabled": False,
            "oktaIntegration": False,
        }

    @patch("app.core.userClient.DatabaseClient.__init__")
    def test_init(self, mock_parent_init):
        """Test UserClient initialization."""
        mock_parent_init.return_value = None
        client = UserClient()
        mock_parent_init.assert_called_once()

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_all_no_filters(self, mock_get_collection):
        """Test get_all without filters."""
        mock_collection = Mock()
        mock_collection.count_documents.return_value = 1
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
            self.sample_user_data
        ]
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        users, total = client.get_all()

        assert total == 1
        assert len(users) == 1
        assert users[0].email == "test@example.com"
        mock_collection.count_documents.assert_called_once_with({})

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_all_with_filters(self, mock_get_collection):
        """Test get_all with various filters."""
        mock_collection = Mock()
        mock_collection.count_documents.return_value = 1
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
            self.sample_user_data
        ]
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        users, total = client.get_all(
            role="Developer",
            namespace="cluster-dev:development",
            status="active",
            search="test",
            page=2,
            limit=25,
        )

        expected_query = {
            "role": "Developer",
            "status": "active",
            "namespaces": {"$in": ["cluster-dev:development"]},
            "$or": [
                {"email": {"$regex": "test", "$options": "i"}},
                {"fullname": {"$regex": "test", "$options": "i"}},
            ],
        }

        mock_collection.count_documents.assert_called_once_with(expected_query)
        mock_collection.find.assert_called_once_with(expected_query, {"_id": 0})

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_by_id(self, mock_get_collection):
        """Test get_by_id method."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = self.sample_user_data
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        user = client.get_by_id("user123")

        assert user is not None
        assert user.id == "user123"
        assert user.email == "test@example.com"
        mock_collection.find_one.assert_called_once_with({"id": "user123"}, {"_id": 0})

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_by_id_not_found(self, mock_get_collection):
        """Test get_by_id when user not found."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        user = client.get_by_id("nonexistent")

        assert user is None

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_by_email(self, mock_get_collection):
        """Test get_by_email method."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = self.sample_user_data
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        user = client.get_by_email("TEST@EXAMPLE.COM")  # Test case insensitive

        assert user is not None
        assert user.email == "test@example.com"
        mock_collection.find_one.assert_called_once_with(
            {"email": "test@example.com"}, {"_id": 0}
        )

    @patch("app.core.userClient.ObjectId")
    @patch("app.core.userClient.UserClient.get_collection")
    def test_create(self, mock_get_collection, mock_object_id):
        """Test create method."""
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection
        mock_object_id.return_value = "generated_id"

        client = UserClient()

        create_data = {
            "email": "NEW@EXAMPLE.COM",  # Test case conversion
            "fullname": "New User",
            "role": "Developer",
            "namespaces": ["cluster-dev:development"],
        }

        user = client.create(create_data)

        assert user.id == "generated_id"
        assert user.email == "new@example.com"  # Should be lowercase
        assert user.fullname == "New User"
        assert user.status == "active"
        assert user.mfaEnabled is False
        assert user.oktaIntegration is False

        # Verify insert was called
        mock_collection.insert_one.assert_called_once()
        inserted_doc = mock_collection.insert_one.call_args[0][0]
        assert inserted_doc["email"] == "new@example.com"

    @patch("app.core.userClient.UserClient.get_collection")
    @patch("app.core.userClient.UserClient.get_by_id")
    def test_update(self, mock_get_by_id, mock_get_collection):
        """Test update method."""
        mock_collection = Mock()
        mock_collection.update_one.return_value.matched_count = 1
        mock_get_collection.return_value = mock_collection

        updated_user = User(**self.sample_user_data)
        updated_user.fullname = "Updated Name"
        mock_get_by_id.return_value = updated_user

        client = UserClient()

        update_data = {
            "fullname": "Updated Name",
            "email": "UPDATED@EXAMPLE.COM",  # Test case conversion
        }

        result = client.update("user123", update_data)

        assert result is not None
        mock_collection.update_one.assert_called_once_with(
            {"id": "user123"},
            {"$set": {"fullname": "Updated Name", "email": "updated@example.com"}},
        )

    @patch("app.core.userClient.UserClient.get_collection")
    def test_update_with_none_values(self, mock_get_collection):
        """Test update method filters out None values."""
        mock_collection = Mock()
        mock_collection.update_one.return_value.matched_count = 1
        mock_get_collection.return_value = mock_collection

        client = UserClient()

        update_data = {
            "fullname": "Updated Name",
            "email": None,  # Should be filtered out
            "role": None,  # Should be filtered out
        }

        with patch.object(
            client, "get_by_id", return_value=User(**self.sample_user_data)
        ):
            client.update("user123", update_data)

        mock_collection.update_one.assert_called_once_with(
            {"id": "user123"}, {"$set": {"fullname": "Updated Name"}}
        )

    @patch("app.core.userClient.UserClient.get_collection")
    def test_delete(self, mock_get_collection):
        """Test delete method."""
        mock_collection = Mock()
        mock_collection.delete_one.return_value.deleted_count = 1
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        result = client.delete("user123")

        assert result is True
        mock_collection.delete_one.assert_called_once_with({"id": "user123"})

    @patch("app.core.userClient.UserClient.get_collection")
    def test_delete_not_found(self, mock_get_collection):
        """Test delete method when user not found."""
        mock_collection = Mock()
        mock_collection.delete_one.return_value.deleted_count = 0
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        result = client.delete("nonexistent")

        assert result is False

    @patch("app.core.userClient.UserClient.get_collection")
    def test_activate_user(self, mock_get_collection):
        """Test activate_user method."""
        client = UserClient()

        with patch.object(client, "update") as mock_update:
            mock_update.return_value = User(**self.sample_user_data)
            result = client.activate_user("user123")

            mock_update.assert_called_once_with("user123", {"status": "active"})
            assert result is not None

    @patch("app.core.userClient.UserClient.get_collection")
    def test_deactivate_user(self, mock_get_collection):
        """Test deactivate_user method."""
        client = UserClient()

        with patch.object(client, "update") as mock_update:
            mock_update.return_value = User(**self.sample_user_data)
            result = client.deactivate_user("user123")

            mock_update.assert_called_once_with("user123", {"status": "inactive"})
            assert result is not None

    @patch("app.core.userClient.UserClient.get_collection")
    def test_update_namespaces(self, mock_get_collection):
        """Test update_namespaces method."""
        client = UserClient()

        new_namespaces = ["cluster-prod:production", "cluster-staging:all"]

        with patch.object(client, "update") as mock_update:
            mock_update.return_value = User(**self.sample_user_data)
            result = client.update_namespaces("user123", new_namespaces)

            mock_update.assert_called_once_with(
                "user123", {"namespaces": new_namespaces}
            )
            assert result is not None

    @patch("app.core.userClient.UserClient.get_collection")
    def test_bulk_update(self, mock_get_collection):
        """Test bulk_update method."""
        mock_collection = Mock()
        mock_collection.update_many.return_value.modified_count = 2
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        user_ids = ["user1", "user2"]
        update_data = {"status": "inactive"}

        result = client.bulk_update(user_ids, update_data)

        assert result == 2
        mock_collection.update_many.assert_called_once_with(
            {"id": {"$in": user_ids}}, {"$set": {"status": "inactive"}}
        )

    @patch("app.core.userClient.UserClient.get_collection")
    def test_bulk_delete(self, mock_get_collection):
        """Test bulk_delete method."""
        mock_collection = Mock()
        mock_collection.delete_many.return_value.deleted_count = 2
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        user_ids = ["user1", "user2"]

        result = client.bulk_delete(user_ids)

        assert result == 2
        mock_collection.delete_many.assert_called_once_with({"id": {"$in": user_ids}})

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_stats(self, mock_get_collection):
        """Test get_stats method."""
        mock_collection = Mock()

        # Mock aggregation results
        stats_pipeline_result = [{"_id": None, "total": 10, "active": 8, "inactive": 2}]

        role_pipeline_result = [
            {"_id": "Developer", "count": 7},
            {"_id": "ClusterAdmin", "count": 2},
            {"_id": "SysAdmin", "count": 1},
        ]

        mock_collection.aggregate.side_effect = [
            stats_pipeline_result,
            role_pipeline_result,
        ]
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        stats = client.get_stats()

        assert stats.total == 10
        assert stats.active == 8
        assert stats.inactive == 2
        assert stats.byRole["Developer"] == 7
        assert stats.byRole["ClusterAdmin"] == 2
        assert stats.byRole["SysAdmin"] == 1

    @patch("app.core.userClient.UserClient.get_collection")
    def test_get_stats_empty_db(self, mock_get_collection):
        """Test get_stats method with empty database."""
        mock_collection = Mock()
        mock_collection.aggregate.side_effect = [[], []]  # Empty results
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        stats = client.get_stats()

        assert stats.total == 0
        assert stats.active == 0
        assert stats.inactive == 0
        assert stats.byRole == {}

    @patch("app.core.userClient.UserClient.get_collection")
    def test_count_active_sysadmins(self, mock_get_collection):
        """Test count_active_sysadmins method."""
        mock_collection = Mock()
        mock_collection.count_documents.return_value = 3
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        count = client.count_active_sysadmins()

        assert count == 3
        mock_collection.count_documents.assert_called_once_with(
            {"role": "SysAdmin", "status": "active"}
        )

    @patch("app.core.userClient.UserClient.get_collection")
    def test_email_exists(self, mock_get_collection):
        """Test email_exists method."""
        mock_collection = Mock()
        mock_collection.count_documents.return_value = 1
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        exists = client.email_exists("TEST@EXAMPLE.COM")  # Test case insensitive

        assert exists is True
        mock_collection.count_documents.assert_called_once_with(
            {"email": "test@example.com"}
        )

    @patch("app.core.userClient.UserClient.get_collection")
    def test_email_exists_with_exclusion(self, mock_get_collection):
        """Test email_exists method with user exclusion."""
        mock_collection = Mock()
        mock_collection.count_documents.return_value = 0
        mock_get_collection.return_value = mock_collection

        client = UserClient()
        exists = client.email_exists("test@example.com", exclude_user_id="user123")

        assert exists is False
        mock_collection.count_documents.assert_called_once_with(
            {"email": "test@example.com", "id": {"$ne": "user123"}}
        )

    def test_get_roles(self):
        """Test get_roles method."""
        client = UserClient()
        roles = client.get_roles()

        assert len(roles) == 3
        role_ids = [role.id for role in roles]
        assert "SysAdmin" in role_ids
        assert "ClusterAdmin" in role_ids
        assert "Developer" in role_ids

        # Check SysAdmin role has full permissions
        sysadmin_role = next(role for role in roles if role.id == "SysAdmin")
        assert "users:*" in sysadmin_role.permissions
        assert "clusters:*" in sysadmin_role.permissions

    @patch("app.core.userClient.UserClient.get_by_id")
    def test_get_user_activity(self, mock_get_by_id):
        """Test get_user_activity method."""
        mock_get_by_id.return_value = User(**self.sample_user_data)

        client = UserClient()
        activity = client.get_user_activity("user123")

        assert len(activity) == 1
        assert activity[0]["action"] == "user_created"
        assert "Test User" in activity[0]["details"]

    @patch("app.core.userClient.UserClient.get_by_id")
    def test_get_user_activity_user_not_found(self, mock_get_by_id):
        """Test get_user_activity when user not found."""
        mock_get_by_id.return_value = None

        client = UserClient()
        activity = client.get_user_activity("nonexistent")

        assert activity == []

    def test_format_user(self):
        """Test _format_user method."""
        client = UserClient()
        user = client._format_user(self.sample_user_data)

        assert isinstance(user, User)
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.role == "Developer"
        assert user.status == "active"
