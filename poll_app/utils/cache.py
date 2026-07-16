"""
Caching utilities for data that doesn't change frequently.
"""

import streamlit as st
from typing import Dict, Any


class CacheManager:
    """Manages cached data for the application."""

    @staticmethod
    @st.cache_data(ttl=5)  # Cache for 5 seconds (counts change frequently)
    def get_topics_data(year: str) -> Dict[str, Dict[str, Any]]:
        """
        Get cached topics data, filtered to the topics visible to `year`.

        Args:
            year: The requesting user's group ('year1' or 'year2'). Part of
                  the cache key, so each group gets its own cached result —
                  Year1 and Year2 never share a cache entry.

        Returns:
            Dictionary mapping topic names to their count and completion status
        """
        from ..database import db_manager

        topics = db_manager.get_all_topics(year=year)
        return {
            topic.get("topic_name", ""): {
                "count": topic.get("count", 0),
                "complete": topic.get("complete", False),
                "topic_id": topic.get("_id"),   # ObjectId reference (for users.topic_id)
                "number": topic.get("id"),       # int display number (1..22)
            }
            for topic in topics
            if topic.get("topic_name")
        }

    @staticmethod
    def clear_topics_cache() -> None:
        """Clear the topics cache (all cached groups)."""
        CacheManager.get_topics_data.clear()