from abc import ABC, abstractmethod

from app.database.models.models import User


class UserRepository(ABC):
    """Interface for User repository."""
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a user."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Retrieve a user by its username."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by its user id."""
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        """Retrieve all the user from the database."""
        pass
