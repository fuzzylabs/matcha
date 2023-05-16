"""Remote state manager module."""
import dataclasses


@dataclasses.dataclass
class RemoteStateBucketConfig:
    """Dataclass to store state bucket configuration."""

    container_name: str


@dataclasses.dataclass
class RemoteStateConfig:
    """Dataclass to store remote state configuration."""

    remote_state_bucket: RemoteStateBucketConfig


class RemoteStateManager:
    """Remote State Manager class.

    This class is used to interact with the remote Matcha state.
    """

    def __init__(self) -> None:
        """Initialise Remote State Manager."""
        ...
