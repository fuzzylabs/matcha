"""The analytics service interface.

This approach to collecting usage data was inspired by ZenML; source: https://github.com/zenml-io/zenml/blob/main/src/zenml/utils/analytics_utils.py
"""
import functools
import logging
from enum import Enum
from time import perf_counter
from typing import Annotated, Any, Callable, Optional, Tuple
from warnings import warn

from segment import analytics

from matcha_ml.errors import MatchaError
from matcha_ml.services._validation import _check_uuid
from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.state import MatchaResourceProperty, MatchaState, MatchaStateService

WRITE_KEY = "qwBKAvY6MEUvv5XIs4rE07ohf5neT3sx"

# Suppress Segment warnings
logging.getLogger("segment").setLevel(logging.FATAL)


class AnalyticsEvent(str, Enum):
    """Analytics event enum class."""

    PROVISION = "provision"
    DESTROY = "destroy"
    GET = "get"


def _get_state_uuid() -> Optional[MatchaResourceProperty]:
    """A function for retrieving the Matcha State UUID.

    Returns:
        matcha_state_uuid (Optional[MatchaResourceProperty]): The Matcha State UUID if present.

    Raises:
        MatchaError: where the MatchaStateService fails to instantiate, the MatchaStateService does not have an 'id' component, or the Matcha state UUID fails validation.
    """
    try:
        matcha_state_service = MatchaStateService()
    except MatchaError:
        return None

    try:
        state_id_component = matcha_state_service.get_component("id")
    except MatchaError:
        return None

    matcha_state_uuid = state_id_component.find_property(property_name="matcha_uuid")

    try:
        _check_uuid(str(matcha_state_uuid.value))
    except MatchaError as err:
        raise err

    return matcha_state_uuid


def _execute_analytics_event(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Tuple[Optional[MatchaState], Any]:
    """Executes the function decorated by track.

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


def _time_event(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Tuple[Any, Exception, float, float]:
    """Times the execution of the function decorated by track.

    Args:
        func (Callable): The function decorated by track.
        *args (Any): arguments passed to the function.
        **kwargs (Any): additional keyword arguments passed to the function.

    Returns:
        Tuple[Any, Exception, float, float]: The result of the call to func, the error code, the start time of execution, the end time of execution.
    """
    ts = perf_counter()
    result, error_code = _execute_analytics_event(func, *args, **kwargs)
    te = perf_counter()

    return result, error_code, ts, te


def _post_event(
    event_name: AnalyticsEvent,
    matcha_state_uuid: Optional[MatchaResourceProperty],
    global_params: GlobalParameters,
    error_code: Optional[Exception],
    time_taken: float,
) -> Tuple[Annotated[bool, "success"], Annotated[str, "message"]]:
    """Posts the tracked analytics to Segment.

    Args:
        event_name (AnalyticsEvent): The enumerated name of the analytics event.
        matcha_state_uuid (Optional[MatchaResourceProperty]): the uuid for the Matcha state file.
        global_params (GlobalParameters): The GlobalParameters object containing the user id.
        error_code (Optional[Exception]): The error propagated by a failing underlying command.
        time_taken (float): The time taken for the underlying command to execute.

    Returns:
        A boolean representing the status of the event posting, the message representing the status of the event posting.
    """
    client = analytics.Client(WRITE_KEY, max_retries=1, debug=False)

    if matcha_state_uuid:
        matcha_state_uuid = matcha_state_uuid.value

    return client.track(
        global_params.user_id,
        event_name.value,
        {
            "time_taken": time_taken,
            "error_type": f"{error_code.__class__}.{error_code.__class__.__name__}",
            "command_succeeded": error_code is None,
            "matcha_state_uuid": matcha_state_uuid,
        },
    )


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

            # checks if the tracking event name is a valid enum
            if event_name.value not in {event.value for event in AnalyticsEvent}:
                warn("Event not recognized by analytics service.")

            if not global_params.analytics_opt_out:
                result, error_code, ts, te = None, None, None, None

                if event_name.value in [event_name.PROVISION, event_name.GET]:
                    result, error_code, ts, te = _time_event(func, *args, **kwargs)

                matcha_state_uuid: Optional[MatchaResourceProperty] = _get_state_uuid()

                if event_name.value in [event_name.DESTROY]:
                    result, error_code, ts, te = _time_event(func, *args, **kwargs)

                time_taken = te - ts if te is not None and ts is not None else 0.0

                _post_event(
                    event_name=event_name,
                    matcha_state_uuid=matcha_state_uuid,
                    global_params=global_params,
                    error_code=error_code,
                    time_taken=time_taken,
                )

                # if not event[0]:
                #     warn("Analytics for f{event_name} were not posted to Segment.")
            else:
                result = func(*args, **kwargs)

            return result

        return inner

    return decorator
