"""The analytics service interface."""
from time import time

from segment import analytics

from matcha_ml.services.global_parameters_service import GlobalParameters
from matcha_ml.services.matcha_state import MatchaStateService

analytics.write_key = "qwBKAvY6MEUvv5XIs4rE07ohf5neT3sx"


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
            matcha_state_service = MatchaStateService()

            # Get the matcha.state UUID if it exists
            matcha_state_uuid = None
            if matcha_state_service.check_state_file_exists():
                if "id" in matcha_state_service.get_resource_names():
                    if "matcha_uuid" in matcha_state_service.get_property_names("id"):
                        matcha_state_uuid = (
                            matcha_state_service.fetch_resources_from_state_file["id"][
                                "matcha_uuid"
                            ]
                        )

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
