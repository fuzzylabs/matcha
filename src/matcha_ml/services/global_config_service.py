"""Global config service for creating and modifying a users global config files."""
import os
import uuid
from typing import Any, Dict, Optional

import yaml


class GlobalConfigurationService:
    """_summary_."""

    _instance: Optional["GlobalConfigurationService"] = None
    user_id: Optional[str] = None
    analytics_opt_in: Optional[bool] = True
    _config_file_path: Optional[str] = None
    __initialized: bool = False

    def __init__(self) -> None:
        """_summary_."""
        if self.__initialized is False:
            # Check if config.yaml file exists and read in variables to the class
            self._config_file_path = os.path.join(
                self.default_config_directory(), "config.yaml"
            )

            if os.path.exists(self._config_file_path):
                with open(self._config_file_path) as file:
                    yaml_data = yaml.safe_load(file)
                self.user_id = yaml_data.get("user_id")
                self.analytics_opt_in = yaml_data.get("analytics_opt_in")
            else:
                # Set variables
                self.user_id = str(uuid.uuid4())
                self.analytics_opt_in = True

                data = {
                    "user_id": self.user_id,
                    "analytics_opt_in": self.analytics_opt_in,
                }

                # Create the '.matcha-ml' config directory
                os.makedirs(os.path.dirname(self._config_file_path), exist_ok=True)
                # Create config file and populate with the current class variables
                with open(self._config_file_path, "w") as file:
                    yaml.dump(data, file)

    def __new__(cls) -> "GlobalConfigurationService":
        """Singleton class definition.

        Returns:
            GlobalConfigurationService: Already existing initialised object, otherwise a new singleton object
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        else:
            cls.__initialized = True

        return cls._instance

    def analytics_opt_out(self) -> None:
        """Opt out of analytic collection."""
        self.analytics_opt_in = False
        # UPDATE CONFIG FILE

    @staticmethod
    def default_config_directory() -> str:
        """Path to the default global configuration directory.

        Returns:
            The default global configuration directory.
        """
        home_path = os.path.expanduser("~")
        return os.path.join(home_path, ".matcha-ml")

    @staticmethod
    def default_config_file_path() -> str:
        """Path to the default global configuration file.

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
        with open(self.default_config_file_path()) as f:
            self._config = dict(yaml.safe_load(f))

        return self._config

    # @config_file.setter(fset)
    # def config_file(self) -> Dict[str, Any]:
    #     """Getter of the config file.

    #     Returns:
    #         Dict[str, Any]: the user config file in the format of a dictionary.
    #     """
    #     with open(self.default_config_file_path()) as f:
    #         self._config = dict(yaml.safe_load(f))

    #     return self._config
