from sqlalchemy import select
from .bgg import get_game_types

from app.models import Type


def get_or_create_type(db, game_type, type_kind):
    """
    Checks if the game_type is already in the database, if not it adds it to
    the database
    Args:
        db: Database session
        game_type: Name of the category of mechanic
        type_kind: Type classification (category or mechanic).

    Returns:
        Type: Existing or newly created type.
    """
    existing_type = db.execute(
        select(Type).where(
            Type.type_kind == type_kind,
            Type.game_type == game_type
        )
    ).scalars().first()
    if not existing_type:
        new_type = Type(
            game_type=game_type,
            type_kind=type_kind
        )
        db.add(new_type)
        db.flush()
        return new_type
    else:
        return existing_type
