from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.db_tables import User

# Read bearer tokens from the Authorization header for FastAPI routes
def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> int:
    # Return error for invalid tokens and users that no longer are in the database
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify the token signature and expiry
        # read the user's ID
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        subject = payload.get("sub")
        user_id = int(subject)
    except (JWTError, TypeError, ValueError) as exc:
        raise credentials_error from exc

    # Confirm the token refers to a current user 
    # (i.e., the user has not been deleted from the database)
    user = db.query(User.id).filter(User.id == user_id).first()
    if user is None:
        raise credentials_error

    # Routes can depend on this function to require an authenticated user
    return user_id
