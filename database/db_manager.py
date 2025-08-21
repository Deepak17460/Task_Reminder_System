import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Optional

# Import from our model
from .model import Task, TaskSchema, Priority, get_current_timestamp, validate_priority, validate_task_description

# Get the project root directory (this file is in database/db_manager.py, so go up one level)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Directory and file for SQLite database (root level)
DB_DIR = os.path.join(PROJECT_ROOT, 'database')
DB_FILE = os.path.join(DB_DIR, 'tasks.db')

# Ensure database directory exists
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Configure logging (shared with task_reminder.py)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize SQLite database with all schemas."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create all tables using schemas from model
    for schema in TaskSchema.get_all_schemas():
        cursor.execute(schema)
    
    conn.commit()
    conn.close()
    logger.info("Initialized SQLite database at %s", DB_FILE)

def load_tasks() -> List[Task]:
    """Load tasks from database and return as Task objects."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    cursor = conn.cursor()
    cursor.execute('SELECT id, description, completed, created_at, priority FROM tasks')
    
    tasks = []
    for row in cursor.fetchall():
        try:
            task = Task.from_db_row(row)
            tasks.append(task)
        except Exception as e:
            logger.error("Error loading task ID %s: %s", row.get('id'), e)
    
    conn.close()
    logger.info("Loaded %d tasks from database", len(tasks))
    return tasks

def add_task(description: str, priority: str = 'Medium') -> Optional[int]:
    """Add a new task with validation."""
    # Validate inputs
    is_valid, error_msg = validate_task_description(description)
    if not is_valid:
        logger.error("Invalid task description: %s", error_msg)
        return None
    
    if not validate_priority(priority):
        logger.error("Invalid priority: %s", priority)
        return None
    
    # Generate fresh timestamp
    timestamp = get_current_timestamp()
    logger.info("Generated timestamp: %s", timestamp)  # Debug log
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (description, completed, created_at, priority) VALUES (?, ?, ?, ?)',
        (description.strip(), False, timestamp, priority)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    logger.info("Added task ID %d: %s (Priority: %s) at %s", task_id, description.strip(), priority, timestamp)
    return task_id

def get_task_by_id(task_id: int) -> Optional[Task]:
    """Get a single task by ID."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, description, completed, created_at, priority FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        try:
            return Task.from_db_row(row)
        except Exception as e:
            logger.error("Error loading task ID %d: %s", task_id, e)
    
    return None

def update_task(task_id: int, new_description: str, new_priority: str) -> bool:
    """Update a task with validation."""
    # Validate inputs
    is_valid, error_msg = validate_task_description(new_description)
    if not is_valid:
        logger.error("Invalid task description: %s", error_msg)
        return False
    
    if not validate_priority(new_priority):
        logger.error("Invalid priority: %s", new_priority)
        return False
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET description = ?, priority = ? WHERE id = ?', 
        (new_description.strip(), new_priority, task_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected > 0:
        logger.info("Updated task ID %d to description: %s, priority: %s", task_id, new_description.strip(), new_priority)
        return True
    else:
        logger.warning("Failed to update task ID %d: not found", task_id)
        return False

def delete_task(task_id: int) -> bool:
    """Delete a task."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected > 0:
        logger.info("Deleted task ID %d", task_id)
        return True
    else:
        logger.warning("Failed to delete task ID %d: not found", task_id)
        return False

def mark_task(task_id: int, completed: bool = True) -> bool:
    """Mark task as completed or incomplete."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    status = "completed" if completed else "incomplete"
    if affected > 0:
        logger.info("Marked task ID %d as %s", task_id, status)
        return True
    else:
        logger.warning("Failed to mark task ID %d as %s: not found", task_id, status)
        return False

def get_tasks_by_priority(priority: Priority) -> List[Task]:
    """Get all tasks with specific priority."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, description, completed, created_at, priority FROM tasks WHERE priority = ?', (priority.value,))
    
    tasks = []
    for row in cursor.fetchall():
        try:
            task = Task.from_db_row(row)
            tasks.append(task)
        except Exception as e:
            logger.error("Error loading task ID %s: %s", row.get('id'), e)
    
    conn.close()
    return tasks

def get_incomplete_tasks() -> List[Task]:
    """Get all incomplete tasks."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, description, completed, created_at, priority FROM tasks WHERE completed = 0')
    
    tasks = []
    for row in cursor.fetchall():
        try:
            task = Task.from_db_row(row)
            tasks.append(task)
        except Exception as e:
            logger.error("Error loading task ID %s: %s", row.get('id'), e)
    
    conn.close()
    return tasks

# Legacy functions for backward compatibility (if other parts of your code use them)
def format_datetime(dt):
    """Legacy function - use get_current_timestamp() instead."""
    hour = dt.hour % 12 or 12
    am_pm = 'am' if dt.hour < 12 else 'pm'
    return f"{dt.day} {dt.strftime('%B %Y, %I')}{am_pm}"