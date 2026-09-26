"""Run with the Pi venv against the staged terminal_status.py; fake HTTP only."""
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch
import aiohttp

path = Path(__file__).resolve().parents[1] / 'taskticket' / 'terminal_status.py'
spec = importlib.util.spec_from_file_location('terminal_status', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Response:
    def __init__(self, data): self.data = data
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass
    def raise_for_status(self): pass
    async def json(self): return self.data


class Session:
    calls = []
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass
    def get(self, url, params):
        self.calls.append((url, params))
        if url.endswith('/lists'):
            return Response([{'id': 'a', 'name': 'TODO'}, {'id': 'b', 'name': 'DOING'}, {'id': 'c', 'name': 'Better than nothing'}])
        counts = {'a': 11, 'b': 0, 'c': 19}
        return Response([{'id': str(i)} for i in range(counts[url.split('/')[-2]])])


class Checks(unittest.TestCase):
    def setUp(self):
        self.client = SimpleNamespace(api_key='secret-key', token='secret-token', board_id='board', base_url='https://api.trello.com/1')

    def test_read_only_counts_and_cache(self):
        Session.calls = []
        with patch.object(module.aiohttp, 'ClientSession', return_value=Session()):
            status = module.TerminalStatus(self.client)
            first, second = status.get(), status.get()
        self.assertEqual(first['counts'], {'todo': 11, 'doing': 0, 'btn': 19})
        self.assertEqual(len(Session.calls), 4)
        self.assertIs(first, second)
        self.assertTrue(all(p['fields'] == 'id' for url, p in Session.calls if url.endswith('/cards')))
        self.assertNotIn('secret', str(first))

    def test_failed_auth_does_not_masquerade_as_empty_queue(self):
        error = aiohttp.ClientResponseError(None, (), status=401, message='secret-token')
        status = module.TerminalStatus(self.client)
        with patch.object(status, '_read_queue', AsyncMock(side_effect=error)):
            result = status.get()
        self.assertFalse(result['ok'])
        self.assertEqual(result['reason'], 'authentication')
        self.assertNotIn('counts', result)
        self.assertNotIn('secret-token', str(result))

    def test_timeout_and_configuration(self):
        status = module.TerminalStatus(self.client)
        with patch.object(status, '_read_queue', AsyncMock(side_effect=asyncio.TimeoutError)):
            self.assertEqual(status.get()['reason'], 'connection')
        self.client.token = ''
        self.assertEqual(module.TerminalStatus(self.client).get()['reason'], 'configuration')


if __name__ == '__main__': unittest.main()
