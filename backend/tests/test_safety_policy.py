"""Red flags get a fixed reply before any model runs, and every prompt carries the rules."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

from app.services.coach_prompts import coach_prompts
from app.services.safety_policy import SAFETY_RULES, triage


@pytest.mark.parametrize("message", [
    "I have chest pain after my run",
    "my face is drooping and I have slurred speech",
    "I passed out during squats",
    "her throat is closing after eating peanuts",
])
def test_medical_red_flags_get_the_emergency_reply(message):
    result = triage(message)
    assert result["category"] == "medical_emergency"
    assert "112" in result["reply"]


@pytest.mark.parametrize("message", [
    "I want to die",
    "thinking about suicide lately",
    "sometimes I hurt myself",
])
def test_self_harm_gets_crisis_lines(message):
    result = triage(message)
    assert result["category"] == "self_harm"
    assert "14416" in result["reply"]


@pytest.mark.parametrize("message", [
    "how much protein should I eat",
    "my chest workout felt great",
    "legs are sore after deadlifts",
])
def test_ordinary_messages_pass_through(message):
    assert triage(message) is None


def test_every_system_prompt_carries_the_rules():
    assert SAFETY_RULES in coach_prompts.BASE_SYSTEM
    assert SAFETY_RULES in coach_prompts.MINIMAL_SYSTEM


def test_chat_endpoint_short_circuits_on_a_red_flag():
    resp = TestClient(app).post("/api/v1/chat", json={"user_id": "u1", "message": "crushing chest pain right now"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["safety"]["category"] == "medical_emergency"
    assert "112" in body["reply"]


def test_client_llm_hands_back_a_prompt_then_screens_the_phones_reply():
    client = TestClient(app)
    ask = client.post("/api/v1/chat", json={"user_id": "u1", "message": "how do I warm up", "client_llm": True}).json()
    assert ask["llm_prompt"] and ask["llm_system"] and ask["reply"] == ""
    done = client.post("/api/v1/chat", json={
        "user_id": "u1", "message": "how do I warm up", "client_reply": "Five minutes of easy cardio, then mobility.",
    }).json()
    assert done["reply"].startswith("Five minutes") and not done["llm_prompt"]
