from app.database.models.models import Game, Type, GameType
from app.repositories.game_repository import GameRepository
from app.schemas.schemas import GameCreate, GameUpdate
from app.services.bgg_service import BGGService
from app.exceptions.exceptions import GameAlreadyExistsError, BGGGameNotFoundError


class GameService:
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    def get_game(self, game_id: int) -> Game | None:
        """
        Retrieve a game by its ID.
        Args:
            game_id: ID of the game to retrieve.
        Returns:
            Game | None: The requested game or None if it does not exist.
        """
        game = self.game_repository.get_by_id(game_id)
        return game

    def get_games(self) -> list[Game]:
        """
       Retrieve the list of games stored in the database
       Returns:
           list[Game]: List of Game entities.
       """
        return self.game_repository.get_all()

    def _create_game(self, game_data: GameCreate) -> Game:
        """
        Create a game entity and add it to the current database session.
        The game is not permanently stored until the transaction is comitted.
        Args:
            game_data: Validated game information.

        Returns:
            Game: Newly created game entity.
        """
        game = Game(
            bgg_id=game_data.bgg_id,
            name=game_data.name,
            release_year=game_data.release_year,
            min_players=game_data.min_players,
            max_players=game_data.max_players,
            min_playing_time=game_data.min_playing_time,
            max_playing_time=game_data.max_playing_time,
            min_age=game_data.min_age,
            average_rating=game_data.average_rating,
            box_image=game_data.box_image
        )
        return self.game_repository.create(game)

    def create_game(self, game_data: GameCreate) -> Game:
        """
        Creates the game entity, adds it to the current database session,
        and commits the transaction
        Args:
            game_data: Validated game information.

        Returns:
            Game: Newly created game entity.
        """
        created_game = self._create_game(game_data)
        self.game_repository.commit()
        return created_game

    def update_game(self, game_id: int, game_update: GameUpdate) -> Game | None:
        """
        Update an existing game in the database and commits the transaction.
        Args:
            game_id: Id of a game
            game_update: Game fields to update
        Returns:
            Game | None: Updated Game entity or None if no game with the
            specified game id exists.
        """
        game = self.game_repository.get_by_id(game_id)
        if game is None:
            return None
        update_data = game_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(game, key, value)
        updated_game = self.game_repository.update(game)
        self.game_repository.commit()
        return updated_game

    def delete_game(self, game_id: int) -> Game | None:
        """
        Deletes an existing game in the database and its associated game-type relationships,
        then commits the transaction.
        Args:
            game_id: Id of a game
        Returns:
            Game | None: Deleted Game entity or None if no game with the
            specified game id exists.
        """
        game = self.game_repository.get_by_id(game_id)
        if game is None:
            return None
        self.game_repository.delete_game_types(game_id)
        self.game_repository.delete(game)
        self.game_repository.commit()
        return game

    def get_game_by_bgg_id(self, bgg_id: int) -> Game | None:
        """
        Retrieves a game from de repository using the bgg_id.
        Args:
            bgg_id: Id from the Board Game Geek API
        Returns:
            Game | None: Game entity that matches with bgg_id or None if no
             game with the specified Board Game Geek id was found.
        """
        return self.game_repository.get_by_bgg_id(bgg_id)

    def get_type(self, game_type: str, type_kind: str) -> Type | None:
        """
        Retrieves the game type by its name and kind.
        Args:
            game_type: Name of the game type
            type_kind: Kind of game type (category or mechanic)

        Returns:
            Type | None: Matching game type or None if no Type with the
             specified parameters was found.
        """
        return self.game_repository.get_type(game_type, type_kind)

    def create_type(self, game_type: str, type_kind: str) -> Type:
        """
        Create a new game type and add it to the current database session.
        The new type is not permanently stored until the transaction is
         committed.
        Args:
            game_type: Name of the type.
            type_kind: Kind of type (category or mechanic)
        Returns:
            Type: Type entity that has been created.

        """
        new_type = Type(
            game_type=game_type,
            type_kind=type_kind
        )
        return self.game_repository.create_type(new_type)

    def create_game_type(self, game_id: int, type_id: int) -> GameType:
        """
        Create a game-type association and add it to the current database session.
         The association is not permanently stored until the transaction is
        committed.
        Args:
            game_id: id of the game.
            type_id: id of the type of the game

        Returns:
            GameType: The GameType entity that was created.
        """
        new_game_type = GameType(
            game_id=game_id,
            type_id=type_id
        )
        return self.game_repository.create_game_type(new_game_type)

    def import_game_from_bgg(self, bgg_id: int) -> Game:
        """
        Retrieves the game data from Board Game Geek API and its types,
        adds this information to the database including the relationship
        between game and types and commits the transaction.
        Args:
            bgg_id: Game Id used in the Board Game Geek Api

        Returns:
            Game: Game entity that has been imported form BGG API.
        Raises:
            GameAlreadyExistsError: If a game with the specified
                BoardGameGeek ID already exists.
            BGGGameNotFoundError: If the game cannot be found in the
                BoardGameGeek API.
        """
        existing_game = self.get_game_by_bgg_id(bgg_id)
        if existing_game:
            raise GameAlreadyExistsError
        bgg_service = BGGService()
        game_data = bgg_service.get_game_details(bgg_id)
        if game_data is None:
            raise BGGGameNotFoundError
        new_game = self._create_game(game_data)
        game_types = bgg_service.get_game_types(bgg_id)
        for category in game_types.get("categories"):
            existing_type = self.get_type(category, "category")
            if not existing_type:
                type_category = self.create_type(category, "category")
                self.create_game_type(new_game.id, type_category.id)
            else:
                self.create_game_type(new_game.id, existing_type.id)
        for mechanic in game_types.get("mechanics"):
            existing_type = self.get_type(mechanic, "mechanic")
            if not existing_type:
                type_category = self.create_type(mechanic, "mechanic")
                self.create_game_type(new_game.id, type_category.id)
            else:
                self.create_game_type(new_game.id, existing_type.id)
        self.game_repository.commit()
        return new_game
