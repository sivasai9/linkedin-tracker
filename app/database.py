from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import JobApplication, Reminder
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "linkedin_tracker")


async def init_db():
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[JobApplication, Reminder],
    )
