import unittest
from voice.stt import SpeechToText
from voice.tts import TextToSpeech
from voice.voice_agent import VoiceAgent

class TestVoice(unittest.TestCase):

    def setUp(self):
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.voice_agent = VoiceAgent()

    def test_strip_markdown(self):
        text = "**Hello** - This is a test •"
        stripped = self.voice_agent._strip_markdown(text)
        self.assertEqual(stripped, "Hello  This is a test")

    def test_tts_synthesis(self):
        result = self.tts.synthesize("Hello world", "en")
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["audio_bytes"])

    # We skip STT testing here as it requires real audio bytes,
    # but the integration is tested in browser.

if __name__ == '__main__':
    unittest.main()
