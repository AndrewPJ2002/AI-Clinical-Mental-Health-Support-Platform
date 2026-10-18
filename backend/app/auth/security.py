# building authentification

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password before storing it in the database."""
    password_bytes = password.encode("utf-8")

    # bcrypt supports a maximum of 72 password bytes.
    if not password_bytes or len(password_bytes) > 72:
        raise ValueError(
            "Password must be between 1 and 72 UTF-8 bytes."
        )

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against its stored bcrypt hash."""
    password_bytes = password.encode("utf-8")

    if not password_bytes or len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    """Create a signed token identifying a user."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.access_token_expire
        ),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> int | None:
    """Return the user ID from a valid token, or None."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit():
            return None

        user_id = int(subject)
        return user_id if user_id > 0 else None

    except (JWTError, ValueError, TypeError):
        return None
