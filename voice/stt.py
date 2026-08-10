import io
import logging
import speech_recognition as sr

from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from config.settings import (
    STT_PROVIDER,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# SPEECH-TO-TEXT
# ============================================================

class SpeechToText:
    """
    Speech-to-Text engine.

    Supports:
        - google_web: Free Google Web Speech API
          (no API key needed, good for development)
        - google_cloud: Google Cloud Speech-to-Text
          (requires credentials, production quality)

    Provider is configurable via .env STT_PROVIDER.
    """

    def __init__(self, provider=None):

        self.provider = provider or STT_PROVIDER
        self.recognizer = sr.Recognizer()

        logger.info(
            "STT initialized with provider: %s",
            self.provider,
        )

    # --------------------------------------------------------
    # TRANSCRIBE AUDIO BYTES
    # --------------------------------------------------------

    def transcribe_audio(
        self,
        audio_bytes,
        language="en",
        sample_rate=16000,
        sample_width=2,
    ):
        """
        Convert audio bytes to text.

        Parameters:
            audio_bytes: Raw audio data (WAV or raw PCM)
            language: Language code (en, te, hi)
            sample_rate: Audio sample rate
            sample_width: Bytes per sample

        Returns:
            dict with keys:
                success: bool
                text: transcribed text (if success)
                message: error message (if not success)
                language: detected/used language code
        """

        try:

            # Get the STT language code
            lang_config = SUPPORTED_LANGUAGES.get(
                language,
                SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
            )

            stt_code = lang_config["stt_code"]

            # ------------------------------------------------
            # Convert bytes to AudioData
            # ------------------------------------------------

            audio_data = sr.AudioData(
                audio_bytes,
                sample_rate,
                sample_width,
            )

            # ------------------------------------------------
            # Transcribe using selected provider
            # ------------------------------------------------

            if self.provider == "google_cloud":

                text = self._transcribe_google_cloud(
                    audio_data, stt_code
                )

            else:

                text = self._transcribe_google_web(
                    audio_data, stt_code
                )

            if not text or text.strip() == "":

                return {
                    "success": False,
                    "text": "",
                    "message": "No speech detected.",
                    "language": language,
                }

            logger.info(
                "STT result [%s]: %s",
                language,
                text,
            )

            return {
                "success": True,
                "text": text.strip(),
                "message": "Transcription successful.",
                "language": language,
            }

        except sr.UnknownValueError:

            logger.warning(
                "STT could not understand audio."
            )

            return {
                "success": False,
                "text": "",
                "message": (
                    "Sorry, I could not understand "
                    "the audio. Please try again."
                ),
                "language": language,
            }

        except sr.RequestError as e:

            logger.error(
                "STT service error: %s", str(e)
            )

            return {
                "success": False,
                "text": "",
                "message": (
                    "Speech recognition service "
                    "is temporarily unavailable."
                ),
                "language": language,
            }

        except Exception as e:

            logger.error(
                "STT unexpected error: %s", str(e)
            )

            return {
                "success": False,
                "text": "",
                "message": (
                    "An error occurred during "
                    "speech recognition."
                ),
                "language": language,
            }

    # --------------------------------------------------------
    # TRANSCRIBE FROM WAV FILE BYTES
    # --------------------------------------------------------

    def transcribe_wav(
        self,
        wav_bytes,
        language="en",
    ):
        """
        Transcribe from WAV file bytes.

        This is the primary method for Streamlit
        audio recorder widgets which return WAV bytes.
        """

        try:

            lang_config = SUPPORTED_LANGUAGES.get(
                language,
                SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
            )

            stt_code = lang_config["stt_code"]

            # Convert WAV bytes to AudioFile
            wav_io = io.BytesIO(wav_bytes)

            with sr.AudioFile(wav_io) as source:

                audio_data = self.recognizer.record(
                    source
                )

            # Transcribe
            if self.provider == "google_cloud":

                text = self._transcribe_google_cloud(
                    audio_data, stt_code
                )

            else:

                text = self._transcribe_google_web(
                    audio_data, stt_code
                )

            if not text or text.strip() == "":

                return {
                    "success": False,
                    "text": "",
                    "message": "No speech detected.",
                    "language": language,
                }

            logger.info(
                "STT WAV result [%s]: %s",
                language,
                text,
            )

            return {
                "success": True,
                "text": text.strip(),
                "message": "Transcription successful.",
                "language": language,
            }

        except sr.UnknownValueError:

            return {
                "success": False,
                "text": "",
                "message": (
                    "Sorry, I could not understand "
                    "the audio. Please try again."
                ),
                "language": language,
            }

        except sr.RequestError as e:

            logger.error(
                "STT service error: %s", str(e)
            )

            return {
                "success": False,
                "text": "",
                "message": (
                    "Speech recognition service "
                    "is temporarily unavailable."
                ),
                "language": language,
            }

        except Exception as e:

            logger.error(
                "STT WAV error: %s", str(e)
            )

            return {
                "success": False,
                "text": "",
                "message": (
                    "An error occurred during "
                    "speech recognition."
                ),
                "language": language,
            }

    # --------------------------------------------------------
    # GOOGLE WEB SPEECH API (FREE)
    # --------------------------------------------------------

    def _transcribe_google_web(
        self, audio_data, language_code
    ):
        """
        Uses the free Google Web Speech API.

        No API key required.
        Supports multiple languages including
        en-IN, te-IN, hi-IN.
        """

        text = self.recognizer.recognize_google(
            audio_data,
            language=language_code,
        )

        return text

    # --------------------------------------------------------
    # GOOGLE CLOUD SPEECH-TO-TEXT
    # --------------------------------------------------------

    def _transcribe_google_cloud(
        self, audio_data, language_code
    ):
        """
        Uses Google Cloud Speech-to-Text API.

        Requires GOOGLE_CLOUD_CREDENTIALS in .env.
        Higher accuracy, production-grade.
        """

        from config.settings import (
            GOOGLE_CLOUD_CREDENTIALS,
        )

        text = self.recognizer.recognize_google_cloud(
            audio_data,
            credentials_json=GOOGLE_CLOUD_CREDENTIALS,
            language=language_code,
        )

        return text

    # --------------------------------------------------------
    # RECORD FROM MICROPHONE
    # --------------------------------------------------------

    def record_from_microphone(
        self,
        language="en",
        timeout=10,
        phrase_time_limit=15,
    ):
        """
        Record audio from the system microphone
        and transcribe it.

        Used for local testing, NOT for Streamlit
        (Streamlit uses its own audio recorder widget).
        """

        try:

            with sr.Microphone() as source:

                logger.info(
                    "Adjusting for ambient noise..."
                )

                self.recognizer.adjust_for_ambient_noise(
                    source, duration=1
                )

                logger.info(
                    "Listening... (timeout=%ds)",
                    timeout,
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )

            # Get raw audio bytes
            audio_bytes = audio.get_raw_data()

            return self.transcribe_audio(
                audio_bytes,
                language=language,
                sample_rate=audio.sample_rate,
                sample_width=audio.sample_width,
            )

        except sr.WaitTimeoutError:

            return {
                "success": False,
                "text": "",
                "message": (
                    "No speech detected within "
                    "the timeout period."
                ),
                "language": language,
            }

        except Exception as e:

            logger.error(
                "Microphone error: %s", str(e)
            )

            return {
                "success": False,
                "text": "",
                "message": (
                    "Could not access the microphone."
                ),
                "language": language,
            }


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    stt = SpeechToText()

    print("=" * 60)
    print("SPEECH-TO-TEXT TEST")
    print("=" * 60)
    print(f"\nProvider: {stt.provider}")
    print(f"\nSupported languages:")

    for code, config in SUPPORTED_LANGUAGES.items():
        print(
            f"  {code}: {config['name']} "
            f"({config['native_name']}) "
            f"→ {config['stt_code']}"
        )

    print("\nSTT module loaded successfully.")
