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
VOICE_RATE   = 175       # Words per minute (150-200 recommended)
VOICE_VOLUME = 1.0       # 0.0 to 1.0

# ── Conversation Flow ─────────────────────────
CONVERSATION_PAUSE = 5         # Legacy — only used as max cap
CONVERSATION_PAUSE_SHORT = 1.5 # Pause after short responses (< 50 chars, e.g. "Paused.")
CONVERSATION_PAUSE_LONG = 3    # Pause after longer responses
ENABLE_AVATAR = True           # Show floating anime avatar on screen

# ── Contacts & Messaging ──────────────────────
# Add phone numbers (with country code) for WhatsApp
CONTACTS = {
    "yashank": "+917990480791", # Example: Replace with actual number
    "mom": "+917284965188",
}
# Add usernames for Instagram
INSTAGRAM_USERS = {
    "yashank": "yashan_ig", # Example: Replace with actual username
}

# ── AI Brain Settings ─────────────────────────
# Option 0: Ollama — LOCAL AI (NO internet, NO API key needed!)
# Make sure Ollama is running: open a terminal and run -> ollama serve
# Install Mistral model once:  ollama pull mistral
OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")  # Local Ollama server
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")                 # Change to "llama3", "phi3", etc.

# Option 1: OpenAI (requires API key)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Option 2: Google Gemini (requires API key)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Option 3: OpenRouter (access GPT-4, Claude, Llama, etc. via one key)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Which AI provider to use: "ollama" | "gemini" | "openrouter" | "offline"
# "ollama" = fully local Mistral brain (no API key, no internet needed)
AI_PROVIDER = "ollama"   # <- Primary AI brain (falls back to Gemini -> OpenRouter -> offline)

# ── Memory Settings ───────────────────────────
MAX_MEMORY_TURNS = 10     # How many past messages to remember

# ── Logging ───────────────────────────────────
LOG_FILE = "logs/assistant.log"
ENABLE_LOGGING = True

# ── Telegram Bot (control MAZE from your phone) ──
# 1. Open Telegram -> search @BotFather -> send /newbot -> follow steps
# 2. Copy the bot token and paste it below
# 3. Start a chat with your bot, send /start to get your user ID
# 4. Add your user ID to TELEGRAM_ALLOWED_USERS list
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_USERS = [6243523432]  # Leave empty for now -- bot will show your numeric ID when you send /start
