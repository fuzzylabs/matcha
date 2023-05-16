"""The analytics service interface."""
from time import time

from segment import analytics

from matcha_ml.services.global_parameters_service import GlobalParameters

analytics.write_key = "A34pcHvmJcQKKjGtcmR5TR2jEthHCeUE"


def track(event_name: str):
    """Track decorator for tracking user analytics with Segment.

    Args:
        event_name (str): Name of the command or event being called, e.g. 'provision'
    """

    def decorator(func):
        """Decorator function.

        Args:
            func (_type_): _description_
        """

        def inner(*args, **kw):
            """Inner decorator function."""
            ts = time()
            error_code = None
            try:
                func(*args, **kw)
            except Exception as e:
                error_code = e
            te = time()

            global_params = GlobalParameters()

            if not global_params.analytics_opt_out:
                analytics.track(
                    global_params.user_id,
                    event_name,
                    {
                        "time_taken": te - ts,
                        "error_type": f"{error_code.__class__}.{error_code.__class__.__name__}",
                        "command_succeeded": error_code is None,
                    },
                )

        return inner

    return decorator
