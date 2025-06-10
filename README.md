# Daily Reminder System for Google Drive File Uploads

This system automatically sends daily reminder emails to participants who haven't uploaded files to a specified Google Drive folder by the end of the day.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Drive API
4. Create credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the JSON file and save it as `credentials.json` in this folder

### 3. Configure Gmail App Password

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a 16-character password
3. Update `gmail_credentials.txt` with your actual credentials:
   ```
   lateowl-survey@gmail.com
   your-16-character-app-password
   ```

### 4. Create Participants File

Run the sample creation script:
```bash
python create_sample_excel.py
```

Then replace `participants.xlsx` with your actual participant data. The Excel file should have these columns:
- `email` (string): Participant's email address
- `name` (string): Participant's full name  
- `active` (number): 1 for active, 0 for inactive

### 5. Run OAuth Setup

```bash
python setup_oauth.py
```

This will open a browser window for Google API authentication.

## Usage

### Start the Daily Reminder System

```bash
python daily_reminder.py
```

The system will:
- Run daily checks at 6 PM (configurable)
- Monitor the "Survey Uploads" folder (configurable)
- Send diary reminders to participants who haven't uploaded

### Configuration Options

Edit the `main()` function in `daily_reminder.py` to customize:

```python
check_time = "18:00"  # Time for daily check (24-hour format)
folder_name = "Survey Uploads"  # Google Drive folder name to monitor
```

### Manual Test Run

To test the system immediately:

```python
reminder_system = ImprovedDailyReminderSystem()
reminder_system.run_daily_check("Your Folder Name")
```

## Customization

### Email Template

The current email format includes:
- **Subject**: "Diary Reminder - DD/MM" (e.g., "Diary Reminder - 20/05")
- **Body**: Personalized message asking for reading progress updates

To customize, edit the email content in the `send_reminder_email()` method:

```python
current_date = datetime.now().strftime('%d/%m')
subject = f"Diary Reminder - {current_date}"
body = f"""Dear {participant_name},

Thanks for your response! Can you update the progress of your reading yesterday? We're really interested in your personal finding.

LateOwls"""
```

### Drive Folder Detection

The system finds folders by name. Ensure:
- The folder name matches exactly (case-sensitive)
- The Google account has access to the folder
- The folder is not in Trash

### Scheduling

Uses the `schedule` library. You can add multiple schedules:

```python
schedule.every().day.at("09:00").do(morning_check)
schedule.every().day.at("18:00").do(evening_check)
```