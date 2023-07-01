import os

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Config class provides a model for application configuration settings,
    which includes the path to the configuration file.

    Attributes:
        config_file (str): The path to the configuration file. Default is '~/.monstermashcfg'.
    """

    config_file: str = '~/.monstermashcfg'

    @field_validator('config_file')
    def validate_file(cls, v: str) -> str:
        """
        Validate and normalize the path of the configuration file.

        This validator check that if the config_file path starts with '~', it is expanded to the full path in the
        user's home directory. If not we store it where you have asked.

        Args:
            v (str): The original path string.

        Returns:
            str: The normalized file path.
        """
        if v.startswith('~'):
            home = os.path.expanduser('~')
            return os.path.join(home, v.replace('~/', ''))
        return v
