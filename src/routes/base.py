from fastapi import FastAPI, APIRouter, Depends , status
from fastapi.responses import JSONResponse
from helpers.config import get_settings ,Settings
from models.enums import ResponseSignal
import logging


base_router = APIRouter(
    prefix = "/api/v1",
    tags = ["api_v1"]
)

logger = logging.getLogger(__name__)


@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return  JSONResponse(status_code=status.HTTP_200_OK,
                                     content={
                                             "signal" : ResponseSignal.SERVER_IS_UP.value,
                                             "App_Name" : app_name,
                                             "App_Version" : app_version,
                                     })