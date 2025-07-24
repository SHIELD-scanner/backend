import sentry_sdk
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/debug")
def sentry_debug_check():
    """Test endpoint to trigger a Sentry exception"""
    try:
        # This will definitely trigger an exception
        _ = 1 / 0  # Assign to underscore to indicate intentionally unused variable
        return {"status": "ok", "message": "This should never be reached"}
    except ZeroDivisionError as e:
        # Manually capture the exception to ensure it's sent to Sentry
        sentry_sdk.capture_exception(e)
        # Re-raise the exception so it's also handled by FastAPI
        raise HTTPException(
            status_code=500, detail="Division by zero error - check Sentry!"
        ) from e


@router.get("/test-sentry")
def test_sentry():
    """Test Sentry integration without raising an HTTP exception"""
    # Send a test message to Sentry
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("test", "manual-trigger")
        scope.set_level("info")
        sentry_sdk.capture_message("Manual Sentry test from API endpoint")

    # Also trigger an exception
    try:
        raise ValueError("This is a test exception for Sentry")
    except ValueError as e:
        sentry_sdk.capture_exception(e)
        return {"status": "exception_sent", "message": "Test exception sent to Sentry"}
