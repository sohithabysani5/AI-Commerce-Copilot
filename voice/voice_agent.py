import logging
import base64
from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from voice.stt import SpeechToText
from voice.tts import TextToSpeech
from agents.local_agent import local_commerce_agent


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# VOICE AGENT
# ============================================================

class VoiceAgent:
    """
    Orchestrates Voice-to-Voice conversation.

    Pipeline:
        Audio Input -> STT -> Commerce Agent -> TTS -> Audio Output
    """

    def __init__(self):

        logger.info("Initializing VoiceAgent...")

        self.stt = SpeechToText()
        self.tts = TextToSpeech()

    # --------------------------------------------------------
    # PROCESS WEB AUDIO (WAV BYTES)
    # --------------------------------------------------------

    def process_web_audio(
        self,
        wav_bytes,
        language,
        order_state,
    ):
        """
        Process audio from Streamlit microphone recorder.

        Parameters:
            wav_bytes: Audio bytes from Streamlit
            language: Language code (en, te, hi)
            order_state: The session state dictionary for orders

        Returns:
            dict with keys:
                success: bool
                transcription: STT text
                response_text: AI response text
                audio_base64: TTS audio encoded as base64
                message: Error message if any
        """

        # 1. Speech-to-Text
        logger.info("Starting STT...")

        # The audio_recorder_streamlit widget may return
        # WebM/OGG encoded audio (depending on browser).
        # We try multiple strategies to get valid WAV:
        #   A) pydub + FFmpeg conversion
        #   B) Direct WAV passthrough (if already WAV)
        #   C) Pure-python wave header check + re-wrap

        import io
        import wave
        converted_wav_bytes = None

        # --- Strategy A: pydub + FFmpeg (best quality) ---
        try:
            from pydub import AudioSegment

            audio_io = io.BytesIO(wav_bytes)
            audio_segment = AudioSegment.from_file(audio_io)

            # Normalize to 16kHz mono 16-bit for STT
            audio_segment = audio_segment.set_frame_rate(16000)
            audio_segment = audio_segment.set_channels(1)
            audio_segment = audio_segment.set_sample_width(2)

            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            converted_wav_bytes = wav_io.getvalue()

            logger.info(
                "Strategy A (pydub): converted %d -> %d bytes",
                len(wav_bytes), len(converted_wav_bytes),
            )

        except Exception as e:
            logger.warning(
                "Strategy A (pydub) failed: %s", str(e)
            )

        # --- Strategy B: Direct WAV passthrough ---
        if converted_wav_bytes is None:
            try:
                test_io = io.BytesIO(wav_bytes)
                with wave.open(test_io, "rb") as wf:
                    # If this succeeds, it's already valid WAV
                    logger.info(
                        "Strategy B: valid WAV detected "
                        "(channels=%d, rate=%d, frames=%d)",
                        wf.getnchannels(),
                        wf.getframerate(),
                        wf.getnframes(),
                    )
                converted_wav_bytes = wav_bytes
            except Exception as e:
                logger.warning(
                    "Strategy B (WAV check) failed: %s", str(e)
                )

        # --- Strategy C: Raw bytes passthrough (last resort) ---
        if converted_wav_bytes is None:
            logger.warning(
                "All conversion strategies failed. "
                "Passing raw bytes to STT (may fail)."
            )
            converted_wav_bytes = wav_bytes

        stt_result = self.stt.transcribe_wav(
            converted_wav_bytes, language=language
        )

        if not stt_result["success"]:
            return {
                "success": False,
                "transcription": "",
                "response_text": "",
                "audio_base64": None,
                "message": stt_result["message"],
            }

        transcription = stt_result["text"]

        logger.info(
            "Transcription [%s]: %s",
            language,
            transcription,
        )

        # 2. Commerce Agent
        logger.info("Calling commerce agent...")
        response_text = local_commerce_agent(
            transcription,
            order_state,
            language=language,
        )

        logger.info(
            "AI Response: %s",
            response_text,
        )

        # 3. Text-to-Speech
        logger.info("Starting TTS...")

        # We strip markdown from response before TTS
        # to prevent it from reading asterisks aloud.
        clean_text = self._strip_markdown(response_text)

        tts_result = self.tts.synthesize(
            clean_text, language=language
        )

        if not tts_result["success"]:
            return {
                "success": True, # Process succeeded, just no audio
                "transcription": transcription,
                "response_text": response_text,
                "audio_base64": None,
                "message": (
                    "Response generated, but audio "
                    f"synthesis failed: {tts_result['message']}"
                ),
            }

        # Convert MP3 bytes to base64 for Streamlit HTML audio
        audio_b64 = base64.b64encode(
            tts_result["audio_bytes"]
        ).decode("utf-8")

        return {
            "success": True,
            "transcription": transcription,
            "response_text": response_text,
            "audio_base64": audio_b64,
            "message": "Success",
        }

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def detect_language(self, text):
        """
        Automatically detect human language (English, Telugu, Hindi) from spoken speech.
        """
        import re
        if not text:
            return "en"

        # Telugu Unicode range \u0C00-\u0C7F or keywords
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"
        te_keywords = ["నాకు", "ఆర్డర్", "కావాలి", "ఎక్కడ", "రద్దు", "వద్దు", "అవును", "తెలుగు", "ఉత్పత్తి"]
        if any(k in text for k in te_keywords):
            return "te"

        # Hindi Unicode range \u0900-\u097F or keywords
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        hi_keywords = ["मुझे", "ऑर्डर", "चाहिए", "कहाँ", "रद्द", "नहीं", "हाँ", "हिंदी", "सामान"]
        if any(k in text for k in hi_keywords):
            return "hi"

        return "en"

    def _strip_markdown(self, text):
        """
        Convert raw AI agent output into 100% natural human-to-human speech.
        Removes emojis, markdown, technical guidelines, and formats lists conversationally.
        """
        import re

        if not text:
            return ""

        # 1. Remove all emojis
        text = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27FF\u2300-\u23FF\u2B50\u2B06\u2934\u25AA-\u25FE]', '', text)

        # 2. Remove markdown asterisks, hashes, underscores, backticks
        text = re.sub(r'[\*\_#\`\~]', '', text)

        # 3. Clean up technical bullet points & numbers
        text = text.replace("•", "").replace("- ", " ")

        # 4. Convert currency symbols to human spoken words
        text = re.sub(r'₹\s*([\d,]+(?:\.\d+)?)', r'\1 rupees', text)

        # 5. Clean up technical user guidelines & prompt instructions
        technical_replacements = [
            ("Example: ORD001", ""),
            ("Example: ORD002", ""),
            ("Example: RET20260809132757", ""),
            ("Example: C001", ""),
            ("Example: 1 or 2", ""),
            ("Please enter the number of the product you want to order.", "Which item would you like to order?"),
            ("Please enter the quantity as a number.", "How many units would you like?"),
            ("Please answer Yes or No.", "Shall I proceed for you?"),
            ("Please confirm the order by answering Yes or No.", "Would you like me to confirm this order?"),
            ("Please provide your Order ID.", "Could you please tell me your order ID?"),
            ("Please provide your Customer ID", "Could you please share your customer ID"),
            ("Please provide your Return ID.", "Could you please tell me your return ID?")
        ]

        for old_txt, new_txt in technical_replacements:
            text = text.replace(old_txt, new_txt)

        # 6. Normalize multiple spaces and newlines into natural pause sentences
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = " ".join(lines)
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("VOICE AGENT INITIALIZATION TEST")
    print("=" * 60)

    try:
        agent = VoiceAgent()
        print("\nVoiceAgent initialized successfully.")
    except Exception as e:
        print(f"\nFailed to initialize VoiceAgent: {e}")
