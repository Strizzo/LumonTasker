"""Local selection checks; no network requests or physical printer access."""
import asyncio
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import random
import sys
import unittest

root = Path(__file__).resolve().parents[1] / 'taskticket'
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('task_selector', root / 'core/task_selector.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def card(id, **kwargs): return {'id': id, 'name': 'Task ' + id, **kwargs}


class History:
    def __init__(self, entries=None, skipped=None): self.history = entries or []; self.skipped = skipped or set()
    def get_recently_skipped_tasks(self, days): return self.skipped


class Trello:
    def __init__(self, todo=None, doing=None, btn=None): self.todo = todo or []; self.doing = doing or []; self.btn = btn or []
    async def get_tasks(self): return {'todo': self.todo, 'doing': self.doing}
    async def get_btn_tasks(self): return self.btn


class FakeAI:
    def __init__(self, response): self.response = response; self.calls = 0
    async def process(self, **kwargs): self.calls += 1; return self.response


class Checks(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 26, 12, tzinfo=timezone.utc)
        self.selector = module.TaskSelector(rng=random.Random(12), clock=lambda: self.now, use_ai=False)

    def select(self, trello, history=None):
        return asyncio.run(self.selector.get_next_task(trello, history or History()))

    def test_local_mode_never_calls_ai(self):
        ai = FakeAI('{"task_id":"a"}'); self.selector.llm = ai
        result = self.select(Trello(todo=[card('a')]))
        self.assertEqual(result['task_id'], 'a')
        self.assertEqual(result['selection_method'], 'local')
        self.assertEqual(ai.calls, 0)

    def test_in_progress_before_nonurgent_tasks(self):
        result = self.select(Trello(todo=[card('a')], doing=[card('b')], btn=[card('c')]))
        self.assertEqual(result['task_id'], 'b')

    def test_deadline_overrides_weekend_preference(self):
        result = self.select(Trello(todo=[card('a', due=(self.now - timedelta(hours=3)).isoformat()), card('b', due=(self.now + timedelta(hours=1)).isoformat())], btn=[card('c')]))
        self.assertEqual(result['task_id'], 'a')

    def test_completed_deadline_not_urgent(self):
        self.selector.rng = random.Random(1)
        result = self.select(Trello(todo=[card('a', due=(self.now - timedelta(hours=3)).isoformat(), dueComplete=True)], btn=[card('c')]))
        self.assertEqual(result['task_id'], 'c')

    def test_recent_repeat_and_skipped_are_avoided(self):
        history = History(entries=[{'id':'a','timestamp':self.now.isoformat()}], skipped={'c'})
        result = self.select(Trello(todo=[card('a'),card('b')], doing=[card('c')]), history)
        self.assertEqual(result['task_id'], 'b')

    def test_all_skipped_is_empty_but_all_recent_is_not(self):
        trello = Trello(todo=[card('a')])
        self.assertIsNone(self.select(trello, History(skipped={'a'})))
        self.assertEqual(self.select(trello, History(entries=[{'id':'a','timestamp':self.now.isoformat()}]))['task_id'], 'a')

    def test_provider_failure_falls_back_without_repeated_calls(self):
        self.selector.use_ai = True
        ai = FakeAI('not JSON'); self.selector.llm = ai
        trello = Trello(todo=[card('a')])
        self.assertEqual(self.select(trello)['selection_method'], 'local')
        self.assertEqual(self.select(trello)['selection_method'], 'local')
        self.assertEqual(ai.calls, 1)

    def test_hallucinated_id_cannot_be_selected(self):
        self.selector.use_ai = True
        self.selector.llm = FakeAI('{"task_id":"does-not-exist"}')
        self.assertEqual(self.select(Trello(todo=[card('a')]))['task_id'], 'a')

    def test_optional_ai_valid_id_preserves_trello_title(self):
        self.selector.use_ai = True
        self.selector.llm = FakeAI('{"task_id":"a","title":"invented"}')
        result = self.select(Trello(todo=[card('a')]))
        self.assertEqual(result['ticket_title'], 'Task a')
        self.assertEqual(result['selection_method'], 'qwen')


if __name__ == '__main__': unittest.main()
