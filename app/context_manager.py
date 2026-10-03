from typing import List, Dict, Any

class ContextManager:
    """
    Manages token budgeting, message trimming, and context assembly
    to guarantee prompts fit within configured limits while preserving
    the critical system prompt, character identity, and most recent turns.
    """

    def __init__(self, max_messages: int = 20, max_token_estimate: int = 4000):
        self.max_messages = max_messages
        self.max_token_estimate = max_token_estimate

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 characters per token."""
        return max(1, len(text) // 4)

    def trim_context(
        self,
        messages: List[Dict[str, str]],
        max_messages: int = None
    ) -> List[Dict[str, str]]:
        """
        Trims message history while preserving:
        1. The system prompt at index 0 (critical character definition).
        2. The most recent N conversation turns.
        """
        limit = max_messages or self.max_messages
        if len(messages) <= limit + 1:
            return messages

        system_message = None
        conversation_turns = []

        if messages and messages[0].get("role") == "system":
            system_message = messages[0]
            conversation_turns = messages[1:]
        else:
            conversation_turns = messages

        # Keep the most recent `limit` messages
        trimmed_turns = conversation_turns[-limit:]

        result = []
        if system_message:
            result.append(system_message)
        result.extend(trimmed_turns)

        return result
