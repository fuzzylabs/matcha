"""The analytics service interface.

This approach to collecting usage data was inspired by ZenML; source: https://github.com/zenml-io/zenml/blob/main/src/zenml/utils/analytics_utils.py
"""
import functools
import logging
from enum import Enum
from time import perf_counter
from typing import Any, Callable, Optional, Tuple
from warnings import warn

from segment import analytics

from matcha_ml.errors import MatchaError
from matcha_ml.services._validation import _check_uuid
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state import MatchaState, MatchaStateService

WRITE_KEY = "qwBKAvY6MEUvv5XIs4rE07ohf5neT3sx"

# Suppress Segment warnings
logging.getLogger("segment").setLevel(logging.FATAL)


class AnalyticsEvent(str, Enum):
    """Analytics event enum class."""

    PROVISION = "provision"
    DESTROY = "destroy"
    GET = "get"


def execute_analytics_event(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Tuple[Optional[MatchaState], Any]:
    """Exists to Temporarily fix misleading error messages coming from track decorator.

    Args:
        func (Callable): The function decorated by track.
        *args (Any): arguments passed to the function.
        **kwargs (Any): additional key word arguments passed to the function.

    Returns:
        The result of the call to func, the error code.
    """
    error_code, result = None, None
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        error_code = e
    return result, error_code


def track(event_name: AnalyticsEvent) -> Callable[..., Any]:
    """Track decorator for tracking user analytics with Segment.

    Args:
        event_name (AnalyticsEvent): Name of the command or event being called, e.g. 'provision'
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator function.

        Args:
            func (Callable[..., Any]): The function that is being decorated

        Returns:
            Callable[..., Any]: The function that is being decorated
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
            result, error_code, te, ts = None, None, None, None
            if event_name.value not in {event.value for event in AnalyticsEvent}:
                warn("Event not recognized by analytics service.")

            if not global_params.analytics_opt_out:
                if event_name.value in [event_name.PROVISION, event_name.GET]:
                    ts = perf_counter()
                    result, error_code = execute_analytics_event(func, *args, **kwargs)
                    te = perf_counter()

                try:
                    matcha_state_service = MatchaStateService()
                except Exception as e:
                    matcha_state_service = None
                    error_code = e

                # Get the matcha.state UUID if it exists
                matcha_state_uuid: Optional[str] = None
                if matcha_state_service and matcha_state_service.state_exists():
                    try:
                        state_id_component = matcha_state_service.get_component("id")
                    except MatchaError:
                        state_id_component = None

                    if state_id_component is not None:
                        matcha_state_uuid = state_id_component.find_property(
                            property_name="matcha_uuid"
                        ).value

                        try:
                            _check_uuid(str(matcha_state_uuid))
                        except MatchaError as err:
                            raise err

                if event_name.value in [event_name.DESTROY]:
                    ts = perf_counter()
                    result, error_code = execute_analytics_event(func, *args, **kwargs)
                    te = perf_counter()

                client = analytics.Client(WRITE_KEY, max_retries=1, debug=False)

                client.track(
                    global_params.user_id,
                    event_name.value,
                    {
                        "time_taken": float(te) - float(ts),  # type: ignore
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
