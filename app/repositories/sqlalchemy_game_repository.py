from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.models import Game, GameType, Type
from app.repositories.game_repository import GameRepository


class SQLAlchemyGameRepository(GameRepository):
    """Repository implementation for managing games with SQLAlchemy."""
    def __init__(self, db: Session):
        self.db = db

    def rollback(self):
        """
        Roll back the current database transaction.
        Reverts all uncommitted changes in the current session.
        """
        self.db.rollback()

    def commit(self):
        """commit"""
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_by_id(self, game_id: int) -> Game | None:
        """
        Retrieves the game information from database by looking for the game id.
        Args:
            game_id: Id of the game

        Returns:
            Game | None: The requested game or None if it was not found
        """
        return (
            self.db.execute(
                select(Game).where(Game.id == game_id)
            ).scalar_one_or_none()
        )

    def create(self, game: Game) -> Game:
        """
        Add and persist a game in the database.
        Args:
            game: game data to be added
        Returns:
            Game: the added game
        """
        self.db.add(game)
        self.commit()
        self.db.refresh(game)
        return game

    def add(self, game: Game) -> Game:
        """
        Adds the game to the database.
        Args:
            game: game data to be added
        Returns:
            Game: the added game
        """
        self.db.add(game)
        self.db.flush()
        self.db.refresh(game)
        return game

    def get_all(self) -> list[Game]:
        """
        Retrieve all games existing in the database.
        Returns:
            list[Game]: list of games
        """
        games = self.db.execute(select(Game)).scalars().all()
        return games

    def update(self, game: Game) -> Game:
        """
        Refresh an updated game entity in database after persistence.
        Args:
            game: game to update
        Returns:
            Game: that has been updated
        """
        self.commit()
        self.db.refresh(game)
        return game

    def delete(self, game: Game) -> Game:
        """
        Remove a game entity from the current database session.
        Args:
            game: game to delete
        Returns:
            Game: game entity that has been deleted.
        """
        self.db.delete(game)
        self.commit()
        return game

    def delete_game_types(self, game_id: int) -> list[GameType]:
        """
        Remove all game-type associations for a given game.
        Args:
            game_id: ID of the game whose type associations should be removed.

        Returns:
            list[GameType]: The deleted game-type associations.
        """
        game_types = self.db.execute(
            select(GameType).where(GameType.game_id == game_id)
        ).scalars().all()
        for game_type in game_types:
            self.db.delete(game_type)
        self.commit()
        return game_types

    def get_by_bgg_id(self, bgg_id: int) -> Game | None:
        """
        Retrieve a game from the database using its BoardGameGeek ID..
        Args:
            bgg_id: ID from board Game Geek Api
        Returns:
            Game| None: Game entity founded or None if no game was found.
        """
        existing_game = self.db.execute(
            select(Game).where(Game.bgg_id == bgg_id)).scalar_one_or_none()
        return existing_game

    def get_type(self, game_type: str, type_kind: str) -> Type | None:
        """
        Retrieve a type from the database using the game type and the type kind
        Args:
            game_type: The game type.
            type_kind: The kind of type of game, category or mechanic.
        Returns:
            Type | None: Type entity founded or None if no type was found.
        """
        existing_type = self.db.execute(
            select(Type).where(
                Type.type_kind == type_kind,
                Type.game_type == game_type
            )
        ).scalars().first()
        return existing_type

    def create_type(self, new_type: Type) -> Type:
        """
        Add type to the database.
        Args:
            new_type: Type entity to add to the database.
        Returns:
            Type: Type entity that has been added.
        """
        self.db.add(new_type)
        self.commit()
        return new_type

    def create_game_type(self, new_game_type: GameType) -> GameType:
        """
        Add game type to the database.
        Args:
            new_game_type: GameType entity to add to the database.
        Returns:
            GameType: GameType entity that has been added.
        """
        self.db.add(new_game_type)
        self.commit()
        return new_game_type
