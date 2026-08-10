import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from config.settings import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    WEBHOOK_BASE_URL,
)


logger = logging.getLogger(__name__)


class TelephonyManager:
    """
    Manages Twilio API interactions.
    """

    def __init__(self):

        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.phone_number = TWILIO_PHONE_NUMBER
        self.webhook_base_url = WEBHOOK_BASE_URL

        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(
                self.account_sid,
                self.auth_token
            )

    # --------------------------------------------------------
    # CALL ACTIONS
    # --------------------------------------------------------

    def make_call(self, to_number, from_number=None):
        """
        Initiate an outbound call.
        """

        if not self.client:
            logger.error("Twilio client not initialized.")
            raise Exception("Twilio client not initialized.")

        try:

            call = self.client.calls.create(
                url=f"{self.webhook_base_url}/voice/incoming",
                to=to_number,
                from_=from_number or self.phone_number,
                status_callback=f"{self.webhook_base_url}/voice/status",
                status_callback_event=["completed"]
            )

            logger.info(
                "Started call to %s, SID: %s",
                to_number,
                call.sid,
            )

            return call.sid

        except Exception as e:

            logger.error("Error making call: %s", str(e))
            raise e

    # --------------------------------------------------------
    # TWIML BUILDERS
    # --------------------------------------------------------

    def create_gather_twiml(
        self,
        action_url,
        say_text=None,
        audio_url=None,
        language="en-US",
        timeout=6,
        hints=None,
    ):
        """
        Creates TwiML for <Gather> to record user speech and DTMF.
        """
        response = VoiceResponse()

        # Map language codes for speech recognition & TTS
        stt_lang = language
        if language in ["en", "en-IN", "en-US"]:
            stt_lang = "en-IN"
            say_lang = "en-IN"
        elif language in ["te", "te-IN"]:
            stt_lang = "te-IN"
            say_lang = "hi-IN" # Twilio Polly.Aditi handles Hindi/Telugu text via hi-IN or en-IN
        elif language in ["hi", "hi-IN"]:
            stt_lang = "hi-IN"
            say_lang = "hi-IN"
        else:
            stt_lang = "en-US"
            say_lang = "en-US"

        gather = response.gather(
            input="speech dtmf",
            action=action_url,
            method="POST",
            timeout=timeout,
            language=stt_lang,
            hints=hints,
        )

        if audio_url:
            gather.play(audio_url)
        elif say_text:
            gather.say(say_text, language=say_lang, voice="Polly.Aditi")

        # If user is silent, redirect to action_url to prompt again instead of hanging up
        response.redirect(action_url)

        return str(response)

    def create_say_twiml(self, text, language="en-US"):
        """
        Creates simple TwiML to say text and hang up.
        """
        response = VoiceResponse()
        say_lang = "hi-IN" if language.startswith("hi") or language.startswith("te") else "en-IN"
        response.say(text, language=say_lang, voice="Polly.Aditi")
        response.hangup()

        return str(response)

    def create_play_twiml(self, audio_url):
        """
        Creates simple TwiML to play audio and hang up.
        """

        response = VoiceResponse()
        response.play(audio_url)
        response.hangup()

        return str(response)
