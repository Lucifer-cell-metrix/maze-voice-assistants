"""
MAZE — Long-Term Memory
Persistent facts and conversation summaries across sessions.
Auto-summarizes conversations every 20 exchanges.
"""

import os
import json
import time

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LONG_TERM_FILE = os.path.join(_PROJECT_DIR, "memory", "long_term.json")

_long_term = {
    "summaries": [],        # Auto-generated conversation summaries
    "last_summary_at": 0,   # Exchange count when last summary was made
}


def load_long_term():
    """Load long-term memory from disk."""
    global _long_term
    try:
        if os.path.exists(LONG_TERM_FILE):
            with open(LONG_TERM_FILE, "r", encoding="utf-8") as f:
                _long_term = json.load(f)
    except:
        _long_term = {"summaries": [], "last_summary_at": 0}


def save_long_term():
    """Save long-term memory to disk."""
    try:
        os.makedirs(os.path.dirname(LONG_TERM_FILE), exist_ok=True)
        with open(LONG_TERM_FILE, "w", encoding="utf-8") as f:
            json.dump(_long_term, f, indent=2)
    except:
        pass


def get_summaries() -> list:
    """Get all stored conversation summaries."""
    return _long_term.get("summaries", [])


def get_context_for_ai() -> str:
    """Build context string from long-term memory for AI system prompt.
    Returns a concise paragraph of what MAZE remembers across sessions."""
    summaries = get_summaries()
    if not summaries:
        return ""

    # Use last 5 summaries max (to keep context window small)
    recent = summaries[-5:]
    context_parts = ["Previous conversation summaries:"]
    for s in recent:
        context_parts.append(f"- {s['summary']}")
    return "\n".join(context_parts)


def should_summarize(exchange_count: int) -> bool:
    """Check if it's time to auto-summarize (every 20 exchanges)."""
    last = _long_term.get("last_summary_at", 0)
    return exchange_count - last >= 20


def add_summary(summary: str, exchange_count: int):
    """Store a conversation summary."""
    _long_term["summaries"].append({
        "summary": summary,
        "timestamp": time.time(),
        "exchanges": exchange_count,
    })
    _long_term["last_summary_at"] = exchange_count

    # Keep max 20 summaries
    if len(_long_term["summaries"]) > 20:
        _long_term["summaries"] = _long_term["summaries"][-20:]

    save_long_term()


def auto_summarize(memory: list, exchange_count: int):
    """Auto-summarize recent conversation using AI (if available).
    Called from the brain after every response."""
    if not should_summarize(exchange_count):
        return

    # Get last 20 exchanges
    recent = memory[-40:]  # 20 exchanges = 40 messages (user + model)
    if len(recent) < 10:
        return

    # Build conversation text for summarization
    conv_text = ""
    for m in recent:
        role = "User" if m["role"] == "user" else "MAZE"
        text = m["parts"][0]["text"] if isinstance(m["parts"], list) else str(m["parts"])
        conv_text += f"{role}: {text}\n"

    # Try to summarize with AI
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from config import GEMINI_API_KEY, AI_PROVIDER, OLLAMA_URL, OLLAMA_MODEL

        summary = None

        if AI_PROVIDER == "ollama":
            try:
                import requests as req
                prompt = (
                    "Summarize this conversation in 2-3 sentences. "
                    "Focus on: what the user talked about, what they asked for, "
                    "any personal facts mentioned (name, interests, projects).\n\n"
                    f"{conv_text}\n\nSummary:"
                )
                data = {
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                }
                response = req.post(f"{OLLAMA_URL}/api/generate", json=data, timeout=15)
                response.raise_for_status()
                summary = response.json()["response"].strip()
            except:
                pass

        if not summary and GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    contents=(
                        "Summarize this conversation in 2-3 sentences. "
                        "Focus on: what the user talked about, what they asked for, "
                        f"any personal facts mentioned.\n\n{conv_text}\n\nSummary:"
                    ),
                    config={"max_output_tokens": 200, "temperature": 0.3}
                )
                summary = response.text.strip()
            except:
                pass

        if summary:
            add_summary(summary, exchange_count)
            print(f"   🧠 Long-term memory updated: \"{summary[:80]}...\"")

    except Exception as e:
        print(f"   ⚠️  Auto-summary failed: {str(e)[:50]}")


# Load long-term memory on import
load_long_term()
