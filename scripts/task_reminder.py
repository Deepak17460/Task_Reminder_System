import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database.db_manager import init_db, load_tasks, add_task, update_task, delete_task, mark_task
from database.model import validate_task_description, validate_priority

# Define project root (one level up from scripts/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Initialize Flask app with correct template and static folders
app = Flask(__name__,
            template_folder=os.path.join(project_root, 'templates'),
            static_folder=os.path.join(project_root, 'static'))
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')  # Use env variable or default

# Directory and file for logs (relative to project root)
LOGS_DIR = os.path.join(project_root, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'task_reminder.log')

# Ensure logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5),  # Rotate at 10MB, keep 5 backups
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# Flask Routes
@app.route('/')
def index():
    logger.info("Rendering index page")
    try:
        tasks = load_tasks()
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        flash('An error occurred while loading tasks.', 'error')
        return render_template('index.html', tasks=[])

@app.route('/add', methods=['POST'])
def add():
    description = request.form.get('description')
    priority = request.form.get('priority', 'Medium')  # Default to Medium

    # Validate description
    is_valid, error_message = validate_task_description(description)
    if not is_valid:
        logger.warning(f"Invalid task description: {error_message}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': error_message, 'status': 'error'})
        flash(error_message, 'error')
        return redirect(url_for('index'))

    # Validate priority
    if not validate_priority(priority):
        logger.warning("Invalid priority provided, defaulting to Medium")
        priority = 'Medium'

    try:
        task_id = add_task(description, priority)
        message = f'Task added: {description} (ID: {task_id}, Priority: {priority})'
        status = 'success'
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        message = 'Failed to add task. Please try again.'
        status = 'error'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'status': status})
    flash(message, status)
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update(task_id):
    new_description = request.form.get('description')
    new_priority = request.form.get('priority')

    # Validate description
    is_valid, error_message = validate_task_description(new_description)
    if not is_valid:
        logger.warning(f"Invalid task description: {error_message}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': error_message, 'status': 'error'})
        flash(error_message, 'error')
        return redirect(url_for('index'))

    # Validate priority
    if not validate_priority(new_priority):
        logger.warning("Invalid priority provided, defaulting to Medium")
        new_priority = 'Medium'

    try:
        if update_task(task_id, new_description, new_priority):
            message = f'Task updated: {new_description} (ID: {task_id}, Priority: {new_priority})'
            status = 'success'
        else:
            message = f'Task ID {task_id} not found.'
            status = 'error'
    except Exception as e:
        logger.error(f"Error updating task ID {task_id}: {e}")
        message = 'Failed to update task. Please try again.'
        status = 'error'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'status': status})
    flash(message, status)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    try:
        if delete_task(task_id):
            message = f'Task ID {task_id} deleted.'
            status = 'success'
        else:
            message = f'Task ID {task_id} not found.'
            status = 'error'
    except Exception as e:
        logger.error(f"Error deleting task ID {task_id}: {e}")
        message = 'Failed to delete task. Please try again.'
        status = 'error'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'status': status})
    flash(message, status)
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete(task_id):
    try:
        if mark_task(task_id, completed=True):
            message = f'Task ID {task_id} marked as completed.'
            status = 'success'
        else:
            message = f'Task ID {task_id} not found.'
            status = 'error'
    except Exception as e:
        logger.error(f"Error marking task ID {task_id} as complete: {e}")
        message = 'Failed to mark task as complete. Please try again.'
        status = 'error'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'status': status})
    flash(message, status)
    return redirect(url_for('index'))

@app.route('/incomplete/<int:task_id>')
def incomplete(task_id):
    try:
        if mark_task(task_id, completed=False):
            message = f'Task ID {task_id} marked as incomplete.'
            status = 'success'
        else:
            message = f'Task ID {task_id} not found.'
            status = 'error'
    except Exception as e:
        logger.error(f"Error marking task ID {task_id} as incomplete: {e}")
        message = 'Failed to mark task as incomplete. Please try again.'
        status = 'error'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'status': status})
    flash(message, status)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Added host and port for broader access