"""
MAZE — OpenRouter AI Provider
Cloud AI fallback using free models from OpenRouter.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import OPENROUTER_API_KEY, MAX_MEMORY_TURNS

# Free models to try in order
OPENROUTER_MODELS = [
    "google/gemma-3n-e4b-it:free",
    "arcee-ai/trinity-large-preview:free",
]


def is_available() -> bool:
    """Check if OpenRouter is configured."""
    return bool(OPENROUTER_API_KEY)


def openrouter_response(command: str, memory: list, save_memory_fn,
                        user_facts: str = "", emotion_context: str = "",
                        fallback_fn=None) -> str:
    """Send command to OpenRouter API with model fallback chain."""
    try:
        import requests as req

        memory.append({"role": "user", "parts": [{"text": command}]})
        save_memory_fn()

        facts_text = f"\n\nHere are some things you know about the user:\n{user_facts}" if user_facts else ""
        emotion_text = ""
        if emotion_context:
            emotion_text = f"\n\nThe user seems {emotion_context}. Adjust your tone accordingly."

        # Convert memory to OpenAI format
        messages = [
            {
                "role": "system",
                "content": (
                    "You are MAZE, an advanced AI assistant. You are professional, sharp, and efficient. "
                    "Keep responses concise — 3-5 sentences. No markdown or formatting. "
                    f"Your responses will be spoken aloud, so keep them natural and conversational."
                    f"{facts_text}{emotion_text}"
                )
            }
        ]
        for m in memory[-MAX_MEMORY_TURNS:]:
            role = "assistant" if m["role"] == "model" else "user"
            text = m["parts"][0]["text"] if isinstance(m["parts"], list) else str(m["parts"])
            messages.append({"role": role, "content": text})

        last_error = None
        for model_name in OPENROUTER_MODELS:
            try:
                response = req.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "max_tokens": 500,
                        "temperature": 0.7,
                    },
                    timeout=15,
                )

                data = response.json()
                if response.status_code == 200 and "choices" in data:
                    reply = data["choices"][0]["message"]["content"].strip()
                    memory.append({"role": "model", "parts": [{"text": reply}]})
                    save_memory_fn()
                    return reply
                else:
                    last_error = data.get("error", {}).get("message", str(data))
                    print(f"   ⚠️  Model {model_name} unavailable, trying next...")
                    continue
            except Exception as e:
                last_error = str(e)
                continue

        # All models failed
        memory.pop()
        print(f"   ⚠️  OpenRouter error: {str(last_error)[:80]}")
        if fallback_fn:
            return fallback_fn(command)
        return "Cloud AI is unavailable. Using offline mode."

    except Exception as e:
        if memory and memory[-1].get("role") == "user":
            memory.pop()
        print(f"   ⚠️  OpenRouter unavailable: {str(e)[:80]}")
        if fallback_fn:
            return fallback_fn(command)
        return "Cloud AI is unavailable. Using offline mode."
