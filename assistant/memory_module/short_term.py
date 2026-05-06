"""
MAZE — Short-Term Memory
Manages conversation history with auto-save and context building.
"""

import os
import json

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import MAX_MEMORY_TURNS

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_FILE = os.path.join(_PROJECT_DIR, "memory", "chat_history.json")
USER_PROFILE_FILE = os.path.join(_PROJECT_DIR, "memory", "user_profile.txt")

_memory = []

# ── Conversation Awareness ───────────────────────────
# Track the last action topic so follow-up commands work naturally
_last_topic = None       # e.g., "music", "search", "app", "task"
_last_query = ""         # e.g., "chill music", "python tutorial"
_last_action_time = 0    # timestamp of last action


def load_memory():
    """Load conversation history from disk."""
    global _memory
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                _memory = json.load(f)
    except:
        _memory = []


def save_memory():
    """Save conversation history to disk (limited to MAX_MEMORY_TURNS)."""
    try:
        mem_to_save = _memory[-(MAX_MEMORY_TURNS * 2):]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem_to_save, f, indent=2)
    except:
        pass


def get_memory() -> list:
    """Get the current conversation memory."""
    return _memory


def add_exchange(user_text: str, ai_text: str):
    """Add a user-AI exchange to memory."""
    _memory.append({"role": "user", "parts": [{"text": user_text}]})
    _memory.append({"role": "model", "parts": [{"text": ai_text}]})
    save_memory()


def add_user_message(text: str):
    """Add a user message to memory."""
    _memory.append({"role": "user", "parts": [{"text": text}]})
    save_memory()


def add_ai_message(text: str):
    """Add an AI response to memory."""
    _memory.append({"role": "model", "parts": [{"text": text}]})
    save_memory()


def get_exchange_count() -> int:
    """Get the total number of exchanges."""
    return len(_memory) // 2


def get_user_profile() -> str:
    """Load user facts from profile file."""
    try:
        if os.path.exists(USER_PROFILE_FILE):
            with open(USER_PROFILE_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
    except:
        pass
    return ""


def handle_remember(command: str) -> str:
    """Save user facts to long-term memory."""
    text = command
    for r in ["remember that", "remember", "memorize that", "memorize", "note that"]:
        if command.startswith(r):
            text = command[len(r):].strip()
            break

    if text:
        try:
            with open(USER_PROFILE_FILE, "a", encoding="utf-8") as f:
                f.write(f"- {text}\n")
            return f"Got it. I'll remember that {text}."
        except:
            return "I couldn't save that to memory right now."
    return "What would you like me to remember?"


def set_last_topic(topic: str, query: str = ""):
    """Track the last action topic for follow-up awareness."""
    global _last_topic, _last_query, _last_action_time
    import time
    _last_topic = topic
    _last_query = query
    _last_action_time = time.time()


def get_last_topic() -> tuple:
    """Get the last topic and query. Returns (topic, query) or (None, '') if stale."""
    import time
    # Topic is stale after 120 seconds
    if _last_topic and (time.time() - _last_action_time) < 120:
        return _last_topic, _last_query
    return None, ""


# Load memory on import
load_memory()
