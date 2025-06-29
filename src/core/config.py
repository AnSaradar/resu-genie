from pydantic_settings import BaseSettings , SettingsConfigDict
import logging
import os
import json
from typing import Optional

class Settings(BaseSettings):

    APP_NAME : str
    APP_VERSION : str

    MONGODB_URL : str
    MONGODB_DATABASE : str

    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int

    GENERATION_BACKEND :str 
    EMBEDDING_BACKEND :str 

    OPENAI_API_KEY :str = None
    OPENAI_API_URL :str = None
    COHERE_API_KEY :str = None

    GENERATION_MODEL_ID :str = None
    EMBEDDING_MODEL_ID :str = None
    EMBEDDING_MODEL_SIZE :int = None

    DEFAULT_INPUT_MAX_CHARACTERS :int = None
    DEFAULT_GENERATION_MAX_OUTPUT_TOKENS :int = None
    DEFAULT_GENERATION_TEMPERATURE :float = None

    
    DEFAULT_LANGUAGE:str ="en"
    PRIMARY_LANGUAGE:str = "en"

    # Email Configuration for OTP
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = None
    SMTP_PASSWORD: str = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = None
    EMAIL_FROM_NAME: str = "Resu-Genie"
    
    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6

    class Config(SettingsConfigDict):
        env_file = '.env'


def get_settings():
    return Settings()


