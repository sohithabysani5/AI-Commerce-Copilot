import unittest
from voice.telephony import TelephonyManager
from voice.call_manager import call_manager

class TestTelephony(unittest.TestCase):

    def setUp(self):
        self.telephony = TelephonyManager()

    def test_create_gather_twiml(self):
        twiml = self.telephony.create_gather_twiml(
            action_url="http://test.com/process",
            say_text="Hello",
            language="en-US"
        )
        self.assertIn("<Gather", twiml)
        self.assertIn('action="http://test.com/process"', twiml)
        self.assertIn("<Say", twiml)
        self.assertIn("Hello</Say>", twiml)

    def test_call_manager(self):
        call_sid = "CA123456789"
        from_num = "+1234567890"
        
        # Test creation
        session = call_manager.get_or_create_session(call_sid, from_num)
        self.assertEqual(session["call_sid"], call_sid)
        self.assertEqual(session["phone_number"], from_num)
        self.assertEqual(session["language"], "en")
        
        # Test update
        call_manager.update_session(call_sid, "language", "te")
        session = call_manager.get_session(call_sid)
        self.assertEqual(session["language"], "te")
        
        # Test cleanup
        call_manager.end_session(call_sid)
        self.assertIsNone(call_manager.get_session(call_sid))

if __name__ == '__main__':
    unittest.main()
