"""
Database models and schema definitions for Task Reminder System.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(Enum):
    """Task priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@dataclass
class Task:
    """Task model representing a single task."""
    id: Optional[int] = None
    description: str = ""
    completed: bool = False
    created_at: str = ""
    priority: str = "Medium"  # Changed to string instead of Priority enum
    
    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at,
            'priority': self.priority
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary."""
        priority = data.get('priority', 'Medium')
        try:
            # Validate and convert to string if it's a Priority enum
            if isinstance(priority, Priority):
                priority = priority.value
            elif not validate_priority(priority):
                priority = 'Medium'  # Default if invalid
        except ValueError:
            priority = 'Medium'
        return cls(
            id=data.get('id'),
            description=data.get('description', ''),
            completed=bool(data.get('completed', False)),
            created_at=data.get('created_at', ''),
            priority=priority
        )
    
    @classmethod
    def from_db_row(cls, row) -> 'Task':
        """Create task from database row."""
        priority = row['priority']
        try:
            # Ensure priority is a string matching Priority enum values
            if not validate_priority(priority):
                priority = 'Medium'  # Default if invalid
        except ValueError:
            priority = 'Medium'
        return cls(
            id=row['id'],
            description=row['description'],
            completed=bool(row['completed']),
            created_at=row['created_at'],
            priority=priority
        )

class TaskSchema:
    """Database schema definitions."""
    
    CREATE_TASKS_TABLE = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium'
        )
    '''
    
    # Future tables can be added here
    CREATE_USERS_TABLE = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    '''
    
    CREATE_CATEGORIES_TABLE = '''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#007bff',
            created_at TEXT NOT NULL
        )
    '''
    
    @classmethod
    def get_all_schemas(cls) -> List[str]:
        """Get all CREATE TABLE statements."""
        return [
            cls.CREATE_TASKS_TABLE,
            cls.CREATE_USERS_TABLE,
            cls.CREATE_CATEGORIES_TABLE
        ]

# Utility functions for formatting
def format_datetime(dt: datetime) -> str:
    """Format datetime in readable format (e.g., '21 August 2025, 3:45pm')."""
    hour = dt.hour % 12 or 12  # Convert 0 or 12 to 12 for 12-hour clock
    am_pm = 'am' if dt.hour < 12 else 'pm'
    minute = dt.minute
    return f"{dt.day} {dt.strftime('%B %Y')}, {hour}:{minute:02d}{am_pm}"

def get_current_timestamp() -> str:
    """Get current timestamp in the application's format."""
    return format_datetime(datetime.now())

def get_current_timestamp_debug() -> tuple[str, datetime]:
    """Debug version that returns both formatted string and raw datetime."""
    now = datetime.now()
    formatted = format_datetime(now)
    return formatted, now

# Validation functions
def validate_priority(priority: str) -> bool:
    """Validate if priority is valid."""
    try:
        Priority(priority)
        return True
    except ValueError:
        return False

def validate_task_description(description: str) -> tuple[bool, str]:
    """Validate task description. Returns (is_valid, error_message)."""
    if not description or not description.strip():
        return False, "Task description cannot be empty"
    
    if len(description.strip()) > 500:
        return False, "Task description cannot exceed 500 characters"
    
    return True, ""