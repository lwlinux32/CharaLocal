from typing import Dict, Any
from .base import AIProvider
from .openai_compatible import OpenAICompatibleProvider
from .mock_provider import MockProvider

def get_provider(config: Dict[str, Any]) -> AIProvider:
    """
    Returns the appropriate AI provider instance.
    If no API key and base_url is default OpenAI, falls back to MockProvider
    unless user explicitly configured an endpoint or local Ollama/LM Studio.
    """
    api_key = config.get("api_key", "").strip()
    base_url = config.get("base_url", "").strip()

    # If base_url is a local server (e.g. localhost, 127.0.0.1) or an API key is provided, use OpenAI-compatible
    is_local = "localhost" in base_url or "127.0.0.1" in base_url or "0.0.0.0" in base_url
    if api_key or is_local:
        return OpenAICompatibleProvider()

    # Otherwise return MockProvider for instant graceful preview
    return MockProvider()

__all__ = ["AIProvider", "OpenAICompatibleProvider", "MockProvider", "get_provider"]
