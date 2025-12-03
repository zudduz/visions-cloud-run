import unittest
import json
from main import parse_ai_response


class TestParseAIResponse(unittest.TestCase):

    def test_parse_valid_response(self):
        response_string = '''Through whimsical chaos, a truth shall unwind,\nA journey of self, a curious kind.\nIn laughter and lightness, you'll find the key,\nTo unlock the person you're destined to be.Your vision for the future has been generated.{"vision_text": "Through whimsical chaos, a truth shall unwind,\\nA journey of self, a curious kind.\\nIn laughter and lightness, you\'ll find the key,\\nTo unlock the person you\'re destined to be.", "image_url": "https://storage.googleapis.com/sandbox-456821-oracle-visions/visions/ca27a9e3-97f5-49e5-bc84-9137cbc0d90c.png"}'''
        expected_output = {
            "text": "Through whimsical chaos, a truth shall unwind,\n" \
                      "A journey of self, a curious kind.\n" \
                      "In laughter and lightness, you'll find the key,\n" \
                      "To unlock the person you're destined to be.",
            "image": "https://storage.googleapis.com/sandbox-456821-oracle-visions/visions/ca27a9e3-97f5-49e5-bc84-9137cbc0d90c.png"
        }
        self.assertEqual(parse_ai_response(response_string), expected_output)

    def test_parse_invalid_json(self):
        response_string = '''Some text with invalid json {"vision_text": "text", "image_url": 'https://example.com/image.png'}'''
        expected_output = {"text": response_string}
        self.assertEqual(parse_ai_response(response_string), expected_output)

    def test_parse_missing_json(self):
        response_string = "This is a string without any JSON object."
        expected_output = {"text": response_string}
        self.assertEqual(parse_ai_response(response_string), expected_output)

    def test_parse_empty_string(self):
        response_string = ""
        expected_output = {"text": ""}
        self.assertEqual(parse_ai_response(response_string), expected_output)


if __name__ == '__main__':
    unittest.main()
