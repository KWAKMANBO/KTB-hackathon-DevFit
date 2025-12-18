from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "culturefit")

client : AsyncIOMotorClient = None
database = None

# DB 연결
async def connect_db():
    global client,database
    client = AsyncIOMotorClient(MONGO_URL)
    database = client[DATABASE_NAME]

# DB 연결 끊기
async def close_db():
    global client
    if client:
        client.close()


def get_database():
    """현재 연결된 database 객체 반환"""
    return database