from fastapi import FastAPI
from routes import base_router, resume_router
import logging

app = FastAPI()

# =================Logger Configurations=================
logging.basicConfig(
    level=logging.INFO,  
    format='%(name)s - %(levelname)s - %(message)s',  # Message format
    datefmt='%Y-%m-%d %H:%M:%S',  
    handlers=[
        logging.StreamHandler(),  # Logs to the console
    ]
)

logger = logging.getLogger(__name__)

# =================Routers Configurations=================
app.include_router(base_router)
app.include_router(resume_router)