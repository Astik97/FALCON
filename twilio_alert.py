import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load Twilio credentials from .env file
load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_PHONE = os.getenv("TWILIO_PHONE_NUMBER")
TO_PHONE = os.getenv("ALERT_RECEIVER_NUMBER")

def send_alert_message(message_text="⚠️ Warning! Weapon is detected. Immediate help is needed."):
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=message_text,
            from_=FROM_PHONE,
            to=TO_PHONE
        )
        print(f"[ALERT] SMS sent successfully! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {e}")
        return False