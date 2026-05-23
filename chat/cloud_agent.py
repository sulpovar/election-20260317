"""Anthropic Claude cloud agent with prompt caching."""
import anthropic
from config import CLOUD_MODEL

_client: anthropic.Anthropic | None = None

_SYSTEM = "You are a highly capable AI assistant. Provide accurate, comprehensive, and well-reasoned responses."


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def ask_cloud(messages: list[dict], escalation_context: dict | None = None) -> str:
    """Send conversation to Claude, optionally annotated with the local model's failed attempt."""
    client = _get_client()

    # System blocks — base prompt is cached across turns
    system: list[dict] = [
        {
            "type": "text",
            "text": _SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    if escalation_context:
        reason = escalation_context.get("limitation_reason") or "exceeded local model confidence"
        local_attempt = escalation_context.get("answer", "").strip()
        note = f"A local model attempted this question but required cloud assistance (reason: {reason})."
        if local_attempt:
            note += f"\n\nLocal model's partial attempt:\n{local_attempt}"
        system.append({"type": "text", "text": note})

    response = client.messages.create(
        model=CLOUD_MODEL,
        max_tokens=2048,
        system=system,
        messages=messages,
    )
    return response.content[0].text
