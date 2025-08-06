import os
from typing import Any, Dict
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()

        self.config: Dict[str, Any] = {
            "env": self._get_env_var("ENV", str, default="development"),
            "ripley":{
                "username": self._get_env_var("RIPLEY_USERNAME", str),
                "password": self._get_env_var("RIPLEY_PASSWORD", str),
            }
        }

    def _get_env_var(self, name, expected_type, default=None):
        value = os.getenv(name)

        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Environment variable {name} not set")

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Environment variable {name} is not of type {expected_type.__name__}"
            )

        return value
