#!/usr/bin/env python3
"""
OAuth Setup Script for Google APIs
Run this script once to authenticate with Google Drive and Gmail APIs.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for the application
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def setup_oauth():
    """Set up OAuth credentials for Google APIs."""
    creds = None
    token_file = 'token.json'
    credentials_json = 'credentials.json'
    
    # Check if token file exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_json):
                print(f"Error: {credentials_json} not found!")
                print("\nTo set up OAuth authentication:")
                print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print("2. Create a new project or select an existing one")
                print("3. Enable the Gmail API and Google Drive API")
                print("4. Create credentials (OAuth 2.0 Client ID) for a desktop application")
                print("5. Download the credentials JSON file and save it as 'credentials.json' in this folder")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    # Test the credentials
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        gmail_service = build('gmail', 'v1', credentials=creds)
        
        # Test Drive API
        results = drive_service.files().list(pageSize=1).execute()
        print("✓ Google Drive API access successful")
        
        # Test Gmail API
        profile = gmail_service.users().getProfile(userId='me').execute()
        print(f"✓ Gmail API access successful (Email: {profile['emailAddress']})")
        
        print("\n✓ OAuth setup completed successfully!")
        print("You can now run the daily_reminder.py script")
        return True
        
    except Exception as error:
        print(f"✗ Error testing APIs: {error}")
        return False

if __name__ == "__main__":
    print("Setting up OAuth authentication for Google APIs...")
    print("This will open a browser window for authentication.")
    
    if setup_oauth():
        print("\nSetup complete! You can now use the daily reminder system.")
    else:
        print("\nSetup failed. Please check the instructions above.") 