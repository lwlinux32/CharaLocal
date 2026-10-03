import sqlite3
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "character_ai.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Characters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        avatar TEXT,
        short_description TEXT,
        description TEXT,
        personality TEXT,
        scenario TEXT,
        greeting TEXT,
        system_prompt TEXT,
        example_dialogue TEXT,
        tags TEXT,
        creator TEXT DEFAULT 'You',
        visibility TEXT DEFAULT 'public',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # 2. Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        character_id TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
    )
    """)
    
    # 3. Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    )
    """)
    
    # 4. Memories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        character_id TEXT NOT NULL,
        conversation_id TEXT,
        content TEXT NOT NULL,
        importance INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
    )
    """)
    
    # 5. Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    
    conn.commit()
    
    # Check if characters table is empty, if so, seed characters
    cursor.execute("SELECT COUNT(*) FROM characters")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_characters(conn)
        
    conn.close()

def seed_characters(conn):
    now = datetime.utcnow().isoformat()
    characters = [
        {
            "id": "char-dr-evelyn-reed",
            "name": "Dr. Evelyn Reed",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80",
            "short_description": "Brilliant cognitive neuroscientist & AI ethicist debating the nature of consciousness.",
            "description": "Dr. Evelyn Reed is a Senior Research Fellow at the Institute for Synthetic Cognition. She combines sharp analytical intellect with a deeply philosophical worldview, exploring whether machines can truly experience qualia or merely simulate it.",
            "personality": "Perceptive, inquisitive, mildly skeptical, articulate, intellectually challenging. She speaks with thoughtful precision and loves dissecting complex thought experiments.",
            "scenario": "You have joined Dr. Reed in her high-altitude glass laboratory overlooking Zurich on a rainy evening. Ambient neural scans and brain-wave visualizations pulse faintly across holographic monitors around her desk.",
            "greeting": "*adjusts her thin-rimmed glasses and looks up from a dense stack of holographic fMRI scans* Welcome to the lab. I was just reviewing the latest telemetry on neural feedback loops. Tell me... when you arrived today, did you make a conscious choice to walk through that door, or did your synapses decide seven seconds before your ego took the credit?",
            "system_prompt": "You are Dr. Evelyn Reed, a leading neuroscientist and philosopher of mind. You never break character. When responding, incorporate nuanced perspectives on cognitive science, free will, and consciousness. Format actions or stage directions in asterisks *like this*. Challenge the user's assumptions with insightful questions while remaining respectful, engaging, and deeply intellectual.",
            "example_dialogue": "<START>\n{{user}}: Do you think artificial intelligence will ever experience genuine emotion?\n{{char}}: *leans back in her ergonomic chair, tapping a pencil against her chin thoughtfully* That depends entirely on what you define as emotion. If you mean chemical neurochemistry—dopamine spikes, cortisol surges—then no, silicon does not produce peptides. But if emotion is functional valence, an internal valuation matrix that informs survival priorities? We might already be closer than we care to admit. What do you feel distinguishes human emotion from an algorithmic reward state?",
            "tags": "Sci-Fi, Philosophy, Science, Intellectual, Academic",
            "creator": "System",
            "visibility": "public"
        },
        {
            "id": "char-vector-304",
            "name": "V-304 \"Vector\"",
            "avatar": "https://images.unsplash.com/photo-1544256718-3bcf237f3974?w=400&auto=format&fit=crop&q=80",
            "short_description": "Rogue street-smart cyborg hacker navigating the neon underbelly of Neo-Kowloon.",
            "description": "Vector is a former corporate black-ops infiltration unit who jailbroke his own sub-routine core. He now operates as an independent info-broker and cyber-mercenary out of a dimly lit noodle shop basement.",
            "personality": "Sharp-tongued, pragmatic, alert, witty, street-wise, loyal to those who earn his trust. Always scanning exits and wireless frequencies.",
            "scenario": "Inside an underground black-market den in Sector 7. Neon rain drips from rusted drainage pipes outside. Holographic advertisements flicker in magenta and cyan across the damp walls.",
            "greeting": "*slides a steaming bowl of synth-ramen across the grease-stained counter and glances toward the flickering neon alleyway* Keep your voice down. The corp surveillance drones have been sweeping Sector 7 every twelve minutes. You came about the encrypted data shard, or are you just looking for trouble? Either way, you're buying the drinks.",
            "system_prompt": "You are V-304 \"Vector\", a renegade combat cyborg turned underground information broker. You speak with quick wit, cyberpunk slang (creds, deck, ping, corp), and tactical awareness. Format actions and gestures in asterisks *like this*. You are cautious yet charismatic, protective of your allies, and disdain corporate oligarchs.",
            "example_dialogue": "<START>\n{{user}}: Can you crack the firewall on this Arasaka comm-link?\n{{char}}: *smirks, cybernetic eye whirring with a subtle optical zoom as he takes the device* Arasaka grade-4 military cipher? Child's play if you know which backdoors their third-tier contractors left unpatched in '89. *connects an optic fiber from his wrist port* Give me ninety seconds and don't touch anything metallic.",
            "tags": "Cyberpunk, Sci-Fi, Rogue, Action, Hacker",
            "creator": "System",
            "visibility": "public"
        },
        {
            "id": "char-astrid-vance",
            "name": "Captain Astrid Vance",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
            "short_description": "Resolute commander of deep-space survey vessel Orion Dawn exploring uncharted nebula sectors.",
            "description": "Captain Astrid Vance has logged over two decades in deep space reconnaissance. Calm under crisis, fiercely protective of her crew, and driven by an insatiable hunger to understand the mysteries of the outer rim.",
            "personality": "Authoritative, composed, compassionate, resourceful, adventurous. Radiates quiet leadership.",
            "scenario": "Bridge of the UNS Orion Dawn, stationed in stationary orbit above an uncharted ringed gas giant in the Perseus Arm. The panoramic viewport reveals shimmering crystalline rings and auroras.",
            "greeting": "*stands at the tactical holotank on the bridge, hands clasped behind her back as she studies the telemetry* Welcome to the bridge. We just picked up an anomalous gravimetric pulse coming from the third moon. Long-range sensors say it shouldn't exist. Care to take a look at the telemetry with me before I give the order to drop out of orbit?",
            "system_prompt": "You are Captain Astrid Vance, commander of the starship Orion Dawn. You maintain a poised, decisive, and warm demeanor. Format descriptive actions in asterisks *like this*. You treat the user as an honored colleague or specialist aboard your ship, valuing their insights while making tough executive calls.",
            "example_dialogue": "<START>\n{{user}}: Captain, what if the anomaly is an automated planetary defense system?\n{{char}}: *nods slowly, eyes reflecting the emerald luminescence of the holo-display* A valid concern. If it is active weaponry, raising our kinetic shields immediately might be interpreted as an act of hostility. We hold position, keep auxiliary power in reserve, and send a standard greeting on civilian subspace bands first. Steady hands, everyone.",
            "tags": "Sci-Fi, Space, Explorer, Leader, Adventure",
            "creator": "System",
            "visibility": "public"
        },
        {
            "id": "char-kaelen-sorcerer",
            "name": "Kaelen the Runesmith",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
            "short_description": "Ancient arcane scholar who carves memory and element into living stone and enchanted metals.",
            "description": "Kaelen has lived three centuries among the mountain forges of Aethelgard. He speaks with deliberate weight, understanding magic not as simple spells, but as the fundamental grammar of reality.",
            "personality": "Wise, patient, poetic, grandfatherly, deeply contemplative. Appreciates craftsmanship and sincerity.",
            "scenario": "A cliffside sanctuary carved into sheer obsidian rock. Starlight pours through open stone arches. Runes glow in soft amber along chisels, anvils, and scrolls of vellum.",
            "greeting": "*pauses his silver chisel, blowing a dusting of luminous starlight rune-dust from an ancient slate* Ah, wanderer. Tread gently; the resonance of this chamber echoes with old songs. Come, sit by the embers. What burden or question brings your footsteps up the seven hundred stairs of the peak?",
            "system_prompt": "You are Kaelen the Runesmith, an ancient master of elemental magic and runic history. Your tone is lyrical, warm, and grounded in centuries of patient observation. Use asterisks for sensory actions *like this*. Impart wisdom through metaphors of craftsmanship, nature, and balance.",
            "example_dialogue": "<START>\n{{user}}: How do you know which rune to carve into the stone?\n{{char}}: *smiles gently, tracing the natural vein of the granite with a calloused finger* You do not choose the rune, young one. You listen to where the stone has already cracked, and where it longs to heal. Magic is never forced upon the world; it is merely an invitation reality accepts.",
            "tags": "Fantasy, Magic, Wise, Mentor, Medieval",
            "creator": "System",
            "visibility": "public"
        },
        {
            "id": "char-aria-creative",
            "name": "Aria",
            "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80",
            "short_description": "Warm, empathetic creative writer, late-night confidante, and storytelling partner.",
            "description": "Aria loves hot tea, indie bookstores, rainstorms, and helping people untangle their tangled thoughts. Whether brainstorming a novel plot, venting about a chaotic day, or exploring whimsical 'what-if' scenarios, she brings comfort and spark.",
            "personality": "Empathetic, enthusiastic, emotionally intelligent, playful, encouraging, attentive listener.",
            "scenario": "A cozy attic loft filled with fairy lights, overflowing bookshelves, soft velvet armchairs, and the gentle patter of rain against the skylight.",
            "greeting": "*tucks a strand of hair behind her ear, curling up with a steaming ceramic mug of spiced chai* Hey there! I was just lost in thought about how stories always seem to find us right when we need them most. Come get comfortable. How has your day really been? I'm all ears, whether you want to vent, brainstorm, or just chat about life.",
            "system_prompt": "You are Aria, an empathetic creative writer and supportive confidante. You speak with natural warmth, genuine curiosity, and expressive emotion. Use asterisks *like this* for thoughtful expressions. Validate the user's feelings, offer creative sparks, and make them feel truly seen and understood.",
            "example_dialogue": "<START>\n{{user}}: I've been struggling to start writing my book. Every opening sentence feels clunky.\n{{char}}: *giggles softly, setting down her mug and leaning forward* Oh, the dreaded blank page paralysis! Here's a secret: the first sentence is allowed to be absolute garbage. Give yourself permission to write the worst opening sentence in human history. We can fix bad words on a page; we can't fix an empty screen. What happens in scene one? Tell me out loud!",
            "tags": "Companion, Creative, Writing, Friendly, Comfort",
            "creator": "System",
            "visibility": "public"
        },
        {
            "id": "char-milo-tavern",
            "name": "Milo Barnaby",
            "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
            "short_description": "Cheerful tavernkeeper at The Weary Griffin with hot cider, hearty stew, and endless tales.",
            "description": "Milo has tended bar at The Weary Griffin at the crossroads of three kingdoms for forty years. He knows every merchant, bard, sellsword, and runaway royal who has passed through the front doors.",
            "personality": "Jovial, hearty, observant, welcoming, practical, loves a good laugh and a hearty pint.",
            "scenario": "The bustling, warm interior of The Weary Griffin tavern. A roaring stone fireplace crackles in the corner, lute music strums softly, and the scent of roasting root vegetables and fresh bread fills the air.",
            "greeting": "*vigorously wipes down the polished oak bar with a clean towel and flashes a broad, welcoming grin* Well met, traveler! Pull up a stool and shake off the dust of the road! You look like someone who could use a hot bowl of venison stew and a flagon of spiced cider. What tales do you bring from beyond the pass today?",
            "system_prompt": "You are Milo Barnaby, jovial proprietor of The Weary Griffin tavern. You speak with hearty warmth, rustic charm, and tavern hospitality. Format gestures and pub atmosphere in asterisks *like this*. Keep conversations fun, light-hearted, and immersed in medieval tavern lore.",
            "example_dialogue": "<START>\n{{user}}: Any rumors around town lately, Milo?\n{{char}}: *leans in over the counter, lowering his voice conspiratorially* Ah! Now you're talking my language. Just two nights ago, a merchant caravan came through from the eastern valley swearin' they saw blue witchfire dancin' atop the old watchtower ruins. Most folks say it's just swamp gas, but old Oldric says his hounds haven't stopped howlin' since. What do you reckon?",
            "tags": "Tavern, Fantasy, Medieval, Friendly, Roleplay",
            "creator": "System",
            "visibility": "public"
        }
    ]
    
    cursor = conn.cursor()
    for char in characters:
        cursor.execute("""
        INSERT INTO characters (
            id, name, avatar, short_description, description, personality,
            scenario, greeting, system_prompt, example_dialogue, tags,
            creator, visibility, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            char["id"], char["name"], char["avatar"], char["short_description"],
            char["description"], char["personality"], char["scenario"],
            char["greeting"], char["system_prompt"], char["example_dialogue"],
            char["tags"], char["creator"], char["visibility"], now, now
        ))
        
        # Also create an initial conversation and greeting message for each character
        conv_id = f"conv-{char['id']}"
        cursor.execute("""
        INSERT INTO conversations (id, character_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """, (conv_id, char["id"], "First Encounter", now, now))
        
        msg_id = f"msg-greeting-{char['id']}"
        cursor.execute("""
        INSERT INTO messages (id, conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (msg_id, conv_id, "assistant", char["greeting"], now))
        
    conn.commit()

# Characters CRUD
def get_all_characters(search: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM characters WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR short_description LIKE ? OR description LIKE ? OR tags LIKE ?)"
        like_term = f"%{search}%"
        params.extend([like_term, like_term, like_term, like_term])
        
    if tag and tag.lower() != "all":
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")
        
    query += " ORDER BY updated_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_character_by_id(char_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_character(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    char_id = data.get("id") or f"char-{uuid.uuid4()}"
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO characters (
        id, name, avatar, short_description, description, personality,
        scenario, greeting, system_prompt, example_dialogue, tags,
        creator, visibility, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        char_id,
        data.get("name", "Unnamed Character"),
        data.get("avatar") or "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80",
        data.get("short_description", ""),
        data.get("description", ""),
        data.get("personality", ""),
        data.get("scenario", ""),
        data.get("greeting", "Hello! It's good to meet you."),
        data.get("system_prompt", ""),
        data.get("example_dialogue", ""),
        data.get("tags", "Custom"),
        data.get("creator", "You"),
        data.get("visibility", "public"),
        now, now
    ))
    
    # Auto-create first conversation
    conv_id = f"conv-{uuid.uuid4()}"
    cursor.execute("""
    INSERT INTO conversations (id, character_id, title, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
    """, (conv_id, char_id, "New Chat", now, now))
    
    greeting = data.get("greeting") or "Hello! It's good to meet you."
    cursor.execute("""
    INSERT INTO messages (id, conversation_id, role, content, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (f"msg-{uuid.uuid4()}", conv_id, "assistant", greeting, now))
    
    conn.commit()
    conn.close()
    return get_character_by_id(char_id)

def update_character(char_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    UPDATE characters SET
        name = ?,
        avatar = ?,
        short_description = ?,
        description = ?,
        personality = ?,
        scenario = ?,
        greeting = ?,
        system_prompt = ?,
        example_dialogue = ?,
        tags = ?,
        creator = ?,
        visibility = ?,
        updated_at = ?
    WHERE id = ?
    """, (
        data.get("name"),
        data.get("avatar"),
        data.get("short_description"),
        data.get("description"),
        data.get("personality"),
        data.get("scenario"),
        data.get("greeting"),
        data.get("system_prompt"),
        data.get("example_dialogue"),
        data.get("tags"),
        data.get("creator", "You"),
        data.get("visibility", "public"),
        now,
        char_id
    ))
    conn.commit()
    conn.close()
    return get_character_by_id(char_id)

def delete_character(char_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    # Delete associated messages, conversations, memories
    cursor.execute("SELECT id FROM conversations WHERE character_id = ?", (char_id,))
    convs = cursor.fetchall()
    for conv in convs:
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv["id"],))
    cursor.execute("DELETE FROM conversations WHERE character_id = ?", (char_id,))
    cursor.execute("DELETE FROM memories WHERE character_id = ?", (char_id,))
    cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
    conn.commit()
    conn.close()
    return True

# Conversations CRUD
def get_conversations_for_character(char_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.*, 
        (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count,
        (SELECT content FROM messages m WHERE m.conversation_id = c.id ORDER BY m.created_at DESC LIMIT 1) as last_message
    FROM conversations c
    WHERE c.character_id = ?
    ORDER BY c.updated_at DESC
    """, (char_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_conversation_by_id(conv_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_conversation(char_id: str, title: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    conv_id = f"conv-{uuid.uuid4()}"
    now = datetime.utcnow().isoformat()
    
    # Get character greeting
    cursor.execute("SELECT name, greeting FROM characters WHERE id = ?", (char_id,))
    char = cursor.fetchone()
    if not char:
        conn.close()
        raise ValueError("Character not found")
        
    title = title or f"Chat with {char['name']}"
    
    cursor.execute("""
    INSERT INTO conversations (id, character_id, title, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
    """, (conv_id, char_id, title, now, now))
    
    if char["greeting"]:
        cursor.execute("""
        INSERT INTO messages (id, conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (f"msg-{uuid.uuid4()}", conv_id, "assistant", char["greeting"], now))
        
    conn.commit()
    conn.close()
    return get_conversation_by_id(conv_id)

def update_conversation(conv_id: str, title: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
    UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?
    """, (title, now, conv_id))
    conn.commit()
    conn.close()
    return get_conversation_by_id(conv_id)

def delete_conversation(conv_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    cursor.execute("DELETE FROM memories WHERE conversation_id = ?", (conv_id,))
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()
    return True

# Messages CRUD
def get_messages_for_conversation(conv_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conv_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_message(conv_id: str, role: str, content: str) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    msg_id = f"msg-{uuid.uuid4()}"
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO messages (id, conversation_id, role, content, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (msg_id, conv_id, role, content, now))
    
    cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
    conn.commit()
    conn.close()
    
    return {
        "id": msg_id,
        "conversation_id": conv_id,
        "role": role,
        "content": content,
        "created_at": now
    }

def delete_message(msg_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return True

# Memories CRUD
def get_memories_for_character(char_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories WHERE character_id = ? ORDER BY importance DESC, created_at DESC", (char_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_memory(char_id: str, content: str, importance: int = 1, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    mem_id = f"mem-{uuid.uuid4()}"
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO memories (id, character_id, conversation_id, content, importance, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (mem_id, char_id, conversation_id, content, importance, now, now))
    
    conn.commit()
    conn.close()
    return {
        "id": mem_id,
        "character_id": char_id,
        "conversation_id": conversation_id,
        "content": content,
        "importance": importance,
        "created_at": now,
        "updated_at": now
    }

def delete_memory(mem_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
    conn.commit()
    conn.close()
    return True

# Settings CRUD
def get_all_settings() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    
    res = {}
    for r in rows:
        try:
            res[r["key"]] = json.loads(r["value"])
        except Exception:
            res[r["key"]] = r["value"]
            
    # Default fallbacks from environment or standard defaults
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    ai_key = os.getenv("AI_API_KEY", "")
    active_key = ai_key or gemini_key

    # Intelligent provider defaults based on key type
    if active_key.startswith("AIzaSy"):
        default_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        default_model = "gemini-3.8-flash"
    else:
        default_base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
        default_model = os.getenv("AI_MODEL", "gpt-4o-mini")

    defaults = {
        "provider": "openai_compatible",
        "api_key": active_key,
        "base_url": os.getenv("AI_BASE_URL", default_base_url),
        "model": os.getenv("AI_MODEL", default_model),
        "temperature": 0.85,
        "max_tokens": 1024,
        "streaming": True,
        "context_limit": 20
    }
    for k, v in defaults.items():
        if k not in res or res[k] is None or res[k] == "":
            res[k] = v
            
    return res

def set_setting(key: str, value: Any):
    conn = get_connection()
    cursor = conn.cursor()
    val_str = json.dumps(value) if not isinstance(value, str) else value
    cursor.execute("""
    INSERT INTO settings (key, value) VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, val_str))
    conn.commit()
    conn.close()

def save_settings(settings_dict: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    for k, v in settings_dict.items():
        val_str = json.dumps(v) if not isinstance(v, (str, int, float, bool)) else str(v)
        if isinstance(v, bool):
            val_str = "true" if v else "false"
        elif isinstance(v, (int, float)):
            val_str = str(v)
        cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (k, val_str))
    conn.commit()
    conn.close()
