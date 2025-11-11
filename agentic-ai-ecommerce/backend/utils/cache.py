import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple in-memory cache."""
    def __init__(self):
        self.cache = {}
    def get(self, key: str):
        return self.cache.get(key)
    def set(self, key: str, value, ttl: int = None):
        self.cache[key] = value
        logger.debug(f"Cache set: {key}")
    def delete(self, key: str):
        self.cache.pop(key, None)
    def clear_pattern(self, pattern: str):
        keys_to_delete = [k for k in self.cache.keys() if pattern.replace("*", "") in k]
        for k in keys_to_delete:
            del self.cache[k]

cache_manager = CacheManager()
