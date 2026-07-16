"""
Database module for MongoDB operations.
Handles all data persistence and retrieval.
"""

from pymongo import MongoClient
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import os
import certifi

# --- Configuration ---
load_dotenv()

MONGO_URI = os.getenv("connection_string")
DATABASE_NAME = "e3dad-projects"
DB_COLLECTION_USERS = "users"
DB_COLLECTION_TOPICS = "topics"


class DatabaseManager:
    """Manages MongoDB connection and CRUD operations."""

    def __init__(self):
        if not MONGO_URI:
            raise ConnectionError(
                "MONGO_URI environment variable is not set. "
                "Please configure it in .env file."
            )
        
        try:
            self.client = MongoClient(
                MONGO_URI,
                tlsCAFile=certifi.where()
            )
            self.db = self.client[DATABASE_NAME]
        except Exception as e:
            print(f"Failed to initialize MongoDB connection: {e}")
            raise

    # ==================== User Operations ====================

    def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Fetch a user record by phone number."""
        try:
            return self.db[DB_COLLECTION_USERS].find_one(
                {"phone_number": phone_number}
            )
        except Exception as e:
            print(f"Error fetching user {phone_number}: {e}")
            return None

    def save_or_update_user(self, data: Dict[str, Any]) -> bool:
        """Insert new user or update existing one."""
        try:
            result = self.db[DB_COLLECTION_USERS].update_one(
                {"phone_number": data["phone_number"]},
                {"$set": data},
                upsert=True
            )
            return result.matched_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"Error saving/updating user {data['phone_number']}: {e}")
            return False

    def update_user_selections(
        self, 
        phone_number: str, 
        topic_name: str, 
        increment: int
    ) -> bool:
        """Atomically update selection count for a user's topic."""
        try:
            update_result = self.db[DB_COLLECTION_USERS].update_one(
                {"phone_number": phone_number},
                {
                    "$inc": {
                        f"selected_topic_counts.{topic_name}": increment
                    }
                }
            )
            return (
                update_result.modified_count > 0 
                or update_result.upserted_id is not None
            )
        except Exception as e:
            print(
                f"Error updating topic count for {phone_number} "
                f"with topic '{topic_name}': {e}"
            )
            return False

    # ==================== Topic Operations ====================

    def get_all_topics(self, year: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch topic records.

        Args:
            year: If given ('year1' or 'year2'), only topics whose `groups`
                array contains this value are returned. If omitted, all
                topics are returned (unfiltered).
        """
        try:
            query = {"groups": year} if year else {}
            return list(self.db[DB_COLLECTION_TOPICS].find(query))
        except Exception as e:
            print(f"Error fetching all topics: {e}")
            return []

    def get_topic_by_id(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single topic by its ID."""
        try:
            return self.db[DB_COLLECTION_TOPICS].find_one({"_id": topic_id})
        except Exception as e:
            print(f"Error fetching topic {topic_id}: {e}")
            return None

    def get_topic_id_by_name(self, topic_name: str) -> Optional[Any]:
        """Get the topic ID (the _id field) for a given topic name."""
        try:
            topic = self.db[DB_COLLECTION_TOPICS].find_one(
                {"topic_name": topic_name},
                {"_id": 1}  # Only return the _id field
            )
            if topic:
                return topic.get("_id")
            return None
        except Exception as e:
            print(f"Error getting topic ID for name '{topic_name}': {e}")
            return None

    def get_topic_id_by_name(self, topic_name: str) -> Optional[str]:
        """Fetch a topic's ID by its name."""
        try:
            topic = self.db[DB_COLLECTION_TOPICS].find_one({"topic_name": topic_name})
            if topic:
                return str(topic["_id"])  # Convert ObjectId to string for consistency
            return None
        except Exception as e:
            print(f"Error fetching topic ID for name '{topic_name}': {e}")
            return None

    def update_topic_count(self, topic_name: str, increment: int) -> bool:
        """Atomically increment/decrement a topic's selection count."""
        try:
            result = self.db[DB_COLLECTION_TOPICS].update_one(
                {"topic_name": topic_name},
                {"$inc": {"count": increment}}
            )
            return (
                result.modified_count > 0
                or result.upserted_id is not None
            )
        except Exception as e:
            print(
                f"Error updating count for topic '{topic_name}': {e}"
            )
            return False

    # ==================== Connection Management ====================

    def close(self):
        """Close the database connection."""
        if self.client:
            self.client.close()

    def health_check(self) -> bool:
        """Verify database connection is working."""
        try:
            self.db.command('ping')
            return True
        except Exception:
            return False


# Singleton instance for application-wide use
db_manager = DatabaseManager()


if __name__ == "__main__":
    print("Database setup successful.")
    
    if db_manager.health_check():
        print("Topics:", db_manager.get_all_topics())
        print("Database connection verified.")
    else:
        print("FATAL ERROR: Database health check failed.")