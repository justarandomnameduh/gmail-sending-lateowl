#!/usr/bin/env python3
"""
Daily Reminder System for Google Drive File Uploads (Improved Version)
Uses Flask-Mail for better email handling, based on WhosClimbing implementation.
"""

import os
import pandas as pd
import schedule
import time
from datetime import datetime
from flask import Flask
from flask_mail import Mail
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import sys
from email_utils import send_reminder_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

class ImprovedDailyReminderSystem:
    def __init__(self):
        # Google API scopes
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        # File paths
        self.participants_file = 'participants.xlsx'
        self.token_file = 'token.json'
        
        # Services
        self.drive_service = None
        self.app = None
        self.mail = None
        
        # Setup Flask app and services
        self.setup_flask_app()
        self.setup_google_services()
    
    def setup_flask_app(self):
        """Setup Flask app with email configuration following WhosClimbing pattern."""
        self.app = Flask(__name__)
        
        # Email configuration - following WhosClimbing pattern
        self.app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        self.app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
        self.app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        self.app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        self.app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'Survey Team <lateowl-survey@gmail.com>')
        
        # Load from credentials file if env vars not set
        if not self.app.config['MAIL_USERNAME'] or not self.app.config['MAIL_PASSWORD']:
            self.load_mail_config_from_file()
        
        # Initialize Flask-Mail
        self.mail = Mail(self.app)
        
        logger.info("Flask app configured successfully")
        logger.info(f"Email server: {self.app.config['MAIL_SERVER']}")
        logger.info(f"Email username: {self.app.config['MAIL_USERNAME']}")
    
    def load_mail_config_from_file(self):
        """Load email configuration from gmail_credentials.txt file."""
        try:
            with open('gmail_credentials.txt', 'r') as f:
                lines = f.read().strip().split('\n')
                self.app.config['MAIL_USERNAME'] = lines[0].strip()
                self.app.config['MAIL_PASSWORD'] = lines[1].strip()
                logger.info("Email credentials loaded from file")
        except FileNotFoundError:
            logger.error("gmail_credentials.txt not found!")
        except IndexError:
            logger.error("Invalid format in gmail_credentials.txt")
    
    def setup_google_services(self):
        """Setup Google Drive API service."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.error("Please run the setup_oauth.py script first to authenticate with Google APIs")
                return
        
        try:
            self.drive_service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive service initialized successfully")
        except HttpError as error:
            logger.error(f"An error occurred setting up Google Drive: {error}")
    
    def load_participants(self):
        """Load participant data from Excel file."""
        try:
            df = pd.read_excel(self.participants_file)
            
            # Validate required columns
            required_columns = ['email', 'name', 'active']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Excel file must have columns: {required_columns}")
                return []
            
            # Filter only active participants
            active_participants = df[df['active'] == 1]
            logger.info(f"Loaded {len(active_participants)} active participants from {len(df)} total")
            
            return active_participants[['email', 'name']].to_dict('records')
        except FileNotFoundError:
            logger.error(f"Error: {self.participants_file} not found!")
            logger.error("Please create the file using: python create_sample_excel.py")
            return []
        except Exception as e:
            logger.error(f"Error loading participants: {e}")
            return []
    
    def get_drive_folder_id(self, folder_name):
        """Get the ID of the Google Drive folder by name."""
        try:
            # Search for folders with the given name
            results = self.drive_service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            items = results.get('files', [])
            if items:
                logger.info(f"Found folder '{folder_name}' with ID: {items[0]['id']}")
                return items[0]['id']
            else:
                logger.error(f"Folder '{folder_name}' not found")
                logger.error("Please ensure the folder exists and you have access to it")
                return None
        except HttpError as error:
            logger.error(f"An error occurred searching for folder: {error}")
            return None
    
    def check_files_uploaded_today(self, folder_id, participant_email):
        """Check if participant uploaded any files today to the specified folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Search for files in the folder modified today
            results = self.drive_service.files().list(
                q=f"parents in '{folder_id}' and modifiedTime >= '{today}T00:00:00' and trashed=false",
                fields="files(id, name, owners, modifiedTime, createdTime)"
            ).execute()
            
            items = results.get('files', [])
            logger.debug(f"Found {len(items)} files modified today in the folder")
            
            # Check if any file was uploaded by this participant
            for file in items:
                owners = file.get('owners', [])
                for owner in owners:
                    if owner.get('emailAddress', '').lower() == participant_email.lower():
                        logger.debug(f"Found file by {participant_email}: {file.get('name')}")
                        return True
            
            return False
            
        except HttpError as error:
            logger.error(f"An error occurred while checking files: {error}")
            return False
    
    def run_daily_check(self, folder_name="Survey Uploads"):
        """Run the daily check for file uploads and send reminders."""
        logger.info("=" * 70)
        logger.info(f"Running daily reminder check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        # Check if all services are ready
        if not self.drive_service:
            logger.error("Google Drive service not initialized. Exiting.")
            return
        
        if not self.app.config['MAIL_USERNAME']:
            logger.error("Email configuration not complete. Exiting.")
            return
        
        # Load participants
        participants = self.load_participants()
        if not participants:
            logger.warning("No active participants found.")
            return
        
        logger.info(f"Checking {len(participants)} active participants")
        
        # Get drive folder ID
        folder_id = self.get_drive_folder_id(folder_name)
        if not folder_id:
            logger.error(f"Could not find folder '{folder_name}'. Exiting.")
            return
        
        logger.info(f"Monitoring uploads in folder: {folder_name}")
        
        # Check each participant
        reminders_sent = 0
        upload_count = 0
        
        with self.app.app_context():
            for participant in participants:
                email = participant['email']
                name = participant['name']
                
                # Check if they uploaded today
                uploaded_today = self.check_files_uploaded_today(folder_id, email)
                
                if not uploaded_today:
                    logger.info(f"📧 No upload found for {name} ({email}) - sending reminder")
                    if send_reminder_email(email, name, self.mail):
                        reminders_sent += 1
                else:
                    logger.info(f"✅ {name} ({email}) has uploaded today")
                    upload_count += 1
        
        logger.info("=" * 70)
        logger.info(f"Daily check completed!")
        logger.info(f"  • Participants with uploads: {upload_count}")
        logger.info(f"  • Reminder emails sent: {reminders_sent}")
        logger.info(f"  • Total participants checked: {len(participants)}")
        logger.info("=" * 70)
    
    def start_scheduler(self, check_time="01:00", folder_name="Survey Uploads"):
        """Start the daily scheduler."""
        logger.info(f"Daily check scheduled for: {check_time}")
        logger.info(f"Monitoring folder: {folder_name}")
        logger.info(f"Email sender: {self.app.config['MAIL_DEFAULT_SENDER']}")
        logger.info("=" * 50)
        logger.info("Press Ctrl+C to stop the scheduler")
        # Schedule the daily check
        schedule.every().day.at(check_time).do(self.run_daily_check, folder_name)
        # Keep the script running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\nDaily reminder scheduler stopped by user")

def main():
    """Main function to run the daily reminder system."""
    try:
        reminder_system = ImprovedDailyReminderSystem()
        
        # Configuration
        check_time = "01:00"
        folder_name = "Survey Uploads"
        
        # Start the scheduler
        reminder_system.start_scheduler(check_time, folder_name)
        
    except Exception as e:
        logger.error(f"Failed to start daily reminder system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
