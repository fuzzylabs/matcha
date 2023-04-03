"""Common emojis."""
from enum import Enum


class Emojis(Enum):
    """Enumeration of common emojis.

    Args:
        Enum (Enum): the base class for the enumeration
    """

    CHECKMARK: str = "✔"
    CROSS: str = "❌"
    WAITING: str = "⏳"
    MATCHA: str = "🍵"
