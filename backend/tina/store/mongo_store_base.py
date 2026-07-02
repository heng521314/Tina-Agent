"""MongoDB connection base class, providing synchronous management and general methods"""

import threading
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from backend.tina.config.store_config import parse_db_config
from backend.tina.util.logger import Logger

logger = Logger(__name__)


class MongoDBConnection:
    """MongoDB connection management (singleton pattern)"""

    _instance = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def get_client(self) -> MongoClient:
        """Get client"""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._connect()
        return self._client

    def get_db(self) -> Database:
        """Get database"""
        if self._db is None:
            with self._lock:
                if self._db is None:
                    self._connect()
        return self._db

    def _connect(self):
        """Establish connection"""
        try:
            mongo_config = parse_db_config()["mongo"]
            host = mongo_config["host"]
            port = mongo_config["port"]
            user = mongo_config["user"]
            password = mongo_config["password"]
            db_name = mongo_config["db_name"]

            # Build connection URL
            if user and password:
                connection_url = f"mongodb://{user}:{password}@{host}:{port}/"
            else:
                connection_url = f"mongodb://{host}:{port}/"

            self._client = MongoClient(connection_url, serverSelectionTimeoutMS=5000)
            self._client.server_info()  # Test connection
            self._db = self._client[db_name]
            logger.info(f"Connected to {host}:{port}/{db_name}")
        except Exception as e:
            logger.info(f"Connection failed: {e}")
            raise

    def close(self):
        """Close connection"""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
        logger.info("Connection closed")


class MongoDBStoreBase:
    """MongoDB storage base class: Provide basic operations"""

    def __init__(self):
        """Initialize storage base class"""
        self._connection = MongoDBConnection()

    def get_collection(self, collection_suffix: str) -> Collection:
        """Get collection: collection_suffix"""
        db = self._connection.get_db()
        return db[collection_suffix]

    def save_or_update(self, collection_suffix: str, query: Dict, data: Dict) -> bool:
        """update data"""
        try:
            collection = self.get_collection(collection_suffix)
            collection.update_one(query, {"$set": data}, upsert=True)
            return True
        except Exception as e:
            logger.info(f"Save failed ({collection_suffix}): {e}")
            return False

    def save_one(self, collection_suffix: str, data: Dict):
        """Save a message"""
        try:
            collection = self.get_collection(collection_suffix)
            collection.insert_one(data)
        except Exception as e:
            logger.info(f"Save failed ({collection_suffix}): {e}")

    def find_one(self, collection_suffix: str, query: Dict) -> Optional[Dict]:
        """Query a single record"""
        try:
            collection = self.get_collection(collection_suffix)
            return collection.find_one(query)
        except Exception as e:
            logger.info(f"Find one failed ({collection_suffix}): {e}")
            return None

    def find_many(
        self, collection_suffix: str, query: Dict, limit: int = 0
    ) -> List[Dict]:
        """Query multiple records (limit=0 means no limit)"""
        try:
            collection = self.get_collection(collection_suffix)
            cursor = collection.find(query)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.info(f"Find many failed ({collection_suffix}): {e}")
            return []

    def delete_many(self, collection_suffix: str, query: Dict):
        """Delete by batch based on conditions"""
        try:
            collection = self.get_collection(collection_suffix)
            collection.delete_many(query)
        except Exception as e:
            logger.info(f"delete item fail: {e}")
