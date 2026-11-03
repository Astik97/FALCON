from twilio.rest import Client
from config import (ACCOUNT_SID,AUTH_TOKEN,FROM_PHONE,TO_PHONE)

# Validate configuration
if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_PHONE, TO_PHONE]):
    raise RuntimeError(
        "Missing one or more Twilio environment variables."
        "Check your .env file."
    )

def send_alert_message(
    message_text: str = "⚠️ Warning! Weapon detected. "
    "Immediate help is needed.") -> bool:
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

if __name__ == "__main__":
    send_alert_message("Testing Twilio SMS from Python")