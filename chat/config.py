"""Configuration loaded from environment variables."""
import os

LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.2")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "claude-opus-4-7")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Escalate to cloud when local confidence is below this threshold
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
