# Task Reminder System

A personal task management application with a web-based interface and daily email notifications for incomplete tasks. Built with Flask for the web UI and AWS Simple Email Service (SES) for notifications, this system allows users to add, update, delete, and mark tasks as completed or incomplete. Tasks are stored in a JSON file for persistence, and the application supports both local and Docker-based deployment.

## Features
- **Web Interface**: Manage tasks (add, update, delete, mark complete/incomplete) via a browser-based UI styled with Tailwind CSS.
- **Task Management**: Store tasks with ID, description, completion status, and creation timestamp.
- **Daily Notifications**: Send email reminders for incomplete tasks using AWS SES.
- **Docker Support**: Run the application in a container for consistent deployment.
- **Modular Structure**: Organized directories for scripts, templates, data, and application entry point.

## Project Structure
```
project_folder/
├── scripts/
│   └── task_reminder.py    # Core application logic (Flask routes, task management, SES)
├── templates/
│   └── index.html          # Web UI template (HTML with Tailwind CSS)
├── data/
│   └── tasks.json          # Task storage (created automatically)
├── run_application/
│   └── run_app.py          # Entry point to run the Flask app or notifications
├── .env                    # Environment variables (AWS credentials, Flask config)
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker configuration for containerization
├── .dockerignore           # Files to exclude from Docker build
├── README.md               # Project documentation
```

## Prerequisites
- **Python**: Python 3.11 or higher.
- **AWS Account**: Configured with SES for email notifications.
- **Docker** (optional): For containerized deployment.
- **Git** (optional): For version control.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd project_folder
```

### 2. Install Dependencies
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create and edit the `.env` file:
```bash
cp .env.example .env
```
Update `.env` with your AWS SES credentials and email addresses:
```
FLASK_SECRET_KEY=your-secret-key  # Generate a strong, random key
AWS_REGION=us-east-1              # Your AWS SES region
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
SENDER_EMAIL=your-verified-email@example.com  # SES-verified sender email
RECIPIENT_EMAIL=recipient@example.com        # Recipient email
```

**AWS SES Setup**:
- Verify `SENDER_EMAIL` and `RECIPIENT_EMAIL` in the AWS SES console.
- Ensure SES is out of sandbox mode or recipient emails are verified.
- Obtain AWS credentials with SES permissions and add to `.env`.

### 4. Run Locally
Start the Flask application:
```bash
python run_application/run_app.py
```
- Access the web UI at `http://127.0.0.1:5000`.
- Use the UI to manage tasks (add, update, delete, mark complete/incomplete).

Run daily notifications (sends email with incomplete tasks):
```bash
python run_application/run_app.py notify
```

### 5. Schedule Daily Notifications
Schedule the `notify` command to run daily:
- **Windows**: Use Task Scheduler to run `python run_application/run_app.py notify` (e.g., at 8 AM).
- **Mac/Linux**: Edit crontab (`crontab -e`) and add:
  ```bash
  0 8 * * * /path/to/python /path/to/project_folder/run_application/run_app.py notify
  ```

### 6. Run with Docker
Build the Docker image:
```bash
docker build -t task-reminder .
```

Run the container:
```bash
docker run -p 5000:5000 --env-file .env task-reminder
```
- Access the UI at `http://localhost:5000`.

For persistent task data, mount the `data` directory:
```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data --env-file .env task-reminder
```

Run notifications in Docker:
```bash
docker run --env-file .env task-reminder python run_application/run_app.py notify
```

## Usage
- **Web UI**:
  - **Add Task**: Enter a description and click "Add Task".
  - **Update Task**: Enter a new description next to a task and click "Update".
  - **Delete Task**: Click "Delete" next to a task.
  - **Mark Complete/Incomplete**: Click "Mark Complete" or "Mark Incomplete".
  - Success/error messages appear as flash notifications.
- **Notifications**: Run `python run_application/run_app.py notify` to send an email listing incomplete tasks.

## Development
- **Add Features**: Extend `scripts/task_reminder.py` for features like due dates or task categories.
- **Database**: Replace `data/tasks.json` with SQLite or PostgreSQL for scalability.
- **UI Enhancements**: Modify `templates/index.html` or add JavaScript for interactivity.

## Security Notes
- Use a strong `FLASK_SECRET_KEY` in `.env` for production.
- Keep AWS credentials secure in `.env` and exclude it from version control.
- Consider HTTPS for production deployment.

## Deployment
To deploy to a cloud platform (e.g., AWS ECS, Heroku, Render):
1. Optimize the `Dockerfile` for your platform.
2. Use a volume or database for persistent `tasks.json` storage.
3. Configure environment variables securely in the deployment environment.

## Troubleshooting
- **AWS SES Errors**: Verify sender/recipient emails, check SES sandbox status, and ensure AWS credentials are correct.
- **Docker Issues**: Ensure port 5000 is free and `.env` is properly mounted.
- **Task Persistence**: Use a volume mount (`-v $(pwd)/data:/app/data`) to persist `tasks.json` in Docker.

## License
This project is for personal use and not licensed for distribution.

For questions or contributions, contact the project maintainer.
