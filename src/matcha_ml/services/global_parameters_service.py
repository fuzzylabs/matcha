"""Global parameter service for creating and modifying a users global config files."""
import os
from typing import Any, Dict, Optional
from uuid import uuid4

import yaml

from matcha_ml.errors import MatchaError, MatchaPermissionError
from matcha_ml.services._validation import _check_uuid


class GlobalParameters:
    """A Global parameters service for interacting and updating a users global config file.

    Users are opted-in for analytics data collection by default.
    """

    _instance: Optional["GlobalParameters"] = None
    _user_id: Optional[str] = None
    _analytics_opt_out: bool = False

    def __new__(cls) -> "GlobalParameters":
        """Creates a singleton instance of the GlobalParameters class.

        Returns:
            GlobalParameters: Already existing initialized object, otherwise a new singleton object
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Check if config.yaml file exists and read in variables to the class
            if os.path.exists(cls._instance.default_config_file_path):
                cls._instance._read_global_config()
            else:
                cls._instance._create_global_config()

        return cls._instance

    def _read_global_config(self) -> None:
        """Reads the config yaml file containing the global parameters.

        Raises:
            MatchaError: Raised when the user_id uuid is an invalid uuid.
        """
        with open(self.default_config_file_path) as file:
            yaml_data = yaml.safe_load(file)

        try:
            _check_uuid(yaml_data.get("user_id"))
        except MatchaError as me:
            raise MatchaError(str(me))

        self._user_id = yaml_data.get("user_id")
        self._analytics_opt_out = yaml_data.get("analytics_opt_out")

    def _create_global_config(self) -> None:
        """Creates a new config yaml file containing the global parameters."""
        # Generate a new unique user ID
        data = {
            "user_id": self.user_id,
            "analytics_opt_out": self.analytics_opt_out,
        }

        # Create the '.matcha-ml' config directory
        try:
            os.makedirs(os.path.dirname(self.default_config_file_path), exist_ok=True)
        except PermissionError:
            raise MatchaPermissionError(
                f"Error - You do not have permission to write the configuration. Check if you have write permissions for '{self.default_config_file_path}'"
            )

        # Create config file and populate with the current class variables
        with open(self.default_config_file_path, "w") as file:
            yaml.dump(data, file)

    def _update_global_config(self) -> None:
        """Updates an existing config file with the global parameters."""
        data = {
            "user_id": self.user_id,
            "analytics_opt_out": self.analytics_opt_out,
        }

        with open(self.default_config_file_path, "w") as file:
            yaml.dump(data, file)

    @property
    def user_id(self) -> str:
        """User ID getter.

        Returns:
            str: Unique user ID string
        """
        if self._user_id is None:
            self._user_id = str(uuid4())
        return self._user_id

    @property
    def analytics_opt_out(self) -> bool:
        """Analytics opt out getter.

        Returns:
            bool: User is opted out of analytic data collection bool.
        """
        return self._analytics_opt_out

    @analytics_opt_out.setter
    def analytics_opt_out(self, value: bool) -> None:
        """Opt in or out of analytic collection.

        Args:
            value (bool): Whether to disable analytics (True) or enable analytics (False)
        """
        self._analytics_opt_out = value
        self._update_global_config()

    @property
    def default_config_file_path(self) -> str:
        """Path to the default configuration file containing the global parameters.

        Returns:
            The default global configuration directory.
        """
        config_path = os.path.join(os.path.expanduser("~"), ".config")

        return os.path.join(config_path, "matcha-ml", "config.yaml")

    @property
    def config_file(self) -> Dict[str, Any]:
        """Getter of the config file.

        Returns:
            Dict[str, Any]: the user config file in the format of a dictionary.
        """
        with open(self.default_config_file_path) as f:
            config_contents = dict(yaml.safe_load(f))

        return config_contents
