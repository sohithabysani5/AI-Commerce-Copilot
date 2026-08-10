import unittest
from agents.local_agent import local_commerce_agent, matches_keywords, ORDER_START_KEYWORDS, PRODUCT_KEYWORDS

class TestMultilingual(unittest.TestCase):

    def test_english_order_start(self):
        state = {}
        response = local_commerce_agent("I want to order", state, language="en")
        self.assertIn("What product would you like to order?", response)

    def test_telugu_order_start(self):
        state = {}
        response = local_commerce_agent("ఆర్డర్ చేయాలి", state, language="te")
        self.assertIn("మీకు ఏ ఉత్పత్తి కావాలి?", response)

    def test_hindi_order_start(self):
        state = {}
        response = local_commerce_agent("ऑर्डर करना है", state, language="hi")
        self.assertIn("आपको कौन सा उत्पाद चाहिए?", response)

    def test_keyword_matching(self):
        self.assertTrue(matches_keywords("I want to order", ORDER_START_KEYWORDS, "en"))
        self.assertTrue(matches_keywords("ఆర్డర్ చేయాలి", ORDER_START_KEYWORDS, "te"))
        self.assertTrue(matches_keywords("ऑर्डर करना है", ORDER_START_KEYWORDS, "hi"))
        # Fallback to English
        self.assertTrue(matches_keywords("I want to order", ORDER_START_KEYWORDS, "te"))

if __name__ == '__main__':
    unittest.main()
