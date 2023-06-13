"""Matcha core functionality module."""
from .core import (
    analytics_opt_in,
    analytics_opt_out,
    destroy,
    get,
    provision,
    remove_state_lock,
)

__all__ = [
    "get",
    "analytics_opt_in",
    "analytics_opt_out",
    "remove_state_lock",
    "destroy",
    "provision",
]
