from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.core.userClient import UserClient
from app.models.user import (
    User,
    Role,
    CreateUserRequest,
    UpdateUserRequest,
    UpdateNamespacesRequest,
    UserStats,
    BulkUserRequest,
    PasswordResetRequest,
)

router = APIRouter()


def get_user_client() -> UserClient:
    """Dependency to get UserClient instance."""
    return UserClient()


# Response helper functions
def success_response(data: Any, message: str = None) -> Dict[str, Any]:
    """Create a successful response."""
    response = {"data": data}
    if message:
        response["message"] = message
    return response


def error_response(
    error_type: str, message: str, status_code: int, details: Any = None
) -> Dict[str, Any]:
    """Create an error response."""
    response = {"error": error_type, "message": message, "statusCode": status_code}
    if details:
        response["details"] = details
    return response


@router.get("/roles", response_model=Dict[str, Any])
def get_roles(db: UserClient = Depends(get_user_client)):
    """Get all available user roles with their permissions."""
    try:
        roles = db.get_roles()
        return success_response(roles)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to fetch roles", 500
            ),
        )


@router.get("/stats", response_model=Dict[str, Any])
def get_user_stats(db: UserClient = Depends(get_user_client)):
    """Get user statistics."""
    try:
        stats = db.get_stats()
        return success_response(stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to fetch user statistics", 500
            ),
        )


@router.get("/", response_model=Dict[str, Any])
def list_users(
    role: Optional[str] = Query(None, description="Filter by role ID"),
    namespace: Optional[str] = Query(None, description="Filter by namespace access"),
    status: Optional[str] = Query(
        None, description="Filter by status (active, inactive)"
    ),
    search: Optional[str] = Query(None, description="Search by email or fullname"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: UserClient = Depends(get_user_client),
):
    """List all users with optional filtering and pagination."""
    try:
        users, total = db.get_all(
            role=role,
            namespace=namespace,
            status=status,
            search=search,
            page=page,
            limit=limit,
        )

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit  # Ceiling division

        return success_response(
            {
                "users": [user.model_dump() for user in users],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": total_pages,
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to fetch users", 500
            ),
        )


@router.get("/{user_id}", response_model=Dict[str, Any])
def get_user_by_id(user_id: str, db: UserClient = Depends(get_user_client)):
    """Get user by ID."""
    try:
        user = db.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        return success_response(user.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response("Internal Server Error", "Failed to fetch user", 500),
        )


@router.post("/", status_code=201)
def create_user(
    user_request: CreateUserRequest, db: UserClient = Depends(get_user_client)
):
    """Create a new user."""
    try:
        # Check if email already exists
        if db.email_exists(user_request.email):
            raise HTTPException(
                status_code=409,
                detail=error_response("Conflict", "Email address already in use", 409),
            )

        # Create user
        user = db.create(user_request.model_dump())

        return success_response(user.model_dump(), "User created successfully")

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=error_response("Validation Error", str(e), 400)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to create user", 500
            ),
        )


@router.put("/{user_id}", response_model=Dict[str, Any])
def update_user(
    user_id: str,
    user_request: UpdateUserRequest,
    db: UserClient = Depends(get_user_client),
):
    """Update an existing user."""
    try:
        # Check if user exists
        existing_user = db.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        # Check email conflict if email is being updated
        if user_request.email and user_request.email != existing_user.email:
            if db.email_exists(user_request.email, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=409,
                    detail=error_response(
                        "Conflict", "Email address already in use", 409
                    ),
                )

        # Update user
        update_data = user_request.model_dump(exclude_unset=True)
        updated_user = db.update(user_id, update_data)

        return success_response(updated_user.model_dump(), "User updated successfully")

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=error_response("Validation Error", str(e), 400)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to update user", 500
            ),
        )


@router.delete("/{user_id}", response_model=Dict[str, Any])
def delete_user(user_id: str, db: UserClient = Depends(get_user_client)):
    """Delete a user."""
    try:
        # Check if user exists
        user = db.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        # Check if user can be deleted (business rules)
        if user.role == "SysAdmin":
            active_sysadmin_count = db.count_active_sysadmins()
            if active_sysadmin_count <= 1 and user.status == "active":
                raise HTTPException(
                    status_code=409,
                    detail=error_response(
                        "Conflict",
                        "Cannot delete the last active system administrator",
                        409,
                    ),
                )

        # Delete user
        success = db.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    "Internal Server Error", "Failed to delete user", 500
                ),
            )

        return success_response(
            {"id": user_id, "status": "deleted"}, "User deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to delete user", 500
            ),
        )


