from typing import Dict, Optional, List, Set
from datetime import datetime, timedelta
import json
from processors.json_processor import extract_json
from processors.llm_processor import LLMProcessor
from config.user_preferences import USER_BIO

class TaskSelector:
    def __init__(self):
        self.llm = LLMProcessor()

    async def get_next_task(self, trello_client, history_manager) -> Optional[Dict]:
        try:
            todos = await trello_client.get_tasks()
            goals = await trello_client.get_long_term_goals()
            btn_tasks = await trello_client.get_btn_tasks()
            
            recent_history = [
                task for task in history_manager.get_recent_tasks()
                if datetime.fromisoformat(task['timestamp']) > datetime.now() - timedelta(days=1)
            ]

            # Get all skipped task IDs using the new method (7-day cooldown period)
            recently_skipped_ids = history_manager.get_recently_skipped_tasks(days=7)
            print(f"Found {len(recently_skipped_ids)} recently skipped tasks to avoid")
            for task_id in recently_skipped_ids:
                print(f"  - Will avoid skipped task: {task_id}")

            # Filter out tasks with skipped IDs before passing to the LLM
            filtered_todos = {'todo': [], 'doing': []}
            
            # Process TODO list
            for task in todos['todo']:
                if task['id'] not in recently_skipped_ids:
                    filtered_todos['todo'].append(task)
                else:
                    print(f"Filtering out skipped task from TODO: {task['id']} - {task.get('name', '')}")
                    
            # Process DOING list
            for task in todos['doing']:
                if task['id'] not in recently_skipped_ids:
                    filtered_todos['doing'].append(task)
                else:
                    print(f"Filtering out skipped task from DOING: {task['id']} - {task.get('name', '')}")
            
            print(f"Original TODO count: {len(todos['todo'])}, Filtered: {len(filtered_todos['todo'])}")
            print(f"Original DOING count: {len(todos['doing'])}, Filtered: {len(filtered_todos['doing'])}")
                    
            # Filter BTN tasks
            filtered_btn_tasks = []
            for task in btn_tasks:
                if task['id'] not in recently_skipped_ids:
                    filtered_btn_tasks.append(task)
                else:
                    print(f"Filtering out skipped BTN task: {task['id']} - {task.get('name', '')}")
                    
            print(f"Original BTN count: {len(btn_tasks)}, Filtered: {len(filtered_btn_tasks)}")

            # Use filtered tasks for the prompt
            prompt = self._create_prompt(USER_BIO, recent_history, filtered_todos, filtered_btn_tasks, goals, recently_skipped_ids)
            
            print("\nSending request to LLM...")
            response = await self.llm.process(
                prompt=prompt,
                model_type='smart',
                system_prompt="You are a task selection AI. Only respond with the exact JSON format requested, no additional text.",
                temperature=0.7
            )
            
            print("\nReceived LLM response:")
            print(response)

            task_data = self._parse_response(response)
            if task_data:
                # Double-check the suggested task wasn't recently skipped (as a safeguard)
                task_id = task_data.get('task_id')
                if task_id in recently_skipped_ids:
                    print(f"ERROR: Task {task_id} was recently skipped but still suggested. Rejecting.")
                    return None
                    
                # Check if this task was selected multiple times in recent history
                task_occurrences = self._count_recent_occurrences(task_id, history_manager)
                if task_occurrences >= 3:
                    print(f"Warning: Task {task_id} has been selected {task_occurrences} times recently.")
                    
                # Normalize the task data structure
                return self._normalize_task_data(task_data)
            return None

        except Exception as e:
            print(f"\nError getting next task: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def _count_recent_occurrences(self, task_id: str, history_manager) -> int:
        """Count how many times a task has appeared in the recent history (last 20 entries)."""
        count = 0
        for entry in history_manager.history[-20:]:
            if entry.get('id') == task_id:
                count += 1
        return count

    def _create_prompt(self, user_bio, history, todos, btn_tasks, goals, skipped_task_ids: Set[str]) -> str:
        current_time = datetime.now()
        time_info = {
            'hour': current_time.hour,
            'weekday': current_time.strftime('%A'),
            'date': current_time.strftime('%Y-%m-%d'),
            'time': current_time.strftime('%H:%M')
        }

        # Format the skipped tasks list to be more prominent
        skipped_tasks_formatted = "\n".join([f"- {task_id}" for task_id in skipped_task_ids])

        return f"""As a task selection AI, analyze the following context and select the most appropriate next task.

Current Time Context:
Time: {time_info['time']}
Day: {time_info['weekday']}
Date: {time_info['date']}

User Bio:
{user_bio}

Recent Task History:
{json.dumps(history, indent=2)}

Available TODO Tasks:
{json.dumps(todos['todo'], indent=2)}

Current DOING Tasks:
{json.dumps(todos['doing'], indent=2)}

"Better Than Nothing" Tasks:
{json.dumps(btn_tasks, indent=2)}

Long-term Goals:
{json.dumps(goals, indent=2)}

IMPORTANT GUIDELINES:
1. Prioritize work in progress, then expired, then expiring in the next 2 hours, then everything else.
2. Mix work and fun tasks - strongly consider selecting a "Better Than Nothing" fun task at least 30% of the time
3. Don't overlook tasks without deadlines - these need attention too
4. Consider the current time of day and day of week when selecting tasks
5. For afternoons, consider lighter tasks
6. For weekends and evenings, strongly prefer fun or relaxing tasks
7. On weekends, prioritize BTN tasks over work tasks by a 2:1 ratio, unless there are tasks expiring/expired in the weekend 

⚠️ CRITICAL: DO NOT SUGGEST ANY OF THESE SKIPPED TASKS ⚠️
These tasks have been explicitly skipped by the user and must be avoided:
{skipped_tasks_formatted}

Select a task and respond ONLY with a JSON object in this exact format:
{{
    "task_id": "original task id",
    "title": "task title from trello",
    "ticket_title": "reformatted task title for ticket",
    "estimated_time": "estimated time in minutes",
    "challenge_time": "optional challenge time in minutes",
    "motivation": "brief motivational message",
    "source_list": "TODO/DOING/BTN"
}}"""

    def _parse_response(self, response: str) -> Optional[Dict]:
        json_str = extract_json(response)
        if not json_str:
            print("Could not find valid JSON in response")
            return None

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"\nJSON Parse Error: {str(e)}")
            print(f"Response that couldn't be parsed: {json_str}")
            return None

    def _normalize_task_data(self, task_data: Dict) -> Dict:
        """Ensure task data has all required fields with correct names."""
        normalized = {
            'task_id': task_data.get('task_id', ''),
            'title': task_data.get('title', ''),
            'ticket_title': task_data.get('ticket_title', task_data.get('title', '')),
            'estimated_time': task_data.get('estimated_time', '15'),
            'challenge_time': task_data.get('challenge_time', None),
            'motivation': task_data.get('motivation', 'You can do this!'),
            'source_list': task_data.get('source_list', 'TODO')
        }
        
        # Ensure numeric fields are strings
        normalized['estimated_time'] = str(normalized['estimated_time'])
        if normalized['challenge_time']:
            normalized['challenge_time'] = str(normalized['challenge_time'])
            
        return normalized