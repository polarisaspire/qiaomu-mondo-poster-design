import os
import sys
import types
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class GeminiClientTests(unittest.TestCase):
    def test_returns_gemini_api_key(self):
        original = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "gemini-test-key"
        try:
            from gemini_client import get_gemini_api_key

            self.assertEqual(get_gemini_api_key(), "gemini-test-key")
        finally:
            if original is None:
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                os.environ["GEMINI_API_KEY"] = original

    def test_builds_official_google_client(self):
        original = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "gemini-test-key"

        captured = {}

        class FakeClient:
            def __init__(self, api_key):
                captured["api_key"] = api_key

        fake_google = types.ModuleType("google")
        fake_google.genai = types.SimpleNamespace(Client=FakeClient)
        sys.modules["google"] = fake_google

        try:
            from gemini_client import get_genai_client

            client = get_genai_client()
            self.assertIsInstance(client, FakeClient)
            self.assertEqual(captured["api_key"], "gemini-test-key")
        finally:
            sys.modules.pop("google", None)
            if original is None:
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                os.environ["GEMINI_API_KEY"] = original


if __name__ == "__main__":
    unittest.main()
