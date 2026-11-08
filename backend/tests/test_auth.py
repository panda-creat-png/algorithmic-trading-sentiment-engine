import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    """Verifies user registration, password hashing, JWT generation, and login."""
    test_email = "quant_trader@quantmind.ai"
    test_password = "SuperSecureTradingPassword123!"

    # 1. Register
    reg_payload = {
        "email": test_email,
        "password": test_password,
        "full_name": "Senior Quant Developer"
    }
    reg_response = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["token_type"] == "bearer"
    assert reg_data["user"]["email"] == test_email

    token = reg_data["access_token"]

    # 2. Duplicate registration should fail
    dup_response = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_response.status_code == 400

    # 3. Login with wrong password
    bad_login = await async_client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 4. Login with correct password
    good_login = await async_client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert good_login.status_code == 200
    login_data = good_login.json()
    assert "access_token" in login_data

    # 5. Get current user profile (/me) with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == test_email
    assert me_data["full_name"] == "Senior Quant Developer"

    # 6. /me without authorization header should fail with 401
    unauth_response = await async_client.get("/api/v1/auth/me")
    assert unauth_response.status_code == 401

