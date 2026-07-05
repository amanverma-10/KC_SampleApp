from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from keycloak_utils import verify_token

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

@app.get("/api/private")
def private_endpoint(user_payload: dict = Depends(verify_token)):
    """An endpoint that requires a valid Keycloak JWT token."""
    username = user_payload.get("preferred_username", "Unknown User")
    return {
        "message": f"Hello {user_payload.get('preferred_username', 'Unknown User')}, you have successfully accessed a protected endpoint!",
        "user_data": user_payload
    }
