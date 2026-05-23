"""Routes each user turn to the local or cloud model based on confidence assessment."""
from local_agent import ask_local
from cloud_agent import ask_cloud
from config import CONFIDENCE_THRESHOLD


def chat(history: list[dict], user_message: str) -> dict:
    """
    Process one conversational turn.

    Args:
        history: list of {"role": "user"|"assistant", "content": str} for prior turns
        user_message: the current user input

    Returns:
        dict with keys:
            answer          str   — model response
            model           str   — "local" or "cloud"
            escalated       bool  — whether cloud was invoked
            confidence      float — local model confidence (always present)
            escalation_reason str | None
    """
    messages = history + [{"role": "user", "content": user_message}]

    local = ask_local(messages)

    escalate = local["needs_cloud"] or local["confidence"] < CONFIDENCE_THRESHOLD

    if escalate:
        answer = ask_cloud(messages, escalation_context=local)
        return {
            "answer": answer,
            "model": "cloud",
            "escalated": True,
            "confidence": local["confidence"],
            "escalation_reason": local["limitation_reason"] or "low local confidence",
        }

    return {
        "answer": local["answer"],
        "model": "local",
        "escalated": False,
        "confidence": local["confidence"],
        "escalation_reason": None,
    }
