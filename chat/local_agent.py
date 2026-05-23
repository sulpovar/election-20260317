"""Ollama-backed local model with structured self-assessment output."""
import json
import ollama
from config import LOCAL_MODEL, OLLAMA_BASE_URL

_SYSTEM = """You are a helpful AI assistant with honest self-awareness about your limitations.

For every user message respond ONLY with valid JSON in this exact structure:
{
  "answer": "your complete answer here",
  "confidence": 0.85,
  "needs_cloud": false,
  "limitation_reason": null
}

Rules for "needs_cloud":
- Set to true (and explain in "limitation_reason") when:
  * The question requires information newer than your training data
  * You are genuinely uncertain or the topic is outside your knowledge
  * The task requires complex multi-step reasoning, code review, or expert analysis
  * The question involves real-time data (prices, live events, current news)
- Set to false when you can answer fully and confidently

Rules for "confidence":
- Float 0.0 – 1.0 reflecting how certain you are in your answer
- Be honest: if you are guessing, reflect that with a lower value

When "needs_cloud" is true:
- "answer" may be empty or contain your partial attempt
- "limitation_reason" must be a non-null string explaining why
When "needs_cloud" is false:
- "answer" must be your complete response
- "limitation_reason" must be null

Respond with ONLY the JSON object, no surrounding text."""


def ask_local(messages: list[dict]) -> dict:
    """Send conversation to Ollama, return structured assessment dict."""
    client = ollama.Client(host=OLLAMA_BASE_URL)

    try:
        response = client.chat(
            model=LOCAL_MODEL,
            messages=[{"role": "system", "content": _SYSTEM}] + messages,
            format="json",
            options={"temperature": 0.2},
        )
        raw = response.message.content
    except Exception as e:
        return {
            "answer": "",
            "confidence": 0.0,
            "needs_cloud": True,
            "limitation_reason": f"Ollama error: {e}",
        }

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Model produced non-JSON despite format="json"; treat as escalation
        return {
            "answer": raw,
            "confidence": 0.3,
            "needs_cloud": True,
            "limitation_reason": "Local model returned malformed JSON",
        }

    return {
        "answer": result.get("answer", ""),
        "confidence": float(result.get("confidence", 0.5)),
        "needs_cloud": bool(result.get("needs_cloud", False)),
        "limitation_reason": result.get("limitation_reason"),
    }
