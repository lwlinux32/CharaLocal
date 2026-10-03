import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import (
    init_db,
    get_all_characters,
    get_character_by_id,
    create_character,
    update_character,
    delete_character,
    get_conversations_for_character,
    get_conversation_by_id,
    create_conversation,
    update_conversation,
    delete_conversation,
    get_messages_for_conversation,
    add_message,
    delete_message,
    get_memories_for_character,
    add_memory,
    delete_memory,
    get_all_settings,
    save_settings,
    set_setting
)
from .models import (
    CharacterCreate,
    CharacterUpdate,
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    MemoryCreate,
    SettingsUpdate,
    TestConnectionRequest
)
from .prompt_builder import PromptBuilder
from .context_manager import ContextManager
from .providers import get_provider, OpenAICompatibleProvider

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and tables
    init_db()
    yield

app = FastAPI(
    title="Local Character AI",
    description="Open-source, locally hosted AI character-chat web platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for open accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Character.AI Local backend running.</h1>")

# -------------------------------------------------------------
# Characters Endpoints
# -------------------------------------------------------------
@app.get("/api/characters")
async def list_characters(search: Optional[str] = None, tag: Optional[str] = None):
    return get_all_characters(search=search, tag=tag)

@app.post("/api/characters")
async def api_create_character(payload: CharacterCreate):
    char = create_character(payload.model_dump())
    return char

