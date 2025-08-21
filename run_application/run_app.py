import os
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Configure logging
LOGS_DIR = os.path.join(project_root, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'task_reminder.log')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from scripts.task_reminder import app
from notify.notify_user import notify
from database.db_manager import init_db

# Load environment variables from .env file
load_dotenv()

# Initialize database
init_db()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Task Reminder System")
    parser.add_argument('command', nargs='?', choices=['notify'], help="Run notification command")
    args = parser.parse_args()

    if args.command == 'notify':
        notify()
    else:
        app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')