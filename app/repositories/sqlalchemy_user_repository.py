from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.models import User
from app.repositories.user_repository import UserRepository


class SQLAlchemyUserRepository(UserRepository):
    """Repository implementation for managing users with SQLAlchemy."""
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        """
        Add and persist a user in the database.

        Args:
            user: User entity to add.

        Returns:
            User: Newly created user entity.
        """
        self.db.add(user)
        self.db.commit()
        return user

    def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by username.

        Args:
            username: Username to be retrieved

        Returns:
            User | None: Matching user entity, or None if no user exists.

        """
        return (
            self.db.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()
        )

    def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by ID.

        Args:
            user_id: ID of the user to retrieve.

        Returns:
            User | None: User entity, or None if the user does not exist.
        """
        return self.db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

    def get_all(self) -> list[User]:
        """
        Retrieve all the user from the database.

        Returns:
            List[User]: List of users in the database.
        """
        return self.db.execute(select(User)).scalars().all()
