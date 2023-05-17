"""Global parameter service for creating and modifying a users global config files."""
import os
import uuid
from typing import Any, Dict, Optional

import yaml

from matcha_ml.errors import MatchaPermissionError


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
            GlobalParameters: Already existing initialised object, otherwise a new singleton object
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
        """Reads the config yaml file containing the global parameters."""
        with open(self.default_config_file_path) as file:
            yaml_data = yaml.safe_load(file)

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
            str: Unqiue user ID string
        """
        if self._user_id is None:
            self._user_id = str(uuid.uuid4())
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
        self._analytics_opt_out = value
        self._update_global_config()

    @property
    def default_config_file_path(self) -> str:
        """Path to the default configuration file containing the global parameters.

        Returns:
            The default global configuration directory.
        """
        home_path = os.path.expanduser("~")
        return os.path.join(home_path, ".matcha-ml", "config.yaml")

    @property
    def config_file(self) -> Dict[str, Any]:
        """Getter of the config file.

        Returns:
            Dict[str, Any]: the user config file in the format of a dictionary.
        """
        with open(self.default_config_file_path) as f:
            config_contents = dict(yaml.safe_load(f))

        return config_contents
