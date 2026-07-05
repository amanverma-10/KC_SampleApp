from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import verify_token, get_public_key, RequireRole
import pytest
from fastapi import HTTPException
from jose import jwt

client = TestClient(app)

# Helper to mock token validation for testing endpoint role logic
def mock_verify_token_user():
    return {
        "preferred_username": "test_user",
        "realm_access": {"roles": ["user"]}
    }

def mock_verify_token_admin():
    return {
        "preferred_username": "test_admin",
        "realm_access": {"roles": ["admin"]}
    }

def mock_verify_token_both():
    return {
        "preferred_username": "test_superuser",
        "realm_access": {"roles": ["admin", "user"]}
    }

def mock_verify_token_none():
    return {
        "preferred_username": "test_guest",
        "realm_access": {"roles": []}
    }


def test_public_endpoint():
    response = client.get("/api/public")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello from the public endpoint! No authentication required."

def test_user_endpoint_success():
    app.dependency_overrides[verify_token] = mock_verify_token_user
    response = client.get("/api/user")
    assert response.status_code == 200
    assert "successfully accessed the USER endpoint" in response.json()["message"]
    app.dependency_overrides.clear()

def test_user_endpoint_forbidden():
    app.dependency_overrides[verify_token] = mock_verify_token_admin
    response = client.get("/api/user")
    assert response.status_code == 403
    assert response.json()["detail"] == "Role 'user' is required to access this resource"
    app.dependency_overrides.clear()

def test_admin_endpoint_success():
    app.dependency_overrides[verify_token] = mock_verify_token_admin
    response = client.get("/api/admin")
    assert response.status_code == 200
    assert "successfully accessed the ADMIN endpoint" in response.json()["message"]
    app.dependency_overrides.clear()

def test_admin_endpoint_forbidden():
    app.dependency_overrides[verify_token] = mock_verify_token_user
    response = client.get("/api/admin")
    assert response.status_code == 403
    assert response.json()["detail"] == "Role 'admin' is required to access this resource"
    app.dependency_overrides.clear()


# Unit tests for app.core.auth edge cases
def test_require_role_class():
    require_user = RequireRole("user")
    # Missing realm_access
    with pytest.raises(HTTPException) as excinfo:
        require_user({"preferred_username": "test"})
    assert excinfo.value.status_code == 403

    # Successful call
    assert require_user({"realm_access": {"roles": ["user"]}}) != None

from unittest.mock import patch, MagicMock
from fastapi.security import HTTPAuthorizationCredentials

def test_get_public_key_success():
    with patch("app.core.auth.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"public_key": "MOCK_KEY"}
        mock_get.return_value = mock_response
        
        from app.core.auth import get_public_key
        key = get_public_key()
        assert "MOCK_KEY" in key

def test_get_public_key_failure():
    with patch("app.core.auth.httpx.get") as mock_get:
        mock_get.side_effect = Exception("Network error")
        
        from app.core.auth import get_public_key
        with pytest.raises(HTTPException) as excinfo:
            get_public_key()
        assert excinfo.value.status_code == 500

def test_verify_token_invalid_format():
    from app.core.auth import verify_token
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="undefined")
    with pytest.raises(HTTPException) as excinfo:
        verify_token(cred)
    assert excinfo.value.status_code == 401

def test_verify_token_decode_error():
    from app.core.auth import verify_token
    with patch("app.core.auth.get_public_key", return_value="MOCK_KEY"):
        with patch("app.core.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.JWTError("Invalid token")
            cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="a.b.c")
            with pytest.raises(HTTPException) as excinfo:
                verify_token(cred)
            assert excinfo.value.status_code == 401

def test_verify_token_expired():
    from app.core.auth import verify_token
    with patch("app.core.auth.get_public_key", return_value="MOCK_KEY"):
        with patch("app.core.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Expired")
            cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="a.b.c")
            with pytest.raises(HTTPException) as excinfo:
                verify_token(cred)
            assert excinfo.value.status_code == 401

def test_verify_token_success():
    from app.core.auth import verify_token
    with patch("app.core.auth.get_public_key", return_value="MOCK_KEY"):
        with patch("app.core.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {"user": "test"}
            cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="a.b.c")
            result = verify_token(cred)
            assert result == {"user": "test"}

