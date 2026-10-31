import os
from dotenv import load_dotenv

# Load Twilio credentials from .env file
load_dotenv()

def get_env_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")

    return value

ACCOUNT_SID = get_env_variable("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = get_env_variable("TWILIO_AUTH_TOKEN")
FROM_PHONE = get_env_variable("TWILIO_PHONE_NUMBER")
TO_PHONE = get_env_variable("ALERT_RECEIVER_NUMBER")