import os
import sys
import threading
import time
import schedule
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

def run_notifications():
    """Run the notify function daily at 8am."""
    logger.info("Starting notification scheduler (daily at 8am)")
    schedule.every().day.at("08:00").do(notify)
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Task Reminder System Runner (Server + Notifications)")
    parser.add_argument('--no-notify', action='store_true', help="Run only the Flask server without notifications")
    args = parser.parse_args()

    if not args.no_notify:
        # Start notifications in a separate thread
        notify_thread = threading.Thread(target=run_notifications, daemon=True)
        notify_thread.start()
        logger.info("Started Flask server and notification scheduler")
    else:
        logger.info("Started Flask server without notification scheduler")

    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')