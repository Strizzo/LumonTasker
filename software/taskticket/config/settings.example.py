"""Copy to settings.py; credentials are loaded from an untracked .env file."""
import os
from pathlib import Path
from dotenv import load_dotenv

APP_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(APP_ROOT / '.env')

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY', '')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN', '')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID', '')
TRELLO_TODOS_LIST_NAME = 'TODO'
TRELLO_CACHE_DURATION = 60
DEFAULT_MODEL = os.getenv('TASKTICKET_AI_MODEL', 'qwen/qwen3.7-flash')
MAX_TOKENS = 150
DEFAULT_TEMPERATURE = 0.2
PRINTER_VENDOR_ID = int(os.getenv('PRINTER_VENDOR_ID', '0x0416'), 16)
PRINTER_PRODUCT_ID = int(os.getenv('PRINTER_PRODUCT_ID', '0x5011'), 16)
PRINTER_IN_EP = int(os.getenv('PRINTER_IN_EP', '0x82'), 16)
PRINTER_OUT_EP = int(os.getenv('PRINTER_OUT_EP', '0x01'), 16)
PRINTER_DEBUG = os.getenv('PRINTER_DEBUG', 'false').lower() == 'true'
TASK_HISTORY_FILE = os.getenv('TASK_HISTORY_FILE', str(APP_ROOT / 'data/task_history.json'))
MIN_TASK_INTERVAL = 0
