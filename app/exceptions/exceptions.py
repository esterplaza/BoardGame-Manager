class GameAlreadyExistsError(Exception):
    """Raised when trying to import a game that already exists."""


class BGGGameNotFoundError(Exception):
    """Raised when a game cannot be found in BoardGameGeek."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing username."""
