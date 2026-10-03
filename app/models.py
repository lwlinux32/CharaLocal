from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1)
    avatar: Optional[str] = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80"
    short_description: Optional[str] = ""
    description: Optional[str] = ""
    personality: Optional[str] = ""
    scenario: Optional[str] = ""
    greeting: Optional[str] = "Hello! It's good to meet you."
    system_prompt: Optional[str] = ""
    example_dialogue: Optional[str] = ""
    tags: Optional[str] = "Custom"
    creator: Optional[str] = "You"
    visibility: Optional[str] = "public"

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None
    scenario: Optional[str] = None
    greeting: Optional[str] = None
    system_prompt: Optional[str] = None
    example_dialogue: Optional[str] = None
    tags: Optional[str] = None
    creator: Optional[str] = None
    visibility: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    content: str
    role: Optional[str] = "user"

class MemoryCreate(BaseModel):
    content: str
    importance: Optional[int] = 1
    conversation_id: Optional[str] = None

class SettingsUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    streaming: Optional[bool] = None
    context_limit: Optional[int] = None

class TestConnectionRequest(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
