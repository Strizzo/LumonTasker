"""Exercise real route bodies with in-memory dependencies, never hardware."""
import ast
import asyncio
from datetime import datetime
import time
import json
import os
import tempfile
from datetime import timedelta
from typing import Dict, List, Set
from pathlib import Path
from types import SimpleNamespace
import unittest

class Unavailable(RuntimeError): pass
class Loop:
    def run_until_complete(self, value): return asyncio.run(value)
class Response(dict):
    def __init__(self, value):
        super().__init__(value); self.headers={}; self.status_code=200
class History:
    def __init__(self): self.issued=[]; self.completed=[]; self.history=[]
    def add_task(self, task): self.issued.append(task)
    def mark_completed(self, id): self.completed.append(id)
class Manager:
    def __init__(self):
        self.history=History(); self.printed=[]; self.moved=[]; self.current_task=None; self.trello=None
        async def select(*args): return {'task_id':'a','source_list':'TODO'}
        self.selector=SimpleNamespace(get_next_task=select)
    def print_task_ticket(self, task): self.printed.append(task)
    async def move_task_to_done(self, id, source): self.moved.append(id); return True

class Routes(unittest.TestCase):
    def setUp(self):
        self.manager=Manager()
        self.namespace={'task_manager':self.manager,'loop':Loop(),'jsonify':Response,'TrelloUnavailable':Unavailable,
                        'request':SimpleNamespace(json={},args={}), 'logger':SimpleNamespace(error=lambda *a,**kw:None),
                        'datetime':datetime, 'time':time, 'asyncio':asyncio,
                        'render_template':lambda name:{'template':name}, 'make_response':Response}
        self.namespace['request'].get_json = lambda **kw: self.namespace['request'].json
        self.namespace['request'].get_data = lambda: b''
        tree=ast.parse((Path(__file__).resolve().parents[1]/'taskticket/main.py').read_text())
        for function in tree.body:
            if isinstance(function,ast.FunctionDef) and function.name in ('print_task','list_tasks','complete_task','get_current_task','display'):
                function.decorator_list=[]
                exec(compile(ast.Module(body=[function],type_ignores=[]),'main.py','exec'),self.namespace)

    def test_trello_failure_never_prints_or_changes_history(self):
        async def failure(*args): raise Unavailable('redacted')
        self.manager.selector.get_next_task=failure
        result,code=self.namespace['print_task']()
        self.assertEqual(code,503); self.assertFalse(result['success'])
        self.assertEqual(self.manager.printed,[]); self.assertEqual(self.manager.history.issued,[])

    def test_request_prints_once_after_valid_selection(self):
        result,code=self.namespace['print_task']()
        self.assertEqual(code,200); self.assertTrue(result['success'])
        self.assertEqual(len(self.manager.printed),1); self.assertEqual(len(self.manager.history.issued),1)

    def test_failed_ticket_does_not_record_an_issued_task(self):
        def failure(task): raise RuntimeError('Synthetic printer failure')
        self.manager.print_task_ticket=failure
        result,code=self.namespace['print_task']()
        self.assertEqual(code,500); self.assertFalse(result['success'])
        self.assertEqual(self.manager.history.issued,[])
        self.assertIsNone(self.manager.current_task)

    def test_browsing_does_not_print_or_issue_and_is_not_cached(self):
        async def listing(*args): return [{'task_id':'b','title':'Pick this','source_list':'TODO'}]
        self.manager.selector.list_tasks=listing
        response=self.namespace['list_tasks']()
        self.assertEqual(response['tasks'][0]['task_id'],'b')
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertEqual(self.manager.printed,[]); self.assertEqual(self.manager.history.issued,[])

    def test_manual_issue_uses_server_task_not_browser_title_or_list(self):
        async def manual(trello, task_id):
            self.assertEqual(task_id,'b')
            return {'task_id':'b','title':'Trusted title','source_list':'BTN','selection_method':'manual'}
        async def automatic(*args): self.fail('Manual choice must not invoke automatic selection')
        self.manager.selector.get_task_by_id=manual
        self.manager.selector.get_next_task=automatic
        self.namespace['request'].json={'task_id':'b','title':'Forged','source_list':'DONE'}
        response,code=self.namespace['print_task']()
        self.assertEqual(code,200)
        self.assertEqual(response['task']['title'],'Trusted title')
        self.assertEqual(response['task']['source_list'],'BTN')
        self.assertEqual(len(self.manager.printed),1); self.assertEqual(len(self.manager.history.issued),1)
        self.assertEqual(self.manager.current_task,response['task'])

    def test_manual_stale_card_never_falls_back_to_another_task(self):
        async def missing(*args): return None
        self.manager.selector.get_task_by_id=missing
        self.namespace['request'].json={'task_id':'gone'}
        response,code=self.namespace['print_task']()
        self.assertEqual(code,404)
        self.assertIn('no longer available',response['message'])
        self.assertEqual(self.manager.printed,[]); self.assertEqual(self.manager.history.issued,[])

    def test_manual_outage_returns_error_without_printing(self):
        async def failure(*args): raise Unavailable('redacted')
        self.manager.selector.get_task_by_id=failure
        self.manager.selector.list_tasks=failure
        self.namespace['request'].json={'task_id':'b'}
        self.assertEqual(self.namespace['print_task']()[1],503)
        listing=self.namespace['list_tasks']()
        self.assertEqual(listing.status_code,503)
        self.assertFalse(listing['success'])
        self.assertEqual(self.manager.printed,[]); self.assertEqual(self.manager.history.issued,[])

    def test_invalid_manual_ids_are_rejected_before_selection(self):
        for data in [{'task_id':None},{'task_id':''},{'task_id':[]},{'task_id':' '},['a']]:
            self.namespace['request'].json=data
            self.assertEqual(self.namespace['print_task']()[1],400)
        self.assertEqual(self.manager.printed,[])

    def test_malformed_json_cannot_accidentally_issue_an_automatic_task(self):
        self.namespace['request'].json=None
        self.namespace['request'].get_data=lambda: b'{"task_id":'
        self.assertEqual(self.namespace['print_task']()[1],400)
        self.assertEqual(self.manager.printed,[])

    def test_btn_completion_does_not_move_reusable_card(self):
        self.namespace['request'].json={'task_id':'a','source_list':'BTN'}
        result,code=self.namespace['complete_task']()
        self.assertEqual(code,200); self.assertTrue(result['success'])
        self.assertEqual(self.manager.moved,[]); self.assertEqual(self.manager.history.completed,['a'])

    def test_default_layout_and_whitelisted_optional_layout(self):
        for theme,template in [(None,'terminal.html'),('mdr','terminal_mdr.html'),('../../private','terminal.html')]:
            self.namespace['request'].args={} if theme is None else {'theme':theme}
            response=self.namespace['display']()
            self.assertEqual(response['template'],template)
            self.assertEqual(response.headers['Cache-Control'],'no-store')

    def test_restoring_task_preserves_start_without_print_or_history_write(self):
        stamp=datetime.now().isoformat()
        task={'task_id':'a','source_list':'TODO','estimated_time':'20'}
        self.manager.history.history=[{'id':'a','timestamp':stamp,'task':task}]
        response=self.namespace['get_current_task']()
        self.assertEqual(response['task'],task)
        self.assertEqual(response['started_at'],datetime.fromisoformat(stamp).timestamp()*1000)
        self.assertEqual(self.manager.current_task,task)
        self.assertEqual(self.manager.printed,[]); self.assertEqual(self.manager.history.issued,[])

    def test_finished_and_old_assignments_are_not_restored(self):
        for extra in [{'completed':True},{'skipped':True},{'timestamp':datetime.fromtimestamp(time.time()-13*3600).isoformat()}]:
            self.manager.history.history=[{'id':'a','timestamp':datetime.now().isoformat(),**extra}]
            self.assertIsNone(self.namespace['get_current_task']()['task'])
        self.assertEqual(self.manager.printed,[])

    def test_legacy_btn_assignment_recovers_correct_source_without_reissuing(self):
        async def card(*args,**kwargs): return {'id':'a','name':'An activity','idList':'reusable'}
        async def lists(): return {'TODO':'todo','DOING':'doing','BETTER THAN NOTHING':'reusable'}
        self.manager.trello=SimpleNamespace(_make_request=card,_lists=lists)
        self.manager.selector._ticket=lambda card,mode:{'task_id':card['id'],'source_list':card['_source']}
        self.manager.history.history=[{'id':'a','timestamp':datetime.now().isoformat()}]
        self.assertEqual(self.namespace['get_current_task']()['task']['source_list'],'BTN')
        self.assertEqual(self.manager.printed,[]); self.assertEqual(self.manager.history.issued,[])

    def test_restore_outage_does_not_hide_as_empty_queue(self):
        async def failure(*args,**kwargs): raise Unavailable('redacted')
        self.manager.trello=SimpleNamespace(_make_request=failure)
        self.manager.history.history=[{'id':'a','timestamp':datetime.now().isoformat()}]
        self.assertEqual(self.namespace['get_current_task']().status_code,503)
        self.assertEqual(self.manager.printed,[])

    def test_repeated_task_completion_closes_latest_issue_in_saved_history(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'taskticket/core/history_manager.py').read_text())
        source=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='HistoryManager')
        with tempfile.TemporaryDirectory() as folder:
            settings=SimpleNamespace(TASK_HISTORY_FILE=os.path.join(folder,'history.json'))
            namespace={'Dict':Dict,'List':List,'Set':Set,'json':json,'os':os,'datetime':datetime,'timedelta':timedelta,'settings':settings}
            exec(compile(ast.Module(body=[source],type_ignores=[]),'history_manager.py','exec'),namespace)
            history=namespace['HistoryManager']()
            task={'task_id':'repeat','ticket_title':'A reusable task','estimated_time':'15','source_list':'BTN'}
            history.add_task(task)
            history.add_skipped_task('repeat')
            history.add_task(task)
            history.mark_completed('repeat')
            reopened=namespace['HistoryManager']()
            self.assertTrue(reopened.history[-1]['completed'])
            self.assertEqual(reopened.history[-1]['task'],task)
            self.assertFalse(reopened.history[0]['completed'])

if __name__=='__main__': unittest.main()
