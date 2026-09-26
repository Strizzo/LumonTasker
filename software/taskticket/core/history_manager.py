from typing import Dict, List, Set
import json
import os
from datetime import datetime, timedelta
from config import settings

class HistoryManager:
    def __init__(self):
        self.history = self.load_history()
        self.skipped_task_cache = self._build_skipped_task_cache()

    def load_history(self) -> List[Dict]:
        try:
            if os.path.exists(settings.TASK_HISTORY_FILE):
                with open(settings.TASK_HISTORY_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading task history: {e}")
        return []

    def save_history(self):
        try:
            os.makedirs(os.path.dirname(settings.TASK_HISTORY_FILE), exist_ok=True)
            with open(settings.TASK_HISTORY_FILE, 'w') as f:
                json.dump(self.history, f)
        except Exception as e:
            print(f"Error saving task history: {e}")

    def _build_skipped_task_cache(self) -> Dict[str, datetime]:
        """Build a cache of skipped task IDs with their skip time."""
        skipped_tasks = {}
        for entry in self.history:
            if entry.get('skipped', False) and not entry.get('completed', False):
                task_id = entry.get('id')
                if task_id:
                    try:
                        # Use the most recent skip time
                        skip_time = datetime.fromisoformat(entry.get('skip_time', entry.get('timestamp')))
                        if task_id not in skipped_tasks or skip_time > skipped_tasks[task_id]:
                            skipped_tasks[task_id] = skip_time
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing date for skipped task {task_id}: {e}")
        return skipped_tasks

    def add_task(self, task: Dict):
        task_entry = {
            'id': task['task_id'],
            'title': task['ticket_title'],
            'timestamp': datetime.now().isoformat(),
            'completed': False,
            'task': dict(task)
        }
        self.history.append(task_entry)
        self.save_history()

    def add_skipped_task(self, task_id: str):
        """Mark a task as skipped in the history."""
        skipped_count = 0
        current_time = datetime.now()
        
        # Update the history entries
        for entry in self.history:
            if entry['id'] == task_id and not entry.get('completed', False):
                entry['skipped'] = True
                entry['skip_time'] = current_time.isoformat()
                skipped_count += 1
        
        # Update the skipped task cache
        self.skipped_task_cache[task_id] = current_time
        
        print(f"Marked {skipped_count} entries for task {task_id} as skipped")
        self.save_history()

    def is_task_skipped_recently(self, task_id: str, cooldown_days: int = 7) -> bool:
        """Check if a task was skipped recently and is still in cooldown period."""
        if task_id not in self.skipped_task_cache:
            return False
            
        skip_time = self.skipped_task_cache[task_id]
        cooldown_time = datetime.now() - timedelta(days=cooldown_days)
        return skip_time > cooldown_time

    def get_recently_skipped_tasks(self, days: int = 7) -> Set[str]:
        """Get a set of task IDs that were skipped within the specified days."""
        current_time = datetime.now()
        cooldown_time = current_time - timedelta(days=days)
        
        return {
            task_id for task_id, skip_time in self.skipped_task_cache.items()
            if skip_time > cooldown_time
        }

    def mark_completed(self, task_id: str):
        # Reusable tasks can appear more than once; close the latest issue so
        # a page reload cannot restore a task that was just completed.
        for entry in reversed(self.history):
            if entry['id'] == task_id and not entry.get('completed', False):
                entry['completed'] = True
                entry['completion_time'] = datetime.now().isoformat()
                # Also remove from skipped cache if present
                if task_id in self.skipped_task_cache:
                    del self.skipped_task_cache[task_id]
                break
        self.save_history()

    def get_recent_tasks(self, limit: int = 10) -> List[Dict]:
        return self.history[-limit:]
