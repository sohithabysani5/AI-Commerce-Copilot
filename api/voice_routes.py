from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

import logging
from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from voice.telephony import TelephonyManager
from voice.call_manager import call_manager
from voice.voice_agent import VoiceAgent
from config.settings import WEBHOOK_BASE_URL

logger = logging.getLogger(__name__)

router = APIRouter()

telephony = TelephonyManager()
voice_agent = VoiceAgent()


@router.post("/voice/incoming", response_class=HTMLResponse)
async def incoming_call(
    request: Request,
    CallSid: str = Form(None),
    From: str = Form(None),
    To: str = Form(None)
):
    """
    Webhook for incoming calls from Twilio.
    """

    logger.info(
        "Incoming call from %s to %s (SID: %s)",
        From, To, CallSid
    )

    if not CallSid:
        return "<Response><Reject /></Response>"

    # Create session
    session = call_manager.get_or_create_session(
        CallSid, From
    )

    # Clean up old sessions
    call_manager.cleanup_old_sessions()

    greeting = (
        "Welcome to AI Commerce Copilot. "
        "For English, press 1 or say English. "
        "తెలుగు కోసం 2 నొక్కండి లేదా తెలుగు అని చెప్పండి. "
        "हिंदी के लिए 3 दबाएं या हिंदी बोलें."
    )

    action_url = f"{WEBHOOK_BASE_URL}/voice/language_selection"

    twiml = telephony.create_gather_twiml(
        action_url=action_url,
        say_text=greeting,
        language="en-US", # Use en-US to recognize digits/english
        timeout=5,
    )

    return twiml


@router.post("/voice/language_selection", response_class=HTMLResponse)
async def language_selection(
    request: Request,
    CallSid: str = Form(None),
    SpeechResult: str = Form(None),
    Digits: str = Form(None)
):
    """
    Process language selection via Speech or DTMF.
    """

    if not CallSid:
        return "<Response><Reject /></Response>"

    session = call_manager.get_session(CallSid)

    if not session:
        return telephony.create_say_twiml(
            "Sorry, your session expired. Please call again."
        )

    language = "en" # Default
    welcome_text = (
        "You have selected English. How can I help you today?"
    )
    
    # Process DTMF
    if Digits:
        if Digits == "1":
            language = "en"
        elif Digits == "2":
            language = "te"
            welcome_text = "మీరు తెలుగు ఎంచుకున్నారు. నేను మీకు ఎలా సహాయం చేయగలను?"
        elif Digits == "3":
            language = "hi"
            welcome_text = "आपने हिंदी चुना है। मैं आपकी कैसे मदद कर सकता हूँ?"
            
    # Process Speech (fallback to DTMF if both provided)
    elif SpeechResult:
        speech_lower = SpeechResult.lower()
        if "telugu" in speech_lower or "తెలుగు" in speech_lower:
            language = "te"
            welcome_text = "మీరు తెలుగు ఎంచుకున్నారు. నేను మీకు ఎలా సహాయం చేయగలను?"
        elif "hindi" in speech_lower or "हिंदी" in speech_lower:
            language = "hi"
            welcome_text = "आपने हिंदी चुना है। मैं आपकी कैसे मदद कर सकता हूँ?"

    # Update session
    call_manager.update_session(CallSid, "language", language)

    # Next step is to gather their first actual request
    action_url = f"{WEBHOOK_BASE_URL}/voice/process"

    # We use en-US for Twilio's Gather language because our STT expects english-like letters
    # Wait, actually Twilio's STT language can be set. 
    # Let's get the STT code from our config.
    from config.settings import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
    
    lang_config = SUPPORTED_LANGUAGES.get(
        language, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]
    )
    stt_code = lang_config["stt_code"]

    twiml = telephony.create_gather_twiml(
        action_url=action_url,
        say_text=welcome_text,
        language=stt_code,
        timeout=5,
    )

    return twiml


@router.post("/voice/process", response_class=HTMLResponse)
async def process_speech(
    request: Request,
    CallSid: str = Form(None),
    SpeechResult: str = Form(None)
):
    """
    Webhook called after Twilio <Gather> captures speech.
    """

    if not CallSid:
        return "<Response><Reject /></Response>"

    session = call_manager.get_session(CallSid)

    if not session:
        # Session expired or not found
        logger.warning(
            "Session not found for CallSid: %s",
            CallSid
        )
        return telephony.create_say_twiml(
            "Sorry, your session expired. Please call again."
        )

    # If the user didn't say anything
    if not SpeechResult:
        logger.info("No speech detected.")

        action_url = f"{WEBHOOK_BASE_URL}/voice/process"

        # Get language code for Gather
        from config.settings import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
        lang_config = SUPPORTED_LANGUAGES.get(
            session["language"], SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]
        )
        stt_code = lang_config["stt_code"]
        
        fallback_texts = {
            "en": "I didn't hear anything. Are you still there?",
            "te": "నాకు ఏమీ వినిపించలేదు. మీరు లైన్‌లో ఉన్నారా?",
            "hi": "मुझे कुछ सुनाई नहीं दिया। क्या आप सुन रहे हैं?"
        }
        fallback = fallback_texts.get(session["language"], fallback_texts["en"])

        twiml = telephony.create_gather_twiml(
            action_url=action_url,
            say_text=fallback,
            language=stt_code,
            timeout=5,
        )

        return twiml

    logger.info("User said: %s", SpeechResult)

    session["conversation_history"].append({"role": "user", "content": SpeechResult})

    # Process with local commerce agent
    # Twilio gives us text directly, so we don't need STT here!
    
    # We use the commerce agent directly, similar to what the voice agent does
    from agents.local_agent import local_commerce_agent

    response_text = local_commerce_agent(
        user_message=SpeechResult,
        state=session["order_state"],
        language=session["language"],
    )

    session["conversation_history"].append({"role": "agent", "content": response_text})

    # Strip markdown for TTS
    clean_text = voice_agent._strip_markdown(response_text)

    # Ask for more input
    action_url = f"{WEBHOOK_BASE_URL}/voice/process"

    from config.settings import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
    lang_config = SUPPORTED_LANGUAGES.get(
        session["language"], SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]
    )
    stt_code = lang_config["stt_code"]

    twiml = telephony.create_gather_twiml(
        action_url=action_url,
        say_text=clean_text,
        language=stt_code,
        timeout=5,
    )

    return twiml


@router.post("/voice/status")
async def call_status(
    request: Request,
    CallSid: str = Form(None),
    CallStatus: str = Form(None)
):
    """
    Webhook called by Twilio when the call status changes (e.g., completed).
    """
    import json
    from datetime import datetime

    if CallStatus == "completed" and CallSid:
        session = call_manager.get_session(CallSid)
        if session:
            # Save the conversation history to the JSON file
            log_entry = {
                "call_sid": CallSid,
                "timestamp": datetime.now().isoformat(),
                "customer_id": session.get("customer_id"),
                "language": session.get("language"),
                "history": session.get("conversation_history", [])
            }
            
            logs_file = Path(__file__).parent.parent / "data" / "call_logs.json"
            try:
                if logs_file.exists():
                    with open(logs_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                else:
                    logs = []
                    
                logs.append(log_entry)
                
                with open(logs_file, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=4, ensure_ascii=False)
                    
                logger.info("Call logs saved successfully for %s", CallSid)
            except Exception as e:
                logger.error("Failed to save call logs: %s", str(e))
                
            # Clean up the session since the call is over
            call_manager.end_session(CallSid)
            
    return HTMLResponse("<Response></Response>")
