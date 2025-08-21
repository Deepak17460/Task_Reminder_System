import os
import logging
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from database.db_manager import load_tasks
from notify.notify import RECIPIENT_EMAILS

# Load environment variables
load_dotenv()

# Configure logging
LOGS_DIR = '../logs'
LOG_FILE = os.path.join(LOGS_DIR, 'task_reminder.log')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
logger = logging.getLogger(__name__)

# AWS SES configuration
AWS_REGION = os.getenv("AWS_REGION")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAIL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize SES client
try:
    ses_client = boto3.client(
        'ses',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    logger.info("Initialized AWS SES client for region %s", AWS_REGION)
except Exception as e:
    logger.error("Failed to initialize AWS SES client: %s", str(e))
    raise

# Send email notification via AWS SES
def send_notification_email():
    tasks = load_tasks()
    incomplete = [task for task in tasks if not getattr(task, 'completed', False)]
    if not incomplete:
        logger.info("No incomplete tasks to notify")
        return "No incomplete tasks Ascertain the task details for each incomplete task"
    task_details = "\n".join([f"Task Name: {getattr(task, 'description', 'No description')}\nPriority: {getattr(task, 'priority', 'N/A')}" for task in incomplete])

    # Filter out empty or invalid emails
    valid_recipients = [email.strip() for email in RECIPIENT_EMAILS if email.strip() and '@' in email]
    if not valid_recipients:
        logger.error("No valid recipient emails provided")
        return "Error: No valid recipient emails provided"

    results = []
    for email in valid_recipients:
        # Extract username from email for personalization
        username = email.split('@')[0].split('.')[0] if '.' in email.split('@')[0] else email.split('@')[0]
        username = username.capitalize()

        subject = "Daily Task Reminder"
        body_text = f"""Hi {username},

We hope this message finds you well. 
This is a friendly reminder of your incomplete tasks as of today. 

Please find the details below.

Your Incomplete Tasks:
{task_details}

Please take a moment to review and update your task status as needed
Best regards,
The Task Reminder Team
"""

    body_html = f"""
    <html>
    <head></head>
    <body>
        <p>Hi {username},</p>
        <p>We hope this message finds you well. 
        This is a friendly reminder of your incomplete tasks as of today. </p>
        <p>Please find the details below.</p>
        <h2>Your Incomplete Tasks:</h2>
        {''.join([f"<p>Task Name-{getattr(task, 'description', 'No description')}<br>Priority-{getattr(task, 'priority', 'N/A')}</p>" for task in incomplete])}
        <p>Please take a moment to review and update your task status as needed</p>
        <p>Best regards,<br>The Task Reminder Team</p>
    </body>
    </html>
    """

    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        logger.info("Email sent successfully, Message ID: %s", response['MessageId'])
        return f"Email sent! Message ID: {response['MessageId']}"
    except ClientError as e:
        logger.error("Failed to send email: %s", e.response['Error']['Message'])
        return f"Error sending email: {e.response['Error']['Message']}"

# CLI for notifications
def notify():
    result = send_notification_email()
    print(result)

if __name__ == "__main__":
    notify()