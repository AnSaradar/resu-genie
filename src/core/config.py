from pydantic_settings import BaseSettings , SettingsConfigDict
import logging
import os
import json

class Settings(BaseSettings):

    APP_NAME : str
    APP_VERSION : str

    MONGODB_URL : str
    MONGODB_DATABASE : str

    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int

    class Config(SettingsConfigDict):
        env_file = '.env'


def get_settings():
    return Settings()


