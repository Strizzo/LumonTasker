from typing import Dict, Optional
from datetime import datetime
from core.history_manager import HistoryManager
from core.task_selector import TaskSelector
from data_sources.trello import TrelloClient
from printer.thermal_printer import ThermalPrinter
import random


class TaskTicketManager:
    def __init__(self):
        self.trello = TrelloClient()
        self.history = HistoryManager()
        self.selector = TaskSelector()
        self.printer = ThermalPrinter()
        self.current_task = None
        self.last_suggested_task_id = None
        self.consecutive_same_task_count = 0

    def print_task_ticket(self, task: Dict):
        """Print the task ticket."""
        tf = self.printer.format
        ticket_text = (
            f"{tf.create_header('TASK TICKET')}\n"
            f"{tf.BOLD_ON}{task['ticket_title']}{tf.BOLD_OFF}\n\n"
            f"{'Focus session' if task.get('selection_method') else 'Estimated time'}: {task['estimated_time']} minutes\n"
        )
        if task.get('challenge_time'):
            ticket_text += f"Challenge: Complete in {task['challenge_time']} minutes!\n"
        ticket_text += f"\n{task['motivation']}\n\n"
        ticket_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        # TODO this is temporary
        estimated_time = int(task['estimated_time'])
        base_value = (estimated_time / 60) * 50  # 60 minutes = 50 euros as mean
        variation = random.uniform(0.6, 1.4)  # Random factor between 0.6 and 1.4
        value = round(base_value * variation / 10) * 10  # Round to nearest 10
        ticket_text += f"\nValue: {value} EUR\n"
        if not self.printer.print_text(ticket_text, logo=True):
            raise RuntimeError('The task ticket could not be printed.')

    async def move_task_to_done(self, task_id: str, source_list: str):
        return await self.trello.move_to_done(task_id, source_list)

    async def run(self):
        """Main loop for the task ticket manager."""
        while True:
            try:
                input("Press Enter to get a new task (or Ctrl+C to exit)...")
                print("\nFetching next task...")
                task = await self.selector.get_next_task(self.trello, self.history)
                
                if task:
                    # Check if we're suggesting the same task repeatedly
                    if task['task_id'] == self.last_suggested_task_id:
                        self.consecutive_same_task_count += 1
                        if self.consecutive_same_task_count >= 3:
                            print(f"\nWARNING: Same task suggested {self.consecutive_same_task_count} times in a row!")
                            print(f"Automatically marking task {task['task_id']} as skipped to break the loop.")
                            self.history.add_skipped_task(task['task_id'])
                            self.consecutive_same_task_count = 0
                            self.last_suggested_task_id = None
                            print("\nTrying again with a different task...")
                            task = await self.selector.get_next_task(self.trello, self.history)
                            if not task:
                                print("Still couldn't find a suitable task. Please check your Trello board.")
                                continue
                    else:
                        self.consecutive_same_task_count = 0
                        self.last_suggested_task_id = task['task_id']
                
                    print("\nTask selected successfully!")
                    self.current_task = task
                    self.print_task_ticket(task)
                    self.history.add_task(task)

                    if task['source_list'] in ['TODO', 'DOING']:
                        while True:
                            response = input("\nHave you completed this task? (y/n/q to get new task): ").lower()
                            if response == 'y':
                                if await self.move_task_to_done(task['task_id'], task['source_list']):
                                    self.history.mark_completed(task['task_id'])
                                    print("Task moved to DONE!")
                                break
                            elif response in ['n', 'q']:
                                if response == 'n':
                                    self.history.add_skipped_task(task['task_id'])
                                    print("Task marked as skipped. I'll avoid suggesting it again soon.")
                                print("No problem! Keep at it!" if response == 'n' else "")
                                break
                else:
                    print("\nNo task was selected. Please check the error messages above.")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError in main loop: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
