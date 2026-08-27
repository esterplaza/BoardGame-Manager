import os
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Args:
        password: Plain-text password.

    Returns:
        str: Securely hashed password.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a password hash.

    Args:
        password: Plain-text password.
        hashed_password: Stored password hash.

    Returns:
        bool: True if the password matches the hash, otherwise False.
    """
    return password_hash.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token.

    Returns:
        str: Encoded JWT token.
    """
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
