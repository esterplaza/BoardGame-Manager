from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from .database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    bgg_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    release_year = Column(Integer)
    min_players = Column(Integer)
    max_players = Column(Integer)
    min_playing_time = Column(Integer)
    max_playing_time = Column(Integer)
    min_age = Column(Integer)
    average_rating = Column(Numeric(3, 2))
    box_image = Column(Text)


class Type(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True, index=True)
    game_type = Column(String, nullable=False)
    type_kind = Column(String, nullable=False)


class GameType(Base):
    __tablename__ = "game_types"

    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    type_id = Column(Integer, ForeignKey("types.id"), primary_key=True)
