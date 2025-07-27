import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from app.core.databaseClient import DatabaseClient
from app.models.user import Role, User, UserStats


class UserClient(DatabaseClient):

    """Client for managing users in MongoDB."""

    def __init__(self):
        super().__init__()

    def get_collection(self):
        """Get the users collection."""
        return self.client[os.getenv("MONGODB_DB", "shield")]["users"]

    def get_all(
        self,
        role: Optional[str] = None,
        namespace: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[List[User], int]:
        """Get all users with optional filtering and pagination."""
        query = {}

        # Build query filters
        if role and role != "all":
            query["role"] = role

        if status and status != "all":
            query["status"] = status

        if namespace and namespace != "all":
            query["namespaces"] = {"$in": [namespace]}

        if search:
            # Search in email and fullname (case-insensitive)
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"fullname": {"$regex": search, "$options": "i"}},
            ]

        # Get total count for pagination
        total = self.get_collection().count_documents(query)

        # Calculate skip for pagination
        skip = (page - 1) * limit

        # Execute query with pagination
        cursor = (
            self.get_collection()
            .find(query, {"_id": 0})  # Exclude MongoDB _id field
            .sort("createdAt", -1)
            .skip(skip)
            .limit(limit)
        )

        users = []
        for item in cursor:
            users.append(self._format_user(item))

        return users, total

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        item = self.get_collection().find_one({"id": user_id}, {"_id": 0})

        if not item:
            return None

        return self._format_user(item)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        item = self.get_collection().find_one({"email": email.lower()}, {"_id": 0})

        if not item:
            return None

        return self._format_user(item)

    def create(self, user_data: dict) -> User:
        """Create a new user."""
        # Generate unique ID
        user_id = str(ObjectId())

        # Prepare user document
        user_doc = {
            "id": user_id,
            "email": user_data["email"].lower(),
            "fullname": user_data["fullname"],
            "role": user_data["role"],
            "namespaces": user_data["namespaces"],
            "createdAt": datetime.utcnow(),
            "lastLogin": None,
            "status": "active",
            "mfaEnabled": False,
            "oktaIntegration": False,
        }

        # Insert into database
        self.get_collection().insert_one(user_doc.copy())

        return self._format_user(user_doc)

    def update(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update an existing user."""
        # Remove None values and prepare update
        update_fields = {k: v for k, v in update_data.items() if v is not None}

        if not update_fields:
            return self.get_by_id(user_id)

        # Convert email to lowercase if present
        if "email" in update_fields:
            update_fields["email"] = update_fields["email"].lower()

        # Update in database
        result = self.get_collection().update_one(
            {"id": user_id}, {"$set": update_fields}
        )

        if result.matched_count == 0:
            return None

        return self.get_by_id(user_id)

    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        result = self.get_collection().delete_one({"id": user_id})
        return result.deleted_count > 0

    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        result = self.get_collection().update_one(
            {"id": user_id}, {"$set": {"lastLogin": datetime.utcnow()}}
        )
        return result.modified_count > 0

    def activate_user(self, user_id: str) -> Optional[User]:
        """Activate a user."""
        return self.update(user_id, {"status": "active"})

    def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate a user."""
        return self.update(user_id, {"status": "inactive"})

    def update_namespaces(self, user_id: str, namespaces: List[str]) -> Optional[User]:
        """Update user's namespaces."""
        return self.update(user_id, {"namespaces": namespaces})

    def bulk_update(self, user_ids: List[str], update_data: dict) -> int:
        """Bulk update multiple users."""
        # Remove None values
        update_fields = {k: v for k, v in update_data.items() if v is not None}

        if not update_fields:
            return 0

        # Convert email to lowercase if present
        if "email" in update_fields:
            update_fields["email"] = update_fields["email"].lower()

        result = self.get_collection().update_many(
            {"id": {"$in": user_ids}}, {"$set": update_fields}
        )

        return result.modified_count

    def bulk_delete(self, user_ids: List[str]) -> int:
        """Bulk delete multiple users."""
        result = self.get_collection().delete_many({"id": {"$in": user_ids}})
        return result.deleted_count

    def get_stats(self) -> UserStats:
        """Get user statistics."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "active": {
                        "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                    },
                    "inactive": {
                        "$sum": {"$cond": [{"$eq": ["$status", "inactive"]}, 1, 0]}
                    },
                }
            }
        ]

        stats_result = list(self.get_collection().aggregate(pipeline))

        # Get role statistics
        role_pipeline = [{"$group": {"_id": "$role", "count": {"$sum": 1}}}]

        role_stats = list(self.get_collection().aggregate(role_pipeline))
        by_role = {item["_id"]: item["count"] for item in role_stats}

        if stats_result:
            stats = stats_result[0]
            return UserStats(
                total=stats["total"],
                active=stats["active"],
                inactive=stats["inactive"],
                byRole=by_role,
            )
        else:
            return UserStats(total=0, active=0, inactive=0, byRole={})

    def get_user_activity(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get user activity (placeholder for future implementation)."""
        # This would typically query an activity/audit log collection
        # For now, return basic user info as activity
        user = self.get_by_id(user_id)
        if not user:
            return []

        return [
            {
                "timestamp": user.createdAt,
                "action": "user_created",
                "details": f"User {user.fullname} was created",
            }
        ]

    def count_active_sysadmins(self) -> int:
        """Count active system administrators."""
        return self.get_collection().count_documents(
            {"role": "SysAdmin", "status": "active"}
        )

    def email_exists(self, email: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check if email already exists."""
        query = {"email": email.lower()}

        if exclude_user_id:
            query["id"] = {"$ne": exclude_user_id}

        return self.get_collection().count_documents(query) > 0

    def get_roles(self) -> List[Role]:
        """Get all available roles with permissions."""
        # These would typically come from a roles collection or configuration
        # For now, return predefined roles
        return [
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
                description="Cluster-level access and limited user management",
                permissions=[
                    "users:read",
                    "users:manage:assigned",
                    "clusters:assigned",
                    "namespaces:assigned",
                    "vulnerabilities:assigned",
                    "sbom:assigned",
                    "secrets:assigned",
                ],
            ),
            Role(
                id="Developer",
                name="Developer",
                description="Namespace-level read access",
                permissions=[
                    "namespaces:assigned",
                    "vulnerabilities:read:assigned",
                    "sbom:read:assigned",
                    "secrets:read:assigned",
                ],
            ),
        ]

    def _format_user(self, item: dict) -> User:
        """Format database item to User model."""
        return User(
            id=item["id"],
            email=item["email"],
            fullname=item["fullname"],
            role=item["role"],
            namespaces=item["namespaces"],
            createdAt=item["createdAt"],
            lastLogin=item.get("lastLogin"),
            status=item["status"],
            mfaEnabled=item.get("mfaEnabled", False),
            oktaIntegration=item.get("oktaIntegration", False),
        )
