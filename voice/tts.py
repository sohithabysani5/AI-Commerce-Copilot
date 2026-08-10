import io
import logging

from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from config.settings import (
    TTS_PROVIDER,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# TEXT-TO-SPEECH
# ============================================================

class TextToSpeech:
    """
    Text-to-Speech engine.

    Supports:
        - gtts: Google Text-to-Speech (free, no API key)
          Supports en, te, hi and many more languages.
        - google_cloud: Google Cloud Text-to-Speech
          (requires credentials, higher quality)

    Provider is configurable via .env TTS_PROVIDER.
    """

    def __init__(self, provider=None):

        self.provider = provider or TTS_PROVIDER

        logger.info(
            "TTS initialized with provider: %s",
            self.provider,
        )

    # --------------------------------------------------------
    # SYNTHESIZE TEXT TO AUDIO BYTES
    # --------------------------------------------------------

    def synthesize(
        self,
        text,
        language="en",
    ):
        """
        Convert text to speech audio.

        Parameters:
            text: The text to speak
            language: Language code (en, te, hi)

        Returns:
            dict with keys:
                success: bool
                audio_bytes: MP3 audio bytes (if success)
                content_type: MIME type
                message: status/error message
                language: language code used
        """

        if not text or text.strip() == "":

            return {
                "success": False,
                "audio_bytes": None,
                "content_type": None,
                "message": "No text provided.",
                "language": language,
            }

        try:

            lang_config = SUPPORTED_LANGUAGES.get(
                language,
                SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
            )

            # Select provider
            if self.provider == "google_cloud":

                audio_bytes = (
                    self._synthesize_google_cloud(
                        text, lang_config
                    )
                )

            else:

                audio_bytes = (
                    self._synthesize_gtts(
                        text, lang_config
                    )
                )

            if not audio_bytes:

                return {
                    "success": False,
                    "audio_bytes": None,
                    "content_type": None,
                    "message": (
                        "Failed to generate audio."
                    ),
                    "language": language,
                }

            logger.info(
                "TTS generated %d bytes [%s]: %s...",
                len(audio_bytes),
                language,
                text[:50],
            )

            return {
                "success": True,
                "audio_bytes": audio_bytes,
                "content_type": "audio/mp3",
                "message": "Audio generated.",
                "language": language,
            }

        except Exception as e:

            logger.error(
                "TTS error: %s", str(e)
            )

            return {
                "success": False,
                "audio_bytes": None,
                "content_type": None,
                "message": (
                    "Text-to-speech service "
                    "encountered an error."
                ),
                "language": language,
            }

    # --------------------------------------------------------
    # gTTS (FREE, NO API KEY)
    # --------------------------------------------------------

    def _synthesize_gtts(self, text, lang_config):
        """
        Uses gTTS (Google Text-to-Speech).

        Free, no API key.
        Supports en, te, hi natively.
        Returns MP3 bytes.
        """

        from gtts import gTTS

        tts = gTTS(
            text=text,
            lang=lang_config["tts_code"],
            tld=lang_config.get("tts_tld", "com"),
        )

        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return audio_buffer.read()

    # --------------------------------------------------------
    # GOOGLE CLOUD TTS (PRODUCTION)
    # --------------------------------------------------------

    def _synthesize_google_cloud(
        self, text, lang_config
    ):
        """
        Uses Google Cloud Text-to-Speech API.

        Requires GOOGLE_CLOUD_CREDENTIALS in .env.
        Higher quality voices, SSML support.
        Returns MP3 bytes.
        """

        try:

            from google.cloud import texttospeech

            client = texttospeech.TextToSpeechClient()

            synthesis_input = (
                texttospeech.SynthesisInput(
                    text=text
                )
            )

            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_config["stt_code"],
                ssml_gender=(
                    texttospeech.SsmlVoiceGender.FEMALE
                ),
            )

            audio_config = (
                texttospeech.AudioConfig(
                    audio_encoding=(
                        texttospeech.AudioEncoding.MP3
                    ),
                    speaking_rate=1.0,
                )
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )

            return response.audio_content

        except ImportError:

            logger.warning(
                "google-cloud-texttospeech not "
                "installed. Falling back to gTTS."
            )

            return self._synthesize_gtts(
                text, lang_config
            )

        except Exception as e:

            logger.error(
                "Google Cloud TTS error: %s",
                str(e),
            )

            # Fallback to gTTS
            logger.info(
                "Falling back to gTTS..."
            )

            return self._synthesize_gtts(
                text, lang_config
            )

    # --------------------------------------------------------
    # SYNTHESIZE TO FILE
    # --------------------------------------------------------

    def synthesize_to_file(
        self,
        text,
        language="en",
        output_path="output.mp3",
    ):
        """
        Synthesize speech and save to a file.

        Useful for testing and phone call audio.
        """

        result = self.synthesize(text, language)

        if not result["success"]:
            return result

        with open(output_path, "wb") as f:
            f.write(result["audio_bytes"])

        result["file_path"] = output_path
        result["message"] = (
            f"Audio saved to {output_path}"
        )

        return result


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    tts = TextToSpeech()

    print("=" * 60)
    print("TEXT-TO-SPEECH TEST")
    print("=" * 60)
    print(f"\nProvider: {tts.provider}")
    print(f"\nSupported languages:")

    for code, config in SUPPORTED_LANGUAGES.items():
        print(
            f"  {code}: {config['name']} "
            f"({config['native_name']}) "
            f"→ TTS code: {config['tts_code']}"
        )

    # Test synthesis
    test_texts = {
        "en": "Welcome to AI Commerce Copilot.",
        "te": "AI Commerce Copilot కు స్వాగతం.",
        "hi": "AI Commerce Copilot में आपका स्वागत है.",
    }

    for lang, text in test_texts.items():

        print(f"\nTesting {lang}: {text}")

        result = tts.synthesize(text, lang)

        if result["success"]:
            print(
                f"  ✅ Generated {len(result['audio_bytes'])} "
                f"bytes of audio."
            )
        else:
            print(
                f"  ❌ Error: {result['message']}"
            )

    print("\nTTS module loaded successfully.")
