import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native_name": "English",
        "stt_code": "en-IN",
        "tts_code": "en",
        "tts_tld": "co.in",
    },
    "te": {
        "name": "Telugu",
        "native_name": "తెలుగు",
        "stt_code": "te-IN",
        "tts_code": "te",
        "tts_tld": "co.in",
    },
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "stt_code": "hi-IN",
        "tts_code": "hi",
        "tts_tld": "co.in",
    },
}

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")


# ============================================================
# SPEECH-TO-TEXT CONFIGURATION
# ============================================================

STT_PROVIDER = os.getenv("STT_PROVIDER", "google_web")

# Google Cloud Speech (if using google_cloud provider)
GOOGLE_CLOUD_CREDENTIALS = os.getenv(
    "GOOGLE_CLOUD_CREDENTIALS", ""
)


# ============================================================
# TEXT-TO-SPEECH CONFIGURATION
# ============================================================

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "gtts")


# ============================================================
# TELEPHONY CONFIGURATION
# ============================================================

TELEPHONY_PROVIDER = os.getenv(
    "TELEPHONY_PROVIDER", "twilio"
)

TWILIO_ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID", ""
)

TWILIO_AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN", ""
)

TWILIO_PHONE_NUMBER = os.getenv(
    "TWILIO_PHONE_NUMBER", ""
)

# Webhook base URL (ngrok URL during dev, production URL later)
WEBHOOK_BASE_URL = os.getenv(
    "WEBHOOK_BASE_URL", "http://localhost:8000"
)


# ============================================================
# PHONE NUMBERS CONFIGURATION
# ============================================================

def get_configured_phone_numbers():
    """
    Load configured AI phone numbers from .env.

    Supports:
        PHONE_NUMBER_1=+91XXXXXXXXXX
        PHONE_NUMBER_2=+91XXXXXXXXXX
        etc.
    """

    numbers = []

    for i in range(1, 11):

        number = os.getenv(f"PHONE_NUMBER_{i}", "")

        if number:
            numbers.append(number)

    # Also check the main Twilio number
    if TWILIO_PHONE_NUMBER and TWILIO_PHONE_NUMBER not in numbers:
        numbers.insert(0, TWILIO_PHONE_NUMBER)

    return numbers


# ============================================================
# WEBHOOK SERVER
# ============================================================

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8000"))