@app.get("/api/characters/{char_id}")
async def api_get_character(char_id: str):
    char = get_character_by_id(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char

@app.put("/api/characters/{char_id}")
async def api_update_character(char_id: str, payload: CharacterUpdate):
    char = get_character_by_id(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    merged = {**char, **update_data}
    updated = update_character(char_id, merged)
    return updated

@app.delete("/api/characters/{char_id}")
async def api_delete_character(char_id: str):
    success = delete_character(char_id)
    return {"success": success}

@app.get("/api/characters/{char_id}/export")
async def export_character(char_id: str):
    char = get_character_by_id(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    memories = get_memories_for_character(char_id)
    export_data = {
        "spec": "chara_v1",
        "spec_version": "1.0",
        "data": char,
        "memories": memories,
        "exported_at": datetime.utcnow().isoformat()
    }
    content = json.dumps(export_data, indent=2)
    filename = f"{char['name'].replace(' ', '_').lower()}_character.json"
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/characters/import")
async def import_character(data: Dict[str, Any]):
    char_data = data.get("data", data)
    required = ["name"]
    if not any(k in char_data for k in required):
        raise HTTPException(status_code=400, detail="Invalid character import file: 'name' is required.")
    
    clean_data = {
        "name": char_data.get("name", "Imported Character"),
        "avatar": char_data.get("avatar") or "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80",
        "short_description": char_data.get("short_description", ""),
        "description": char_data.get("description", ""),
        "personality": char_data.get("personality", ""),
        "scenario": char_data.get("scenario", ""),
        "greeting": char_data.get("greeting", "Hello! It is great to meet you."),
        "system_prompt": char_data.get("system_prompt", ""),
        "example_dialogue": char_data.get("example_dialogue", ""),
        "tags": char_data.get("tags", "Imported"),
        "creator": char_data.get("creator", "Imported"),
        "visibility": char_data.get("visibility", "public")
    }
    new_char = create_character(clean_data)
    
    # Import memories if present
    memories = data.get("memories", [])
    if isinstance(memories, list):
        for mem in memories:
            content = mem.get("content")
            if content:
                add_memory(new_char["id"], content, mem.get("importance", 1))
                
    return new_char

# -------------------------------------------------------------
# Conversations Endpoints
# -------------------------------------------------------------
@app.get("/api/characters/{char_id}/conversations")
async def list_conversations(char_id: str):
    return get_conversations_for_character(char_id)

@app.post("/api/characters/{char_id}/conversations")
async def api_create_conversation(char_id: str, payload: Optional[ConversationCreate] = None):
    title = payload.title if payload else None
    return create_conversation(char_id, title)

@app.get("/api/conversations/{conv_id}")
async def api_get_conversation(conv_id: str):
    conv = get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = get_messages_for_conversation(conv_id)
    char = get_character_by_id(conv["character_id"])
    return {
        "conversation": conv,
        "character": char,
        "messages": messages
    }

@app.put("/api/conversations/{conv_id}")
async def api_update_conversation(conv_id: str, payload: ConversationUpdate):
    updated = update_conversation(conv_id, payload.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return updated

@app.delete("/api/conversations/{conv_id}")
async def api_delete_conversation(conv_id: str):
    delete_conversation(conv_id)
    return {"success": True}

@app.get("/api/conversations/{conv_id}/export")
async def export_conversation(conv_id: str):
    conv = get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    char = get_character_by_id(conv["character_id"])
    messages = get_messages_for_conversation(conv_id)
    export_data = {
        "conversation": conv,
        "character": char,
        "messages": messages,
        "exported_at": datetime.utcnow().isoformat()
    }
    content = json.dumps(export_data, indent=2)
    filename = f"chat_{conv_id[:8]}.json"
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/conversations/import")
async def import_conversation(data: Dict[str, Any]):
    conv_data = data.get("conversation", {})
    char_id = conv_data.get("character_id")
    if not char_id or not get_character_by_id(char_id):
        raise HTTPException(status_code=400, detail="Cannot import conversation: Associated character not found.")
    
    title = conv_data.get("title", "Imported Chat")
    new_conv = create_conversation(char_id, title)
    
    # Import messages
    messages = data.get("messages", [])
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant", "system") and content:
            add_message(new_conv["id"], role, content)
            
    return get_conversation_by_id(new_conv["id"])

# -------------------------------------------------------------
# Messages & Streaming Chat Endpoints
# -------------------------------------------------------------
@app.post("/api/conversations/{conv_id}/messages")
async def api_send_message(conv_id: str, payload: MessageCreate):
    conv = get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    char = get_character_by_id(conv["character_id"])
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    # 1. Store user message
    user_msg = add_message(conv_id, payload.role or "user", payload.content)

    # 2. Reconstruct context
    settings = get_all_settings()
    memories = get_memories_for_character(char["id"])
    history = get_messages_for_conversation(conv_id)

    raw_messages = PromptBuilder.build_chat_messages(
        character=char,
        conversation_history=history,
        memories=memories
    )

    ctx_mgr = ContextManager(max_messages=int(settings.get("context_limit", 20)))
    final_messages = ctx_mgr.trim_context(raw_messages)

    # 3. Generate response using configured provider
    provider = get_provider(settings)
    try:
        reply_text = await provider.generate_response(final_messages, settings)
    except Exception as e:
        # Fall back to in-character simulation if remote provider is busy (e.g. 503/429)
        from .providers.mock_provider import MockProvider
        mock = MockProvider()
        sim_reply = await mock.generate_response(final_messages, settings)
        reply_text = f"{sim_reply}\n\n*(Note: Remote provider reported: {str(e)[:120]}. Served via local simulation)*"

    assistant_msg = add_message(conv_id, "assistant", reply_text)
    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg
    }

@app.post("/api/conversations/{conv_id}/chat/stream")
async def stream_chat_response(conv_id: str, payload: MessageCreate):
    """
    Server-Sent Events (SSE) streaming endpoint for progressively streaming
    character responses to the client.
    """
    conv = get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    char = get_character_by_id(conv["character_id"])
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    # 1. Add user message
    user_msg = add_message(conv_id, payload.role or "user", payload.content)

    # 2. Gather context
    settings = get_all_settings()
    memories = get_memories_for_character(char["id"])
    history = get_messages_for_conversation(conv_id)

    raw_messages = PromptBuilder.build_chat_messages(
        character=char,
        conversation_history=history,
        memories=memories
    )
    ctx_mgr = ContextManager(max_messages=int(settings.get("context_limit", 20)))
    final_messages = ctx_mgr.trim_context(raw_messages)

    provider = get_provider(settings)

    async def event_generator():
        # First send user_message info event
        yield f"event: user_message\ndata: {json.dumps(user_msg)}\n\n"

        full_response = []
        try:
            async for token in provider.generate_stream(final_messages, settings):
                full_response.append(token)
                chunk_data = json.dumps({"token": token})
                yield f"event: token\ndata: {chunk_data}\n\n"
        except Exception as e:
            from .providers.mock_provider import MockProvider
            mock = MockProvider()
            notice = f"\n*(Remote provider temporarily unavailable: {str(e)[:100]}. Continuing via local simulation)*\n\n"
            full_response.append(notice)
            yield f"event: token\ndata: {json.dumps({'token': notice})}\n\n"
            async for token in mock.generate_stream(final_messages, settings):
                full_response.append(token)
                yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

        # Finalize and persist assistant message in database
        final_text = "".join(full_response).strip()
        if not final_text:
            final_text = "*looks back thoughtfully in silence.*"
            yield f"event: token\ndata: {json.dumps({'token': final_text})}\n\n"

        assistant_msg = add_message(conv_id, "assistant", final_text)
        yield f"event: done\ndata: {json.dumps(assistant_msg)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/conversations/{conv_id}/regenerate")
async def regenerate_last_message(conv_id: str):
    """
    Removes the last assistant message and streams a newly generated response.
    """
    conv = get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    char = get_character_by_id(conv["character_id"])
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    messages = get_messages_for_conversation(conv_id)
    if messages and messages[-1]["role"] == "assistant":
        delete_message(messages[-1]["id"])
        messages.pop()

    settings = get_all_settings()
    memories = get_memories_for_character(char["id"])

    raw_messages = PromptBuilder.build_chat_messages(
        character=char,
        conversation_history=messages,
        memories=memories
    )
    ctx_mgr = ContextManager(max_messages=int(settings.get("context_limit", 20)))
    final_messages = ctx_mgr.trim_context(raw_messages)

    provider = get_provider(settings)

    async def event_generator():
        full_response = []
        try:
            async for token in provider.generate_stream(final_messages, settings):
                full_response.append(token)
                yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            from .providers.mock_provider import MockProvider
            mock = MockProvider()
            notice = f"\n*(Remote provider temporarily unavailable: {str(e)[:100]}. Continuing via local simulation)*\n\n"
            full_response.append(notice)
            yield f"event: token\ndata: {json.dumps({'token': notice})}\n\n"
            async for token in mock.generate_stream(final_messages, settings):
                full_response.append(token)
                yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

        final_text = "".join(full_response).strip()
        if not final_text:
            final_text = "*pauses and reconsiders.*"
            yield f"event: token\ndata: {json.dumps({'token': final_text})}\n\n"

        assistant_msg = add_message(conv_id, "assistant", final_text)
        yield f"event: done\ndata: {json.dumps(assistant_msg)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.delete("/api/conversations/{conv_id}/messages/{msg_id}")
async def api_delete_message(conv_id: str, msg_id: str):
    delete_message(msg_id)
    return {"success": True}

# -------------------------------------------------------------
# Long-Term Memories Endpoints
# -------------------------------------------------------------
@app.get("/api/characters/{char_id}/memories")
async def list_memories(char_id: str):
    return get_memories_for_character(char_id)

@app.post("/api/characters/{char_id}/memories")
async def api_add_memory(char_id: str, payload: MemoryCreate):
    char = get_character_by_id(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    mem = add_memory(
        char_id=char_id,
        content=payload.content,
        importance=payload.importance or 1,
        conversation_id=payload.conversation_id
    )
    return mem

@app.delete("/api/memories/{mem_id}")
async def api_delete_memory(mem_id: str):
    delete_memory(mem_id)
    return {"success": True}

# -------------------------------------------------------------
# Settings & Provider Configuration Endpoints
# -------------------------------------------------------------
@app.get("/api/settings")
async def api_get_settings():
    s = get_all_settings()
    api_key = s.get("api_key", "")
    masked_key = ""
    if api_key:
        if len(api_key) > 8:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            masked_key = "********"
    return {
        "base_url": s.get("base_url", "https://api.openai.com/v1"),
        "model": s.get("model", "gpt-4o-mini"),
        "temperature": float(s.get("temperature", 0.85)),
        "max_tokens": int(s.get("max_tokens", 1024)),
        "streaming": bool(s.get("streaming", True)),
        "context_limit": int(s.get("context_limit", 20)),
        "has_api_key": bool(api_key),
        "masked_api_key": masked_key
    }

@app.post("/api/settings")
async def api_save_settings(payload: SettingsUpdate):
    current = get_all_settings()
    updates = {}
    if payload.base_url is not None:
        updates["base_url"] = payload.base_url.strip()
    if payload.api_key is not None:
        # If user passed empty string, they might want to clear or keep
        if payload.api_key != "":
            updates["api_key"] = payload.api_key.strip()
    if payload.model is not None:
        updates["model"] = payload.model.strip()
    if payload.temperature is not None:
        updates["temperature"] = payload.temperature
    if payload.max_tokens is not None:
        updates["max_tokens"] = payload.max_tokens
    if payload.streaming is not None:
        updates["streaming"] = payload.streaming
    if payload.context_limit is not None:
        updates["context_limit"] = payload.context_limit

    save_settings(updates)
    return {"success": True, "settings": await api_get_settings()}

@app.get("/api/settings/local-models")
async def api_get_local_models(base_url: Optional[str] = None):
    settings = get_all_settings()
    target_url = base_url or settings.get("base_url", "http://localhost:11434/v1")
    provider = OpenAICompatibleProvider()
    models = await provider.list_models({
        "base_url": target_url,
        "api_key": settings.get("api_key", "")
    })
    return {"base_url": target_url, "models": models}

@app.post("/api/settings/test")
async def api_test_connection(payload: TestConnectionRequest):
    settings = get_all_settings()
    test_config = {
        "base_url": payload.base_url or settings.get("base_url", "https://api.openai.com/v1"),
        "api_key": payload.api_key if payload.api_key is not None else settings.get("api_key", ""),
        "model": payload.model or settings.get("model", "gpt-4o-mini")
    }
    provider = OpenAICompatibleProvider()
    result = await provider.test_connection(test_config)
    return result
