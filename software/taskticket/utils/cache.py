# Caching utilities
import time
from typing import Any, Dict
import json

class Cache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Any:
        """Get value from cache if it exists and hasn't expired."""
        if key in self._cache:
            item = self._cache[key]
            if item['expire_time'] > time.time():
                return item['value']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration time in seconds."""
        self._cache[key] = {
            'value': value,
            'expire_time': time.time() + expire
        }

    def clear(self):
        """Clear all cached items."""
        self._cache.clear()

    def cleanup(self):
        """Remove expired items from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expire_time'] <= current_time
        ]
        for key in expired_keys:
            del self._cache[key]