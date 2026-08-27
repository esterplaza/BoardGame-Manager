from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.auth.security import SECRET_KEY, ALGORITHM
from app.database.database import get_db
from app.database.models.models import User
from app.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieves the currently authenticated user from the JWT token.
    Args:
        token: JWT access token provided in the Authorization header.
        db: Database session.
    Returns:
        User: The authenticated user.
    Raises:
        HTTPException: If the token is invalid, does not contain a user ID,
            or the user does not exist in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    repository = SQLAlchemyUserRepository(db)
    user = repository.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify that the current user has the admin role.
    Args:
        current_user: Authenticated user.
    Returns:
        current_user: The authenticated user with role admin.
    Raises:
        HTTPException: If the current user does not have the admin role.
    """
    if current_user.role == "admin":
        return current_user
    raise HTTPException(
        status_code=403,
        detail="Only Admin role is authorized to do this operation."
    )
