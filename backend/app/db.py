import os
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "urban_hazard")

client: Optional[MongoClient] = None


def get_database() -> Database:
    global client
    if client is None:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return client[MONGODB_DB]


def get_sensor_collection() -> Collection:
    db = get_database()
    return db["sensor_readings"]
