from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.repositories.sqlalchemy_game_repository import SQLAlchemyGameRepository
from app.services.bgg_service import BGGService
from app.services.game_service import GameService
from app.database.database import engine, get_db
from app.exceptions.exceptions import (
    GameAlreadyExistsError, BGGGameNotFoundError, UserAlreadyExistsError,
)
from app.database.database import create_tables
from app.database.models.models import User
from app.schemas.schemas import (
    GameCreate, GameUpdate, BGGSearchResult,
    GameResponse, UserCreate, UserResponse, Token
)
from app.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.services.user_service import UserService
from app.auth.security import create_access_token
from app.auth.dependencies import get_current_user, require_admin

app = FastAPI(
    title="BoardGame Manager",
    description="RESTful API for managing a board game library."
)

create_tables()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_game_service(db: Session = Depends(get_db)) -> GameService:
    """
    Create a GameService with a database-backed repository.
    Args:
        db: Database session used by the repository.
    Returns:
        GameService: Configured game service instance.
    """
    repository = SQLAlchemyGameRepository(db)
    return GameService(repository)


@app.get("/", response_class=HTMLResponse, tags=["Welcome"])
def root():
    """
    Display the BoardGame Manager welcome page and BGG attribution logo.
    """
    return """
    <html>
        <head>
            <title>BoardGame Manager</title>
        </head>
        <body>
            <h1>Welcome to BoardGame Manager</h1>

            <a href="https://boardgamegeek.com" target="_blank">
                <img
                    src="/static/powered_by_BGG_01_SM.png"
                    alt="Powered by BGG"
                >
            </a>
        </body>
    </html>
    """


@app.post("/games", response_model=GameResponse, tags=["Games"])
def create_game(
        game: GameCreate,
        service: GameService = Depends(get_game_service),
        _: User = Depends(require_admin)
):
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


@app.get("/games", response_model=list[GameResponse], tags=["Games"])
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


@app.get("/games/{game_id}", response_model=GameResponse, tags=["Games"])
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


@app.put("/games/{game_id}", response_model=GameResponse, tags=["Games"])
def update_game(
        game_id: int,
        game_update: GameUpdate,
        service: GameService = Depends(get_game_service),
        _: User = Depends(require_admin)
):
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


@app.delete("/games/{game_id}", tags=["Games"])
def delete_game(
        game_id: int,
        service: GameService = Depends(get_game_service),
        _: User = Depends(require_admin)
):
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


@app.get("/bgg/search", response_model=list[BGGSearchResult], tags=["BoardGameGeek"])
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


@app.get("/bgg/game/{bgg_id}", response_model=GameCreate, tags=["BoardGameGeek"])
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


@app.post("/games/import/{bgg_id}", response_model=GameCreate, tags=["BoardGameGeek"])
def import_game(
        bgg_id: int,
        service: GameService = Depends(get_game_service),
        _: User = Depends(require_admin)
):
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
    except GameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=400,
            detail="Game already exists."
        ) from exc
    except BGGGameNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Game not found in BoardGameGeek"
        ) from exc
    return new_game


@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    Args:
        user_data: Data required to create the user.
        db: Database session used to access the user repository.
    Returns:
        UserResponse: The newly created user.
    Raises:
        HTTPException: If the username already exists.
    """
    repository = SQLAlchemyUserRepository(db)
    service = UserService(repository)
    try:
        return service.create_user(user_data)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=400, detail="Username already exists."
        ) from exc


@app.post("/login", response_model=Token, tags=["Users"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and generate a JWT access token.
    Args:
        form_data: Login credentials containing username and password.
        db: Database session used to access the user repository.
    Returns:
        Token: JWT access token and token type for authenticated requests.
    Raises:
        HTTPException: If the username or password is incorrect.
    """
    repository = SQLAlchemyUserRepository(db)
    service = UserService(repository)

    user = service.authenticate_user(
        form_data.username,
        form_data.password
    )
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(
        {"sub": str(user.id)}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/users/me", response_model=UserResponse, tags=["Users"])
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retrieve the information of the currently authenticated user.
    Args:
        current_user: Authenticated user retrieved from the JWT token.
    Returns:
        UserResponse: Information about the currently authenticated user.
    """
    return current_user
