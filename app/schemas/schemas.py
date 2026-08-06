from pydantic import BaseModel, ConfigDict


class GameCreate(BaseModel):
    """
    Schema for creating a new game manually or from BoardGameGeek data.
    """
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

    model_config = ConfigDict(from_attributes=True)


class GameResponse(BaseModel):
    """
    Schema returned when retrieving game information.
    """
    id: int
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
    """
    Schema for updating existing game information.
    Only provided fields will be modified.
    """
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
    """
    Schema representing a game returned by a BoardGameGeek search.
    """
    bgg_id: int
    name: str
    release_year: int | None = None
