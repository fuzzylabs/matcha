"""Global config service for creating and modifying a users global config files."""
import os
import uuid
from typing import Any, Dict, Optional

import yaml


class GlobalConfigurationService:
    """A Global Config Service for interacting and updating a users global config file."""

    _instance: Optional["GlobalConfigurationService"] = None
    user_id: Optional[str] = None
    analytics_opt_out: Optional[bool] = False
    _config_file_path: Optional[str] = None
    __initialized: bool = False

    def __init__(self) -> None:
        """Constructor for the GlobalConfiguration Service.

        Checks if a GlobalConfig under the users home directory exists and creates one if it does not exist.
        """
        if self.__initialized is False:
            # Check if config.yaml file exists and read in variables to the class
            if os.path.exists(self.default_config_file_path):
                self._read_global_config(self.default_config_file_path)
            else:
                self._create_global_config(self.default_config_file_path)

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

    def _read_global_config(self, config_file_path: str) -> None:
        """Reads the global config yaml file.

        Args:
            config_file_path (str): Path to users global config file
        """
        with open(config_file_path) as file:
            yaml_data = yaml.safe_load(file)
            self.user_id = yaml_data.get("user_id")
            self.analytics_opt_out = yaml_data.get("analytics_opt_out")

    def _create_global_config(self, config_file_path: str) -> None:
        """Creates a new global config yaml file.

        Args:
            config_file_path (str): Path to users global config file
        """
        # Set variables
        self.user_id = str(uuid.uuid4())
        self.analytics_opt_out = False

        data = {
            "user_id": self.user_id,
            "analytics_opt_out": self.analytics_opt_out,
        }

        # Create the '.matcha-ml' config directory
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        # Create config file and populate with the current class variables
        with open(config_file_path, "w") as file:
            yaml.dump(data, file)

    def _update_global_config(self, config_file_path: str) -> None:
        """Updates an existing global config file.

        Args:
            config_file_path (str): _description_
        """
        data = {
            "user_id": self.user_id,
            "analytics_opt_out": self.analytics_opt_out,
        }

        with open(config_file_path) as file:
            yaml_data = yaml.safe_load(file)

        yaml_data.update(data)

        # Create config file and populate with the current class variables
        with open(config_file_path, "w") as file:
            yaml.dump(yaml_data, file)

    def opt_out_of_analytics(self) -> None:
        """Opt out of analytic collection."""
        self.analytics_opt_out = True
        self._update_global_config(self.default_config_file_path)

    @property
    def default_config_file_path(self) -> str:
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
        with open(self.default_config_file_path) as f:
            config_contents = dict(yaml.safe_load(f))

        return config_contents
