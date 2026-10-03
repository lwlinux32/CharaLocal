# Local Character AI

A modern, open-source, locally hosted AI character-chat web platform inspired by the concept of Character.AI. Built with a **Python FastAPI backend**, **SQLite persistent database**, and a clean, responsive **HTML5/CSS/Vanilla JavaScript frontend**.

---

##  Quick Start
##### IMPORTANT: If you're gonna run it with npm, create a .env file, if no, you can set your conf from localhost
### 1. Install Dependencies
Ensure you have Python 3.10+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` to configure your preferred OpenAI-compatible endpoint or API key:

```env
AI_API_KEY="your-api-key-here"
AI_BASE_URL="https://api.openai.com/v1"
AI_MODEL="gpt-4o-mini"
```

*Note: You can also configure all provider settings, endpoints, and API keys directly inside the web UI using the Settings modal at any time.*

### 3. Run the Server
Launch the application with a single command:

```bash
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```
(or port `3000` if launched with `python run.py --port 3000`).

---

## 🌟 Key Features

1. **Character Management**
   - Create, edit, and delete characters with editable metadata.
   - Character name, avatar URL, short tagline, backstory, personality, scenario, greeting, system directives, example dialogue, and tags.
   - Built-in library search and tag filter pills.
   - 6 rich starter characters included out-of-the-box (Dr. Evelyn Reed, Vector, Captain Astrid Vance, Kaelen the Runesmith, Aria, and Milo Barnaby).

2. **Multi-Conversation System**
   - Create multiple independent conversations with the same character.
   - Switch between conversations seamlessly via the chat header dropdown.
   - Rename conversations and delete unwanted chat sessions.
   - Automatic character greeting on new conversation creation.

3. **Character Prompt Engine (`app/prompt_builder.py`)**
   - Dedicated Python prompt construction engine.
   - Fuses character personality, background, scenario, behavioral constraints, example dialogue, established long-term memories, and dialogue turns.
   - Enforces immersive roleplay directives (never breaking character, avoiding claiming to be an AI, natural asterisk formatting for physical actions/narration).

4. **Context Manager (`app/context_manager.py`)**
   - Configurable message history window (default 20 turns).
   - Preserves critical system prompt and character definition at index 0 while maintaining the most recent conversation context.

5. **Long-Term Character Memories**
   - Dedicated memory architecture (`memories` table).
   - Add persistent facts, shared lore, or user preferences with importance levels (1-5 stars).
   - Injected directly into the character's system prompt context.

6. **OpenAI-Compatible Provider Layer (`app/providers/`)**
   - Compatible with **any** OpenAI-compatible inference server:
     - **OpenAI**: `https://api.openai.com/v1` (`gpt-4o-mini`, `gpt-4o`)
     - **Google Gemini (OpenAI endpoint)**: `https://generativelanguage.googleapis.com/v1beta/openai/` (`gemini-2.5-flash`)
     - **Local Ollama**: `http://localhost:11434/v1` (`llama3`, `mistral`)
     - **Local LM Studio**: `http://localhost:1234/v1` (`local-model`)
     - **Groq**: `https://api.groq.com/openai/v1` (`llama-3.3-70b-versatile`)
     - **OpenRouter**: `https://openrouter.ai/api/v1` (`anthropic/claude-3.5-sonnet`)
   - Built-in simulation fallback provider for immediate offline testing without requiring an API key.

7. **Real-Time Streaming Responses (SSE)**
   - Server-Sent Events stream tokens in real-time.
   - Visual typing cursor and dynamic markdown/asterisk formatting.
   - Interactive "Stop Generation" button to cancel in-flight streams.
   - "Regenerate" and "Copy" actions on assistant messages.

8. **Export and Import**
   - Export characters to JSON files and import characters with one click.
   - Export and import full conversation histories.

9. **Security & Secrets**
   - API keys are stored on the local backend and SQLite database—never leaked in client-side HTML bundles.
   - `.env` and SQLite `.db` files are included in `.gitignore` to prevent accidental commits.

---

## 📁 Project Architecture

```text
.
├── app/
│   ├── __init__.py
│   ├── database.py         # SQLite database schema, connections, and CRUD
│   ├── models.py           # Pydantic schemas for requests & validation
│   ├── prompt_builder.py   # Dedicated Character Prompt Engine
│   ├── context_manager.py  # Context window trimming and memory injection
│   ├── providers/
│   │   ├── __init__.py     # Provider factory
│   │   ├── base.py         # AIProvider abstract base class
│   │   ├── openai_compatible.py  # OpenAI-compatible streaming client
│   │   └── mock_provider.py      # Offline simulation fallback provider
│   └── main.py             # FastAPI web application and REST/SSE endpoints
├── static/
│   ├── css/
│   │   └── style.css       # Dark-first modern design system
│   └── js/
│       └── app.js         # Vanilla JavaScript (No React, No TypeScript)
├── templates/
│   └── index.html         # HTML5 semantic interface
├── data/                  # SQLite storage directory (character_ai.db)
├── run.py                 # CLI launcher: python run.py [--port 8000]
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md
```

---

## 🔒 Security Best Practices

- **Never share or commit your API keys**: Keep your `.env` file private.
- **Local SQLite Storage**: All character lore, memories, and chat logs are stored locally on your machine in `data/character_ai.db`.
- **Offline Inference**: For complete privacy, connect the application to a local inference engine such as **Ollama** or **LM Studio**. No data leaves your computer.