@router.patch("/{user_id}/activate", response_model=Dict[str, Any])
def activate_user(user_id: str, db: UserClient = Depends(get_user_client)):
    """Activate a user."""
    try:
        user = db.activate_user(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        return success_response(user.model_dump(), "User activated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to activate user", 500
            ),
        )


@router.patch("/{user_id}/deactivate", response_model=Dict[str, Any])
def deactivate_user(user_id: str, db: UserClient = Depends(get_user_client)):
    """Deactivate a user."""
    try:
        # Check if user exists and get current data
        current_user = db.get_by_id(user_id)
        if not current_user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        # Check if user can be deactivated (business rules)
        if current_user.role == "SysAdmin":
            active_sysadmin_count = db.count_active_sysadmins()
            if active_sysadmin_count <= 1 and current_user.status == "active":
                raise HTTPException(
                    status_code=409,
                    detail=error_response(
                        "Conflict",
                        "Cannot deactivate the last active system administrator",
                        409,
                    ),
                )

        user = db.deactivate_user(user_id)

        return success_response(user.model_dump(), "User deactivated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to deactivate user", 500
            ),
        )


@router.put("/{user_id}/namespaces", response_model=Dict[str, Any])
def update_user_namespaces(
    user_id: str,
    namespace_request: UpdateNamespacesRequest,
    db: UserClient = Depends(get_user_client),
):
    """Update user's namespaces."""
    try:
        user = db.update_namespaces(user_id, namespace_request.namespaces)

        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        return success_response(
            user.model_dump(), "User namespaces updated successfully"
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=error_response("Validation Error", str(e), 400)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to update user namespaces", 500
            ),
        )


@router.patch("/bulk", response_model=Dict[str, Dict[str, int]])
def bulk_update_users(
    bulk_request: BulkUserRequest,
    user_updates: UpdateUserRequest,
    db: UserClient = Depends(get_user_client),
):
    """Bulk update multiple users."""
    try:
        update_data = user_updates.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail=error_response("Bad Request", "No update data provided", 400),
            )

        updated_count = db.bulk_update(bulk_request.userIds, update_data)

        return success_response(
            {"updated": updated_count, "requested": len(bulk_request.userIds)},
            f"Bulk update completed: {updated_count} users updated",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to perform bulk update", 500
            ),
        )


@router.delete("/bulk", response_model=Dict[str, Dict[str, int]])
def bulk_delete_users(
    bulk_request: BulkUserRequest, db: UserClient = Depends(get_user_client)
):
    """Bulk delete multiple users."""
    try:
        # Check if any of the users are SysAdmins that would leave the system without admins
        sysadmin_count = db.count_active_sysadmins()

        # Count how many active sysadmins are in the deletion list
        sysadmins_to_delete = 0
        for user_id in bulk_request.userIds:
            user = db.get_by_id(user_id)
            if user and user.role == "SysAdmin" and user.status == "active":
                sysadmins_to_delete += 1

        if sysadmin_count - sysadmins_to_delete < 1:
            raise HTTPException(
                status_code=409,
                detail=error_response(
                    "Conflict",
                    "Cannot delete all system administrators. At least one must remain active.",
                    409,
                ),
            )

        deleted_count = db.bulk_delete(bulk_request.userIds)

        return success_response(
            {"deleted": deleted_count, "requested": len(bulk_request.userIds)},
            f"Bulk delete completed: {deleted_count} users deleted",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to perform bulk delete", 500
            ),
        )


@router.get("/{user_id}/activity", response_model=Dict[str, List[Dict[str, Any]]])
def get_user_activity(
    user_id: str,
    limit: int = Query(
        50, ge=1, le=100, description="Number of activity records to return"
    ),
    db: UserClient = Depends(get_user_client),
):
    """Get user activity logs."""
    try:
        # Check if user exists
        user = db.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response("Not Found", "User not found", 404),
            )

        activity = db.get_user_activity(user_id, limit)

        return success_response(activity)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error_response(
                "Internal Server Error", "Failed to fetch user activity", 500
            ),
        )


@router.post("/password-reset/request", response_model=Dict[str, Any])
def request_password_reset(
    reset_request: PasswordResetRequest, db: UserClient = Depends(get_user_client)
):
    """Request password reset for a user."""
    try:
        # Check if user exists
        user = db.get_by_email(reset_request.email)

        # Always return success for security (don't reveal if email exists)
        # In a real implementation, this would send an email with reset instructions

        return success_response(
            {"status": "sent", "email": reset_request.email},
            "Password reset instructions have been sent to the email address",
        )

    except Exception as e:
        # Always return success for security
        return success_response(
            {"status": "sent", "email": reset_request.email},
            "Password reset instructions have been sent to the email address",
        )
