import os
import httpx
from jose import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.environ.get("KEYCLOAK_REALM", "SampleApp")
CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "SampleClient")

security = HTTPBearer()

def get_public_key() -> str:
    """Fetch the public key from Keycloak realm to verify JWT tokens."""
    url = f"{KEYCLOAK_URL}/realms/{REALM}"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        public_key = response.json()["public_key"]
        return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
    except Exception as e:
        print(f"Error fetching public key: {e}")
        raise HTTPException(status_code=500, detail="Could not connect to auth server")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifies the Keycloak JWT token."""
    token = credentials.credentials
    if token == "undefined" or "." not in token:
        raise HTTPException(status_code=401, detail="Invalid token format. Ensure you are logged in and the token is a valid JWT.")
        
    public_key = get_public_key()
    
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="account", # Default audience in Keycloak is often "account" or the client ID depending on setup. Let's use options to not require strict audience if we just want basic validation for the sample.
            options={"verify_aud": False} 
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

class RequireRole:
    def __init__(self, role: str):
        self.role = role

    def __call__(self, payload: dict = Security(verify_token)):
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])
        
        if self.role not in roles:
            raise HTTPException(status_code=403, detail=f"Role '{self.role}' is required to access this resource")
        
        return payload

