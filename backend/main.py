from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from keycloak_utils import verify_token, RequireRole

app = FastAPI(title="Sample Application API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/public")
def public_endpoint():
    """An endpoint that does not require authentication."""
    return {"message": "Hello from the public endpoint! No authentication required."}

@app.get("/api/user")
def user_endpoint(user_payload: dict = Depends(RequireRole("user"))):
    """An endpoint that requires the 'user' role."""
    username = user_payload.get("preferred_username", "Unknown User")
    return {
        "message": f"Hello {username}, you have successfully accessed the USER endpoint!",
        "user_data": user_payload
    }

@app.get("/api/admin")
def admin_endpoint(user_payload: dict = Depends(RequireRole("admin"))):
    """An endpoint that requires the 'admin' role."""
    username = user_payload.get("preferred_username", "Unknown User")
    return {
        "message": f"Hello {username}, you have successfully accessed the ADMIN endpoint!",
        "user_data": user_payload
    }
