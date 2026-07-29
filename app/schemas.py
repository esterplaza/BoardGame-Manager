from pydantic import BaseModel


class GameCreate(BaseModel):
    bgg_id: int
    name: str
    release_year: int | None = None
    min_players: int | None = None
    max_players: int | None = None
    min_playing_time: int | None = None
    max_playing_time: int | None = None
    min_age: int | None = None
    average_rating: float | None = None
    box_image: str | None = None


class GameUpdate(BaseModel):
    name: str | None = None
    release_year: int | None = None
    min_players: int | None = None
    max_players: int | None = None
    min_playing_time: int | None = None
    max_playing_time: int | None = None
    min_age: int | None = None
    average_rating: float | None = None
    box_image: str | None = None


class BGGSearchResult(BaseModel):
    bgg_id: int
    title: str
    release_year: int | None = None
