class GameAlreadyExistsError(Exception):
    """Raised when trying to import a game that already exists."""
    pass


class BGGGameNotFoundError(Exception):
    """Raised when a game cannot be found in BoardGameGeek."""
    pass