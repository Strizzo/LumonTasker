from typing import Dict, List, Optional
import aiohttp
from config import settings

class TrelloClient:
    def __init__(self):
        self.api_key = settings.TRELLO_API_KEY
        self.token = settings.TRELLO_TOKEN
        self.board_id = settings.TRELLO_BOARD_ID
        self.base_url = "https://api.trello.com/1"

    async def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Dict:
        """Make a request to the Trello API."""
        if params is None:
            params = {}
        
        # Add authentication to params
        params.update({
            'key': self.api_key,
            'token': self.token
        })
        
        full_url = f"{self.base_url}/{endpoint}"
        print(f"Making Trello API request: {method} {full_url}")
        print(f"With params: {params}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, full_url, params=params) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        print(f"Trello API error ({response.status}): {error_text}")
                        raise Exception(f"API Error {response.status}: {error_text}")
                        
                    response_json = await response.json()
                    print(f"Received response: Status {response.status}")
                    return response_json
            except Exception as e:
                print(f"Request error: {str(e)}")
                raise

    async def get_tasks(self) -> Dict[str, List]:
        """Get TODO and DOING tasks."""
        try:
            # Get all lists on the board
            lists = await self._make_request(f'boards/{self.board_id}/lists')
            
            # Find TODO and DOING lists
            todo_list = next((lst for lst in lists if lst['name'].upper() == 'TODO'), None)
            doing_list = next((lst for lst in lists if lst['name'].upper() == 'DOING'), None)
            
            result = {'todo': [], 'doing': []}
            
            # Get cards from TODO list
            if todo_list:
                todo_cards = await self._make_request(f'lists/{todo_list["id"]}/cards')
                result['todo'] = todo_cards
            
            # Get cards from DOING list
            if doing_list:
                doing_cards = await self._make_request(f'lists/{doing_list["id"]}/cards')
                result['doing'] = doing_cards
            
            return result
            
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return {'todo': [], 'doing': []}

    async def get_btn_tasks(self) -> List[Dict]:
        """Get tasks from the 'Better Than Nothing' list."""
        try:
            # Get all lists on the board
            lists = await self._make_request(f'boards/{self.board_id}/lists')
            
            # Find BTN list
            btn_list = next((lst for lst in lists if lst['name'].upper() == 'BETTER THAN NOTHING'), None)
            
            if btn_list:
                btn_cards = await self._make_request(f'lists/{btn_list["id"]}/cards')
                return btn_cards
            
            return []
            
        except Exception as e:
            print(f"Error getting BTN tasks: {e}")
            return []

    async def get_long_term_goals(self) -> List[Dict]:
        """Get long-term goals from dedicated list."""
        try:
            # Get all lists on the board
            lists = await self._make_request(f'boards/{self.board_id}/lists')
            
            # Find Goals list
            goals_list = next((lst for lst in lists if lst['name'].upper() == 'GOALS'), None)
            
            if goals_list:
                goal_cards = await self._make_request(f'lists/{goals_list["id"]}/cards')
                return goal_cards
            
            return []
            
        except Exception as e:
            print(f"Error getting goals: {e}")
            return []

    async def move_to_done(self, task_id: str, source_list: str) -> bool:
        """Move a task to the DONE list."""
        try:
            print(f"Attempting to move task {task_id} from {source_list} to DONE")
            
            # Find DONE list
            lists = await self._make_request(f'boards/{self.board_id}/lists')
            print(f"Retrieved {len(lists)} lists from board")
            
            # Print all list names for debugging
            list_info = [(lst['id'], lst['name']) for lst in lists]
            print(f"Available lists: {list_info}")
            
            done_list = next((lst for lst in lists if lst['name'].upper() == 'DONE'), None)
            
            if not done_list:
                print("Error: DONE list not found on Trello board")
                return False
                
            print(f"Found DONE list with ID: {done_list['id']}")
            
            if source_list in ['TODO', 'DOING']:
                # Move card to DONE list
                print(f"Making API request to move card {task_id} to list {done_list['id']}")
                response = await self._make_request(
                    f'cards/{task_id}/idList',
                    method='PUT',
                    params={'value': done_list['id']}
                )
                print(f"Move card response: {response}")
                return True
            else:
                print(f"Source list '{source_list}' is not in ['TODO', 'DOING'], not moving card")
                return False
        except Exception as e:
            print(f"Error moving task to done: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False