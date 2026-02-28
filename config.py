# ─────────────────────────────────────────────
#   IRON MIND — Configuration File
#   Edit your settings here
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file if present

# ── Assistant Identity ────────────────────────
ASSISTANT_NAME = "MAZE"

# ── Voice Settings ────────────────────────────
VOICE_RATE   = 175       # Words per minute (150–200 recommended)
VOICE_VOLUME = 1.0       # 0.0 to 1.0

# ── AI Brain Settings ─────────────────────────
# Option 1: OpenAI (requires API key)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Option 2: Google Gemini (requires API key)
GEMINI_API_KEY = "AIzaSyCG6KGPbqyYThduoZ7OK4TRJCq-5KXfYPE"

# Which AI provider to use: "openai" | "gemini" | "offline"
AI_PROVIDER = "gemini"   # ← Using Gemini AI brain

# ── Memory Settings ───────────────────────────
MAX_MEMORY_TURNS = 10     # How many past messages to remember

# ── Logging ───────────────────────────────────
LOG_FILE = "logs/assistant.log"
ENABLE_LOGGING = True
