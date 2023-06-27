import os

from pydantic import BaseSettings, validator


class Config(BaseSettings):
    config_file: str = '~/.monstermashcfg'

    @validator('config_file', always=True)
    def validate_file(cls, v: str) -> str:
        if v.startswith('~'):
            home = os.path.expanduser('~')
            return os.path.join(home, v.replace('~/', ''))
        return v
