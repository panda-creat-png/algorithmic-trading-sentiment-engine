import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import jwt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored SHA256/salt hash."""
    # Split salt and hash if formatted as salt$hash
    if "$" in hashed_password:
        salt, stored_hash = hashed_password.split("$", 1)
        calc_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return calc_hash == stored_hash
    # Direct hash fallback
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password


def get_password_hash(password: str, salt: str = "quantmind_salt_") -> str:
    """Generates a secure hashed password string."""
    calc_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${calc_hash}"


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

