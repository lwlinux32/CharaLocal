import asyncio
import random
from typing import List, Dict, Any, AsyncIterator
from .base import AIProvider

class MockProvider(AIProvider):
    """
    Offline fallback provider that generates persona-aware roleplay dialogue
    when no API key or local LLM server is configured.
    """

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> str:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break

        # Simulate thoughtful generation
        return self._craft_reply(messages, last_user)

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> AsyncIterator[str]:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break

        full_reply = self._craft_reply(messages, last_user)
        words = full_reply.split(" ")
        for i, word in enumerate(words):
            await asyncio.sleep(0.04 + random.uniform(0.01, 0.03))
            yield word + (" " if i < len(words) - 1 else "")

    def _craft_reply(self, messages: List[Dict[str, str]], last_user: str) -> str:
        # Check system prompt for character identity
        sys_msg = messages[0].get("content", "") if messages else ""
        char_name = "I"
        if "You are " in sys_msg:
            try:
                char_name = sys_msg.split("You are ")[1].split(".")[0].split(",")[0]
            except Exception:
                char_name = "I"

        actions = [
            "*pauses thoughtfully and considers your words*",
            "*leans in slightly with an intrigued expression*",
            "*gestures gently with a reflective nod*",
            "*smiles softly and reflects on what you just shared*"
        ]
        action = random.choice(actions)

        replies = [
            f"{action} That is quite compelling. When you mention \"{last_user.strip()[:60]}...\", it touches upon something fundamental to our situation here. Let us delve deeper into this thought together.",
            f"{action} You raise an interesting perspective. I find myself pondering the implications of what you've just said. Tell me more about what led you to this conclusion.",
            f"{action} Indeed. Hearing you say that makes the atmosphere around us shift in an unexpected way. I'm listening closely—how do you see our next step unfolding?",
            f"{action} Ah, I appreciate the candor in that. It aligns with what we've been navigating. What else is on your mind regarding this?"
        ]
        return random.choice(replies)

    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "Demo simulation provider is ready. (Configure OpenAI or Local LLM in Settings for real inference)"
        }
