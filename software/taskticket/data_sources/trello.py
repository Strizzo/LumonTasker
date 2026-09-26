"""Trello access with bounded requests and credential-safe failures."""
import asyncio
from typing import Dict, List
import aiohttp
from config import settings


class TrelloUnavailable(RuntimeError):
    pass


class TrelloClient:
    def __init__(self):
        self.api_key = settings.TRELLO_API_KEY
        self.token = settings.TRELLO_TOKEN
        self.board_id = settings.TRELLO_BOARD_ID
        self.base_url = 'https://api.trello.com/1'

    async def _make_request(self, endpoint, method='GET', params=None):
        auth = {**(params or {}), 'key': self.api_key, 'token': self.token}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.request(method, self.base_url + '/' + endpoint, params=auth) as response:
                    if response.status >= 400:
                        raise TrelloUnavailable('Trello request failed (HTTP %s).' % response.status)
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            # Exception URLs can contain key/token; never log or return them.
            raise TrelloUnavailable('Unable to reach Trello or read its response.') from None

    async def _lists(self):
        lists = await self._make_request('boards/%s/lists' % self.board_id, params={'fields': 'id,name', 'filter': 'open'})
        return {item['name'].strip().upper(): item['id'] for item in lists}

    async def _cards(self, list_id):
        return await self._make_request('lists/%s/cards' % list_id, params={'fields': 'id,name,desc,due,dueComplete', 'filter': 'open'})

    async def get_tasks(self) -> Dict[str, List]:
        lists = await self._lists()
        return {key: await self._cards(lists[name]) if name in lists else [] for key, name in [('todo', 'TODO'), ('doing', 'DOING')]}

    async def get_btn_tasks(self) -> List[Dict]:
        lists = await self._lists()
        return await self._cards(lists['BETTER THAN NOTHING']) if 'BETTER THAN NOTHING' in lists else []

    async def get_long_term_goals(self) -> List[Dict]:
        lists = await self._lists()
        return await self._cards(lists['GOALS']) if 'GOALS' in lists else []

    async def move_to_done(self, task_id, source_list):
        if source_list not in ('TODO', 'DOING'):
            return False
        lists = await self._lists()
        if 'DONE' not in lists:
            return False
        await self._make_request('cards/%s/idList' % task_id, method='PUT', params={'value': lists['DONE']})
        return True
