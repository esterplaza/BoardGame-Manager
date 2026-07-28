from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.bgg import search_games
from .database import SessionLocal
from .models import Game
from .schemas import GameCreate, GameUpdate

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
    db.delete(game)
    db.commit()
    return {"message": "Game deleted successfully"}


@app.get("/bgg/search")
def bgg_search(title: str):
    """
    Search BoardGameGeek for games matching a title.

    Args:
        title: Game title to search for.

    Returns:
        list[dict]: list of matching games that contains the BGG ID, title and
        release year.
    """
    result = search_games(title)
    return result
