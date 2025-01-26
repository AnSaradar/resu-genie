from pydantic_settings import BaseSettings , SettingsConfigDict
import logging
import os
import json

class Settings(BaseSettings):

    APP_NAME : str
    APP_VERSION : str

    MONGODB_URL : str
    MONGODB_DATABASE : str

    class Config(SettingsConfigDict):
        env_file = '.env'


def get_settings():
    return Settings()


