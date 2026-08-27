from app.database.models.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserCreate
from app.auth.security import hash_password
from app.exceptions.exceptions import UserAlreadyExistsError
from app.auth.security import verify_password


class UserService:
    """Provides business logic for managing users."""
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with a securely hashed password.

        Args:
            user_data: Validated user registration data.

        Returns:
            User: Newly created user entity.
        """
        existing_user = self.user_repository.get_by_username(
            user_data.username
        )
        if existing_user:
            raise UserAlreadyExistsError()
        hashed_password = hash_password(user_data.hashed_password)
        if self.user_repository.get_all():
            role = "member"
        else:
            role = "admin"
        user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            role=role
        )
        return self.user_repository.create(user)

    def authenticate_user(self, username: str, password: str) -> User | None:
        """
        Authenticate a user using their username and password.
        Args:
            username: Username provided during login.
            password: Password provided during login.

        Returns:
            User | None: Authenticated user, or None if the credentials are invalid.
        """
        user = self.user_repository.get_by_username(username)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
