from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.bgg import search_games, get_game_details, get_game_types
from .database import SessionLocal, engine
from .models import Game, Base, Type, GameType
from .schemas import GameCreate, GameUpdate, BGGSearchResult
from app.services.game_types import get_or_create_type

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


@app.get("/")
def root():
    return {"message": "Welcome to BoardGame Manager"}


@app.post("/games")
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    """
    Create a new game in the game table in the database
    Args:
        game: Game data received from the client (GameCreate schema)
        db: Database session

    Returns:
        Game: The created game
    """
    db_game = Game(**game.model_dump())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


@app.get("/games")
def get_games(db: Session = Depends(get_db)):
    """
    Retrieve all games from the database

    Args:
        db: database session

    Returns:
        list[Game]: list of all games
    """
    games = db.execute(select(Game)).scalars().all()
    return games


@app.get("/games/{game_id}")
def get_game(game_id: int, db: Session = Depends(get_db)):
    """
    Retrieve Game information from database by game iD.

    Args:
        game_id: ID of the game
        db: Database session

    Returns:
        Game: The requested Game

    Raises:
        HTTPException: if the game does not exist in database
    """
    game = db.execute(select(Game).where(Game.id == game_id)).scalar_one_or_none()
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    print(type(game))
    return game


@app.put("/games/{game_id}")
def update_game(game_id: int, game_update: GameUpdate, db: Session = Depends(get_db)):
    """
    Update one or more fields of an existing game in the db.

    Args:
        game_id: ID of the game
        game_update: Fields to update
        db: Database session

    Returns:
        Game: The updated game

    Raises:
        HTTPException: if the game does not exist in database
    """
    game = db.execute(select(Game).where(Game.id == game_id)).scalar_one_or_none()
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    update_data = game_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(game, key, value)
    db.commit()
    db.refresh(game)
    return game


@app.delete("/games/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """
    Deletes a game from the database
    Args:
        game_id: ID of the game
        db: Database session

    Returns:
        dict: message when the game has been deleted

    Raises:
        HTTPException: if the game does not exist in database
    """
    game = db.execute(select(Game).where(Game.id == game_id)).scalar_one_or_none()
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    game_types = db.execute(select(GameType).where(GameType.game_id == game_id)).scalars().all()
    for game_type in game_types:
        db.delete(game_type)
    db.flush()
    db.delete(game)
    db.commit()
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
    return search_games(title)


@app.get("/bgg/game/{bgg_id}", response_model=GameCreate)
def get_bgg_info(bgg_id: int):
    """
    Retrieve detailed information about a game from BGG API.

    Args:
        bgg_id: Board Game Geek game ID.

    Returns:
        GameCreate: Detailed information of game.
    """
    return get_game_details(bgg_id)


@app.post("/games/import/{bgg_id}")
def import_game(bgg_id: int, db: Session = Depends(get_db)):
    """
    Import a game from Board Game Geek and save it in the database,
    including the game types
    Args:
        bgg_id: Board Game Geek ID of the game
        db: Database session

    Returns:
        Game: The imported game.
    """
    existing_game = db.execute(select(Game).where(Game.bgg_id == bgg_id)).first()
    if existing_game is not None:
        raise HTTPException(
            status_code=400,
            detail="Game already exists."
        )
    game_data = get_game_details(bgg_id)
    if game_data is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found in BoardGameGeek"
        )
    new_game = Game(**game_data)
    db.add(new_game)
    db.flush()
    game_types = get_game_types(bgg_id)
    for category in game_types.get("categories"):
        type_category = get_or_create_type(db, category, "category")
        new_type = GameType(
            game_id=new_game.id,
            type_id=type_category.id
        )
        db.add(new_type)
        db.flush()
    for mechanic in game_types.get("mechanics"):
        type_category = get_or_create_type(db, mechanic, "mechanic")
        new_type = GameType(
            game_id=new_game.id,
            type_id=type_category.id
        )
        db.add(new_type)
        db.flush()
    db.commit()
    db.refresh(new_game)
    return new_game
