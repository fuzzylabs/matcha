"""The analytics service interface.

This approach to collecting usage data was inspired by ZenML; source: https://github.com/zenml-io/zenml/blob/main/src/zenml/utils/analytics_utils.py
"""
import functools
from enum import Enum
from time import perf_counter
from typing import Any, Callable, Optional

from segment import analytics

from matcha_ml.errors import MatchaError
from matcha_ml.services._validation import _check_uuid
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state import MatchaStateService

analytics.write_key = "qwBKAvY6MEUvv5XIs4rE07ohf5neT3sx"


class AnalyticsEvent(str, Enum):
    """Analytics event enum class."""

    PROVISION = "provision"
    DESTROY = "destroy"
    GET = "get"


def track(event_name: AnalyticsEvent) -> Callable[..., Any]:
    """Track decorator for tracking user analytics with Segment.

    Args:
        event_name (AnalyticsEvent): Name of the command or event being called, e.g. 'provision'
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator function.

        Args:
            func (Callable[..., Any]): The function that is being decorated
        """

        @functools.wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            """The internal function that does the logic of capturing analytics and executing the function that's being wrapped.

            Raises:
                MatchaError: Raised when the matcha_state_uuid is invalid.
                error_code: Raised when an error occurs when running the wrapped function.

            Returns:
                Any: the result of the wrapped function.
            """
            global_params = GlobalParameters()

            if not global_params.analytics_opt_out:
                ts = perf_counter()
                error_code = None
                result = None
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    error_code = e
                te = perf_counter()

                matcha_state_service = MatchaStateService()

                # Get the matcha.state UUID if it exists
                matcha_state_uuid: Optional[str] = None
                if matcha_state_service.check_state_file_exists():
                    matcha_state_id_dict = matcha_state_service.state_file.get("id")
                    if matcha_state_id_dict is not None:
                        matcha_state_uuid = matcha_state_id_dict.get("matcha_uuid")

                        try:
                            _check_uuid(str(matcha_state_uuid))
                        except MatchaError as me:
                            raise MatchaError(str(me))

                analytics.track(
                    global_params.user_id,
                    event_name.value,
                    {
                        "time_taken": te - ts,
                        "error_type": f"{error_code.__class__}.{error_code.__class__.__name__}",
                        "command_succeeded": error_code is None,
                        "matcha_state_uuid": matcha_state_uuid,
                    },
                )
                if error_code is not None:
                    raise error_code
            else:
                result = func(*args, **kwargs)

            return result

        return inner

    return decorator
