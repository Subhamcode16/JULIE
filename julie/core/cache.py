"""Semantic Caching System.

Caches responses for identical or semantically similar questions to save tokens.
"""

import time
import hashlib
from typing import Optional, Dict, Any
from loguru import logger

# Simple in-memory cache:
# { hash: {"response": str, "timestamp": float} }
_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour

def _hash_query(query: str) -> str:
    """Create a normalized hash for a query."""
    normalized = " ".join(query.lower().strip().split())
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def get_cached_response(query: str) -> Optional[str]:
    """Retrieve a response from cache if it exists and is fresh."""
    query_hash = _hash_query(query)
    if query_hash in _MEMORY_CACHE:
        entry = _MEMORY_CACHE[query_hash]
        if time.time() - entry["timestamp"] < CACHE_TTL_SECONDS:
            logger.info(f"Cache hit for query: {query}")
            return entry["response"]
        else:
            # Expired
            del _MEMORY_CACHE[query_hash]
    return None

def set_cached_response(query: str, response: str) -> None:
    """Save a response to the cache."""
    query_hash = _hash_query(query)
    _MEMORY_CACHE[query_hash] = {
        "response": response,
        "timestamp": time.time()
    }
    logger.debug(f"Cached response for query: {query}")
