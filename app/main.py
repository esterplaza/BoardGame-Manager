from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.bgg import search_games
from .database import SessionLocal
from .models import Game
from .schemas import GameCreate, GameUpdate

app = FastAPI()


def get_db():
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
    db_game = Game(**game.model_dump())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


@app.get("/games")
def get_games(db: Session = Depends(get_db)):
    games = db.execute(select(Game)).scalars().all()
    return games


@app.get("/games/{game_id}")
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.execute(select(Game).where(Game.id == game_id)).scalar_one_or_none()
    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found"
        )
    return game


@app.put("/games/{game_id}")
def update_game(game_id: int, game_update: GameUpdate, db: Session = Depends(get_db)):
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
def update_game(game_id: int, db: Session = Depends(get_db)):
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
    result = search_games(title)
    return result