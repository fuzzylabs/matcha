"""The analytics service interface."""
from enum import Enum
from time import time
from typing import Any, Callable, Optional

from segment import analytics

from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.services.matcha_state import MatchaStateService

analytics.write_key = "qwBKAvY6MEUvv5XIs4rE07ohf5neT3sx"


class AnalyticsEvent(str, Enum):
    """Analytics event enum class."""

    PROVISION = "provision"
    DESTROY = "destroy"


def track(event_name: str) -> Callable[..., Any]:
    """Track decorator for tracking user analytics with Segment.

    Args:
        event_name (str): Name of the command or event being called, e.g. 'provision'
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator function.

        Args:
            func (Callable[..., Any]): The function that is being decorated
        """

        def inner(*args: Any, **kwargs: Any) -> None:
            """Inner decorator function."""
            ts = time()
            error_code = None
            try:
                func(*args, **kwargs)
            except Exception as e:
                error_code = e
            te = time()

            global_params = GlobalParameters()
            matcha_state_service = MatchaStateService()

            # Get the matcha.state UUID if it exists
            matcha_state_uuid: Optional[str] = None
            if matcha_state_service.check_state_file_exists():
                matcha_state_id_dict = matcha_state_service.state_file.get("id")
                if matcha_state_id_dict:
                    matcha_state_uuid = matcha_state_id_dict.get("matcha_uuid")

            if not global_params.analytics_opt_out:
                analytics.track(
                    global_params.user_id,
                    event_name,
                    {
                        "time_taken": te - ts,
                        "error_type": f"{error_code.__class__}.{error_code.__class__.__name__}",
                        "command_succeeded": error_code is None,
                        "matcha_state_uuid": matcha_state_uuid,
                    },
                )

        return inner

    return decorator
