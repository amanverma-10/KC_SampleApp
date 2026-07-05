from fastapi import APIRouter, Depends
from app.core.auth import RequireRole

router = APIRouter()

@router.get("/public")
def public_endpoint():
    """An endpoint that does not require authentication."""
    return {"message": "Hello from the public endpoint! No authentication required."}

@router.get("/user")
def user_endpoint(user_payload: dict = Depends(RequireRole("user"))):
    """An endpoint that requires the 'user' role."""
    username = user_payload.get("preferred_username", "Unknown User")
    return {
        "message": f"Hello {username}, you have successfully accessed the USER endpoint!",
        "user_data": user_payload
    }

@router.get("/admin")
def admin_endpoint(user_payload: dict = Depends(RequireRole("admin"))):
    """An endpoint that requires the 'admin' role."""
    username = user_payload.get("preferred_username", "Unknown User")
    return {
        "message": f"Hello {username}, you have successfully accessed the ADMIN endpoint!",
        "user_data": user_payload
    }
