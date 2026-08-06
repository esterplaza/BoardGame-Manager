from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repositories.sqlalchemy_game_repository import SQLAlchemyGameRepository
from app.services.bgg_service import BGGService
from app.services.game_service import GameService
from app.database.database import SessionLocal, engine
from app.exceptions.exceptions import GameAlreadyExistsError, BGGGameNotFoundError
from app.database.models.models import Game, Base
from app.schemas.schemas import GameCreate, GameUpdate, BGGSearchResult, GameResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    """
    Create a database session and close after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_game_service(db: Session = Depends(get_db)) -> GameService:
    repository = SQLAlchemyGameRepository(db)
    return GameService(repository)


@app.get("/")
def root():
    return {"message": "Welcome to BoardGame Manager"}


@app.post("/games", response_model=GameResponse)
def create_game(game: GameCreate, service: GameService = Depends(get_game_service)):
    """
    Create a new game in the game table in the database
    Args:
        game: Game data received from the client (GameCreate schema)
        service: Service responsible for game management

    Returns:
        Game: The created game
    """
    db_game = service.create_game(game)
    return db_game


@app.get("/games", response_model=list[GameResponse])
def get_games(service: GameService = Depends(get_game_service)):
    """
    Retrieve all games from the database

    Args:
        service: Service responsible for game management

    Returns:
        list[Game]: list of all games
    """
    games = service.get_games()
    return games


@app.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: int, service: GameService = Depends(get_game_service)):
    """
    Retrieve Game information from database by game iD.

    Args:
        game_id: ID of the game
        service: Service responsible for game management

    Returns:
        Game: The requested Game

    Raises:
        HTTPException: if the game does not exist in database
    """
    game = service.get_game(game_id)
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    return game


@app.put("/games/{game_id}", response_model=GameResponse)
def update_game(game_id: int, game_update: GameUpdate, service: GameService = Depends(get_game_service)):
    """
    Update one or more fields of an existing game in the db.

    Args:
        game_id: ID of the game
        game_update: Fields to update
        service: Service responsible for game management

    Returns:
        Game: The updated game

    Raises:
        HTTPException: if the game does not exist in database
    """
    game = service.update_game(game_id, game_update)
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    return game


@app.delete("/games/{game_id}")
def delete_game(game_id: int, service: GameService = Depends(get_game_service)):
    """
    Deletes a game from the database
    Args:
        game_id: ID of the game
        service: Service responsible for game management

    Returns:
        dict: message when the game has been deleted

    Raises:
        HTTPException: if the game does not exist in database
    """
    game = service.delete_game(game_id)
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    return {"message": "Game deleted successfully"}


@app.get("/bgg/search", response_model=list[BGGSearchResult])
def bgg_search(title: str):
    """
    Search BoardGameGeek for games matching a title.

    Args:
        title: Game title to search for.

    Returns:
        list[BGGSearchResult]: list of matching games that contains the BGG ID, title and
        release year.
    """
    bgg_service = BGGService()
    return bgg_service.search_games(title)


@app.get("/bgg/game/{bgg_id}", response_model=GameCreate)
def get_bgg_info(bgg_id: int):
    """
    Retrieve detailed information about a game from BGG API.

    Args:
        bgg_id: Board Game Geek game ID.

    Returns:
        GameCreate: Detailed information of game.
    """
    bgg_service = BGGService()
    return bgg_service.get_game_details(bgg_id)


@app.post("/games/import/{bgg_id}", response_model=GameCreate)
def import_game(bgg_id: int, service: GameService = Depends(get_game_service)):
    """
    Import a game from Board Game Geek and save it in the database,
    including the game types
    Args:
        bgg_id: Board Game Geek ID of the game
        service: Service responsible for game management

    Returns:
        Game: The imported game.
    """
    try:
        new_game = service.import_game_from_bgg(bgg_id)
    except GameAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail="Game already exists."
        )
    except BGGGameNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Game not found in BoardGameGeek"
        )
    return new_game
