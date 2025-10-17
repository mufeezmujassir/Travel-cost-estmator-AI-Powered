import os
import sys

from fastapi.testclient import TestClient


# Ensure we can import backend.main
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from main import app  # type: ignore  # FastAPI app


client = TestClient(app)


def test_chat_simple_message():
    payload = {"message": "What is vibe personalization?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, dict)
    assert "reply" in data
    assert isinstance(data["reply"], str)


def test_chat_with_context_fields():
    payload = {
        "message": "Why were flights skipped for my trip?",
        "page": "travel",
        "formSummary": {
            "origin": "Galle",
            "destination": "Matara",
            "startDate": "2025-10-20",
            "returnDate": "2025-10-22",
            "selectedVibe": "cultural"
        },
        "includeUserContext": False
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "reply" in data
    assert isinstance(data["reply"], str)


