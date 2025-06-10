"""
Email utilities module for sending emails using Flask-Mail
Based on the WhosClimbing project implementation.
"""

from flask import current_app
from flask_mail import Message
import logging

logger = logging.getLogger(__name__)

def send_email(recipient, subject, body, mail_instance):
    """
    Send an actual email using Flask-Mail
    
    Args:
        recipient: Email address of the recipient
        subject: Email subject
        body: Email body text
        mail_instance: Flask-Mail instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail_instance.send(msg)
        logger.info(f"Email sent to {recipient}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        # Log to terminal if fails to send email
        logger.info("=" * 50)
        logger.info("[EMAIL SEND FAILED]")
        logger.info(f"TO: {recipient}")
        logger.info(f"SUBJECT: {subject}")
        logger.info(f"BODY: {body}")
        logger.info("=" * 50)
        return False

def send_reminder_email(recipient, participant_name, mail_instance):
    """
    Send a daily reminder email to a participant
    
    Args:
        recipient: Email address of the recipient
        participant_name: Name of the participant
        mail_instance: Flask-Mail instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    from datetime import datetime
    
    # Format date as DD/MM
    current_date = datetime.now().strftime('%d/%m')
    subject = f"Diary Reminder - {current_date}"
    
    body = f"""Dear {participant_name},

Thanks for your response! Can you update the progress of your reading yesterday? We're really interested in your personal finding.

LateOwls"""
    
    return send_email(recipient, subject, body, mail_instance) 