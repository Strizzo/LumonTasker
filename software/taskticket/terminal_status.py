"""Read-only Trello queue diagnostics; no task selection or printer calls."""
import asyncio
from datetime import datetime, timezone
import threading
import time

import aiohttp


class TerminalStatus:
    def __init__(self, trello, ttl=60):
        self.trello = trello
        self.ttl = ttl
        self._lock = threading.Lock()
        self._cached = None
        self._expires = 0

    def get(self):
        with self._lock:
            if self._cached is not None and time.monotonic() < self._expires:
                return self._cached
            try:
                self._cached = asyncio.run(self._read_queue())
            except aiohttp.ClientResponseError as error:
                self._cached = {"ok": False, "reason": "authentication" if error.status in (401, 403) else "api_error"}
            except (aiohttp.ClientError, asyncio.TimeoutError):
                self._cached = {"ok": False, "reason": "connection"}
            except (TypeError, ValueError, KeyError):
                self._cached = {"ok": False, "reason": "invalid_response"}
            self._cached["checked_at"] = datetime.now(timezone.utc).isoformat()
            self._expires = time.monotonic() + self.ttl
            return self._cached

    async def _read_queue(self):
        if not (self.trello.api_key and self.trello.token and self.trello.board_id):
            return {"ok": False, "reason": "configuration"}
        auth = {"key": self.trello.api_key, "token": self.trello.token}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12)) as session:
            async def read(path, fields):
                async with session.get(self.trello.base_url + "/" + path, params={**auth, "fields": fields, "filter": "open"}) as response:
                    response.raise_for_status()
                    return await response.json()

            lists = await read("boards/" + self.trello.board_id + "/lists", "id,name")
            if not isinstance(lists, list):
                raise ValueError("Invalid queue response")
            by_name = {item["name"].strip().upper(): item["id"] for item in lists}
            queues = {"todo": "TODO", "doing": "DOING", "btn": "BETTER THAN NOTHING"}

            async def count(name):
                if name not in by_name:
                    return 0
                cards = await read("lists/" + by_name[name] + "/cards", "id")
                if not isinstance(cards, list):
                    raise ValueError("Invalid card response")
                return len(cards)

            values = await asyncio.gather(*(count(name) for name in queues.values()))
            return {"ok": True, "counts": dict(zip(queues, values)), "lists_found": {key: name in by_name for key, name in queues.items()}}
