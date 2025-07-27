from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class Role(BaseModel):
    """Role model with permissions."""

    id: str
    name: str
    description: str
    permissions: List[str]


class User(BaseModel):
    """User model for SHIELD Scanner platform."""

    id: str
    email: EmailStr
    fullname: str = Field(..., min_length=2, max_length=100)
    role: str
    namespaces: List[str] = Field(..., min_length=1)
    createdAt: datetime
    lastLogin: Optional[datetime] = None
    status: str = Field(default="active", pattern="^(active|inactive)$")
    mfaEnabled: bool = False
    oktaIntegration: bool = False

    @field_validator("namespaces")
    @classmethod
    def validate_namespaces(cls, v):
        """Validate namespace format."""
        if not v:
            raise ValueError("At least one namespace must be specified")

        for namespace in v:
            if namespace == "*":
                # Full system access - valid
                continue
            elif ":" in namespace:
                # Check cluster:namespace or cluster:all format
                parts = namespace.split(":")
                if len(parts) != 2:
                    raise ValueError(
                        f'Invalid namespace format: {namespace}. Use "clustername:namespace" or "clustername:all"'
                    )
                cluster, ns = parts
                if not cluster or not ns:
                    raise ValueError(
                        f"Invalid namespace format: {namespace}. Cluster and namespace cannot be empty"
                    )
            else:
                raise ValueError(
                    f'Invalid namespace format: {namespace}. Use "*", "clustername:namespace", or "clustername:all"'
                )

        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate role exists in predefined roles."""
        valid_roles = ["SysAdmin", "ClusterAdmin", "Developer"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

    model_config = ConfigDict(
        # Example of valid user data
        json_schema_extra={
            "example": {
                "id": "user123",
                "email": "user@example.com",
                "fullname": "John Doe",
                "role": "Developer",
                "namespaces": ["cluster-dev:development", "cluster-staging:testing"],
                "createdAt": "2024-01-15T10:30:00Z",
                "lastLogin": "2024-01-20T15:45:00Z",
                "status": "active",
                "mfaEnabled": False,
                "oktaIntegration": False,
            }
        }
    )


class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""

    email: EmailStr
    fullname: str = Field(..., min_length=2, max_length=100)
    role: str
    namespaces: List[str] = Field(..., min_length=1)

    @field_validator("namespaces")
    @classmethod
    def validate_namespaces(cls, v):
        """Validate namespace format."""
        return User.validate_namespaces(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate role exists in predefined roles."""
        return User.validate_role(v)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "fullname": "Jane Smith",
                "role": "Developer",
                "namespaces": ["cluster-dev:development"],
            }
        }
    )


class UpdateUserRequest(BaseModel):
    """Request model for updating an existing user."""

    email: Optional[EmailStr] = None
    fullname: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = None
    namespaces: Optional[List[str]] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    mfaEnabled: Optional[bool] = None
    oktaIntegration: Optional[bool] = None

    @field_validator("namespaces")
    @classmethod
    def validate_namespaces(cls, v):
        """Validate namespace format."""
        if v is not None:
            return User.validate_namespaces(v)
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate role exists in predefined roles."""
        if v is not None:
            return User.validate_role(v)
        return v


class UpdateNamespacesRequest(BaseModel):
    """Request model for updating user namespaces."""

    namespaces: List[str] = Field(..., min_length=1)

    @field_validator("namespaces")
    @classmethod
    def validate_namespaces(cls, v):
        """Validate namespace format."""
        return User.validate_namespaces(v)


class UserStats(BaseModel):
    """User statistics model."""

    total: int
    active: int
    inactive: int
    byRole: dict


class BulkUserRequest(BaseModel):
    """Request model for bulk operations."""

    userIds: List[str] = Field(..., min_length=1)


class PasswordResetRequest(BaseModel):
    """Request model for password reset."""

    email: EmailStr
