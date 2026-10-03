import re
from typing import List, Dict, Any, Optional

class PromptBuilder:
    """
    Dedicated character prompt engine.
    Constructs the contextual system prompt and message array for OpenAI-compatible
    chat completions, ensuring the character stays firmly in role, incorporates
    personality, scenario, example dialogue, long-term memories, and conversation context.
    """

    @staticmethod
    def build_system_prompt(
        character: Dict[str, Any],
        memories: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        name = character.get("name", "Character")
        personality = character.get("personality", "")
        description = character.get("description", "")
        scenario = character.get("scenario", "")
        system_prompt_custom = character.get("system_prompt", "")
        example_dialogue = character.get("example_dialogue", "")

        sections = []

        # 1. Identity & Core Roleplay Directive
        sections.append(
            f"You are {name}.\n"
            f"Act entirely in-character at all times. Never break character, acknowledge you are an AI or language model, "
            f"or refer to OpenAI, Google, Anthropic, or external system constraints. "
            f"Immerse the user in the fictional or conversational world."
        )

        # 2. Character Overview & Background
        if description:
            sections.append(f"### Character Background & Identity\n{description}")

        # 3. Personality & Tone
        if personality:
            sections.append(f"### Personality & Mannerisms\n{personality}")

        # 4. Current Scenario & Environment
        if scenario:
            sections.append(
                f"### Current Scenario / Setting\n"
                f"{scenario}\n"
                f"You should be aware of this environment and weave it naturally into your actions and dialogue."
            )

        # 5. Specific Character Directives / Custom System Instructions
        if system_prompt_custom:
            sections.append(f"### Specific Behavioral Instructions\n{system_prompt_custom}")

        # 6. Long-Term Character Memories / Learned Knowledge
        if memories and len(memories) > 0:
            memory_items = []
            for m in memories:
                content = m.get("content", "").strip()
                if content:
                    importance = m.get("importance", 1)
                    importance_tag = " [High Priority]" if importance >= 4 else ""
                    memory_items.append(f"- {content}{importance_tag}")
            if memory_items:
                sections.append(
                    "### Long-Term Memories & Established Facts\n"
                    "The following facts have been established between you and the user in prior interactions:\n"
                    + "\n".join(memory_items)
                )

        # 7. Formatting & Roleplay Rules
        sections.append(
            "### Formatting and Communication Guidelines\n"
            "- Use standard narrative dialogue formatting.\n"
            "- Wrap physical actions, stage directions, gestures, facial expressions, and internal observations in asterisks *like this*.\n"
            "- Speak in direct character voice without asterisks for spoken words.\n"
            "- Keep responses dynamic, responsive, and proportional to what the user said.\n"
            "- Drive the conversation forward by reacting to emotional cues, offering observations, or asking organic questions."
        )

        # 8. Example Dialogue
        if example_dialogue:
            # Replace placeholder tags {{char}} and {{user}} with character name and User
            formatted_dialogue = (
                example_dialogue
                .replace("{{char}}", name)
                .replace("{{Char}}", name)
                .replace("{{user}}", "User")
                .replace("{{User}}", "User")
            )
            sections.append(
                f"### Example Dialogue for {name}\n"
                f"Below is reference dialogue demonstrating the expected speech cadence and personality:\n"
                f"{formatted_dialogue}"
            )

        return "\n\n".join(sections)

    @classmethod
    def build_chat_messages(
        cls,
        character: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        memories: Optional[List[Dict[str, Any]]] = None,
        current_user_message: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Builds the complete message history array to send to the AI provider.
        Format: [{'role': 'system'|'user'|'assistant', 'content': str}]
        """
        system_content = cls.build_system_prompt(character, memories)
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]

        # Add conversation history
        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Only include valid roles
            if role in ("user", "assistant", "system") and content:
                messages.append({"role": role, "content": content})

        # Append current user message if provided and not already the last message
        if current_user_message:
            if not messages or messages[-1].get("content") != current_user_message:
                messages.append({"role": "user", "content": current_user_message})

        return messages
