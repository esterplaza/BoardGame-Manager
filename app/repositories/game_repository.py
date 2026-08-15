from abc import ABC, abstractmethod

from app.database.models.models import Game, Type, GameType


class GameRepository(ABC):
    """Interface for Game repository."""
    @abstractmethod
    def get_by_id(self, game_id: int) -> Game | None:
        """Retrieve a game by its ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Game]:
        """Retrieve all games."""
        pass

    @abstractmethod
    def create(self, game: Game) -> Game:
        """Store a new game."""
        pass

    @abstractmethod
    def add(self, game: Game) -> Game:
        """Add a new game."""
        pass

    @abstractmethod
    def update(self, game: Game) -> Game:
        """Update an existing game."""
        pass

    @abstractmethod
    def delete(self, game: Game) -> None:
        """Delete a game."""
        pass

    @abstractmethod
    def delete_game_types(self, game_id: int):
        """Delete a game types."""
        pass

    @abstractmethod
    def get_by_bgg_id(self, bgg_id: int) -> Game | None:
        """Retrieve a game by its ID."""
        pass

    @abstractmethod
    def get_type(self, game_type: str, type_kind: str) -> Type | None:
        """Retrieve a type by its type and type kind."""
        pass

    @abstractmethod
    def create_type(self, new_type: Type) -> Type:
        """Store a new type."""
        pass

    @abstractmethod
    def create_game_type(self, new_game_type: GameType) -> GameType:
        """Store a new game type."""
        pass

    @abstractmethod
    def commit(self):
        """commits to database"""
        pass

    @abstractmethod
    def rollback(self):
        """
        Roll back the current database transaction.
        Reverts all uncommitted changes in the current session.
        """
        pass
