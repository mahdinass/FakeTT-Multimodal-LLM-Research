import base64
import unittest
from pathlib import Path

from fakett_research.client import InferenceError, OpenAICompatibleClient


ROOT = Path(__file__).resolve().parents[1]


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": '{"label":"real","confidence":0.8}'}}]}


class FakeSession:
    def __init__(self):
        self.request = None

    def post(self, url, *, json, headers, timeout):
        self.request = (url, json, headers, timeout)
        return FakeResponse()


class ClientTests(unittest.TestCase):
    def test_request_contains_authenticated_multimodal_payload(self):
        session = FakeSession()
        client = OpenAICompatibleClient(
            "https://example.invalid/v1", "demo-key", "demo-model", retries=0, session=session
        )
        image = ROOT / "data" / "synthetic" / "images" / "fake-symbol.png"
        answer = client.complete("analyze this synthetic icon", [str(image)], sample_id="toy", branch="visual")
        self.assertIn('"label":"real"', answer)
        url, payload, headers, timeout = session.request
        self.assertEqual(url, "https://example.invalid/v1/chat/completions")
        self.assertEqual(payload["model"], "demo-model")
        self.assertEqual(headers["Authorization"], "Bearer demo-key")
        data_url = payload["messages"][0]["content"][1]["image_url"]["url"]
        self.assertTrue(data_url.startswith("data:image/png;base64,"))
        self.assertEqual(base64.b64decode(data_url.split(",", 1)[1])[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(timeout, 90.0)

    def test_missing_credentials_fail_before_network_call(self):
        client = OpenAICompatibleClient("https://example.invalid/v1", "", "model", retries=0)
        with self.assertRaises(InferenceError):
            client.complete("test")


if __name__ == "__main__":
    unittest.main()
