import os
from dotenv import load_dotenv

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

# -----------------------------
# Project Root
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# Helper Function
# -----------------------------
def get_env_variable(name: str, default=None):
    value = os.getenv(name, default)

    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")

    return value

# -----------------------------
# Database Directory
# -----------------------------
DATABASE_DIR = os.path.join(BASE_DIR, "database")
USERS_DB = os.path.join(DATABASE_DIR, "add_users.db")
ALERTS_DB = os.path.join(DATABASE_DIR, "alerts.db")
DETECTIONS_DB = os.path.join(DATABASE_DIR, "detections.db")

# -----------------------------
# Media Directory
# -----------------------------
MEDIA_DIR = os.path.join(BASE_DIR, "media", "output")
# OUTPUT_DIR = os.path.join(MEDIA_DIR, "output")
# IMAGE_DIR = os.path.join(MEDIA_DIR, "images")
# VIDEO_DIR = os.path.join(MEDIA_DIR, "videos")

# -----------------------------
# AI
# -----------------------------
AI_DIR = os.path.join(BASE_DIR, "AI")
MODEL_DIR = os.path.join(AI_DIR, "models")
MODEL_PATH = get_env_variable(
    "MODEL_PATH",
    os.path.join(MODEL_DIR, "best.pt")
)

# -----------------------------
# Flask
# -----------------------------
SECRET_KEY = get_env_variable("SECRET_KEY")

# -----------------------------
# Twilio
# -----------------------------
ACCOUNT_SID = get_env_variable("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = get_env_variable("TWILIO_AUTH_TOKEN")
FROM_PHONE = get_env_variable("TWILIO_PHONE_NUMBER")
TO_PHONE = get_env_variable("ALERT_RECEIVER_NUMBER")

# -----------------------------
# Telegram (Future)
# -----------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")