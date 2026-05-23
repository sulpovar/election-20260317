#!/usr/bin/env python3
"""Dual-model chat: Ollama handles simple queries, Claude handles complex ones."""
import sys
from pathlib import Path

# Load .env from repo root if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from config import LOCAL_MODEL, CLOUD_MODEL, CONFIDENCE_THRESHOLD
from orchestrator import chat


def _banner(result: dict) -> str:
    if result["escalated"]:
        return (
            f"[cloud · {CLOUD_MODEL}] "
            f"(local confidence {result['confidence']:.0%} → escalated: {result['escalation_reason']})"
        )
    return f"[local · {LOCAL_MODEL}] (confidence {result['confidence']:.0%})"


def main() -> None:
    print(f"Dual-model chat")
    print(f"  Local : {LOCAL_MODEL}  (Ollama at OLLAMA_BASE_URL)")
    print(f"  Cloud : {CLOUD_MODEL}  (Anthropic API)")
    print(f"  Escalation threshold: confidence < {CONFIDENCE_THRESHOLD:.0%}")
    print("Type 'exit' or Ctrl-C to quit.\n")

    history: list[dict] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Bye!")
            sys.exit(0)

        try:
            result = chat(history, user_input)
        except Exception as exc:
            print(f"[error] {exc}\n")
            continue

        print(f"\n{_banner(result)}")
        print(result["answer"])
        print()

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": result["answer"]})


if __name__ == "__main__":
    main()
