from fastapi import FastAPI
from routes import base_router, resume_router, auth_router, user_profile_router, experience_router, education_router, skill_router, language_router, certification_router, link_router
from core.config import get_settings, Settings
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from fastapi.middleware.cors import CORSMiddleware
from llm import LLMProviderFactory
from llm.prompt_templates import TemplateParser

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

# =================CORS Configurations=================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # This allows all headers
)

@app.on_event("startup")
async def startup():
    settings = get_settings()

    # ======================MongoDB Intialization ======================
    try:
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")

   # ======================LLM Initialization ======================
    try:
        llm_provider_factory = LLMProviderFactory(settings)
        app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
        app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
        app.template_parser = TemplateParser(language=settings.PRIMARY_LANGUAGE,
                                            default_language=settings.DEFAULT_LANGUAGE)
        logger.info(f"Initialized LLM with provider: {settings.GENERATION_BACKEND}")
    except Exception as e:
        logger.error(f"Error initializing LLM components: {str(e)}")

# =================Routers Configurations=================
app.include_router(base_router)
app.include_router(resume_router)
app.include_router(auth_router)
app.include_router(user_profile_router)
app.include_router(experience_router)
app.include_router(education_router)
app.include_router(skill_router)
app.include_router(language_router)
app.include_router(certification_router)
app.include_router(link_router)

