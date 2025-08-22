#!/bin/bash

# Paths
VENV_PATH="/root/Task_Reminder_System/task_reminder_system/myvenv"
NOTIFY_SCRIPT="/root/Task_Reminder_System/task_reminder_system/notify/notify.py"
REQUIREMENTS="/root/Task_Reminder_System/task_reminder_system/requirements.txt"
LOG_FILE="/root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_crontab.log"

# Ensure log file directory exists and is writable
LOG_DIR=$(dirname "$LOG_FILE")
mkdir -p "$LOG_DIR"
chmod 775 "$LOG_DIR"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Virtual environment not found at $VENV_PATH. Creating it..." >> "$LOG_FILE" 2>&1
    # Create virtual environment
    /usr/bin/python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment at $VENV_PATH" >> "$LOG_FILE" 2>&1
        exit 1
    fi
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment at $VENV_PATH" >> "$LOG_FILE" 2>&1
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "$REQUIREMENTS" ]; then
    echo "Installing dependencies from $REQUIREMENTS..." >> "$LOG_FILE" 2>&1
    "$VENV_PATH/bin/pip" install --upgrade pip >> "$LOG_FILE" 2>&1
    "$VENV_PATH/bin/pip" install -r "$REQUIREMENTS" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies from $REQUIREMENTS" >> "$LOG_FILE" 2>&1
        exit 1
    fi
else
    echo "Warning: $REQUIREMENTS not found. Assuming dependencies are already installed." >> "$LOG_FILE" 2>&1
fi

# Run notify.py
echo "Running $NOTIFY_SCRIPT at $(date)" >> "$LOG_FILE" 2>&1
"$VENV_PATH/bin/python3" "$NOTIFY_SCRIPT" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to run $NOTIFY_SCRIPT" >> "$LOG_FILE" 2>&1
    exit 1
fi

# Deactivate virtual environment
deactivate
echo "Successfully ran $NOTIFY_SCRIPT and deactivated virtual environment" >> "$LOG_FILE" 2>&1

exit 0