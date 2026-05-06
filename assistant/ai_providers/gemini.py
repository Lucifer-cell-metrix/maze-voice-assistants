"""
MAZE — Google Gemini AI Provider
Cloud AI brain with rate limit handling and model fallback chain.
"""

import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import GEMINI_API_KEY, MAX_MEMORY_TURNS

# Rate limit tracking
_gemini_failed_count = 0
_gemini_last_fail_time = 0
GEMINI_COOLDOWN = 300  # 5 minutes cooldown after rate limit

MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def is_on_cooldown() -> bool:
    """Check if Gemini is on cooldown from rate limiting."""
    global _gemini_failed_count, _gemini_last_fail_time
    if _gemini_failed_count >= 3:
        elapsed = time.time() - _gemini_last_fail_time
        if elapsed >= GEMINI_COOLDOWN:
            _gemini_failed_count = 0
            print("   🔄 Retrying Gemini AI connection...")
            return False
        return True
    return False


def is_available() -> bool:
    """Check if Gemini is configured and not on cooldown."""
    return bool(GEMINI_API_KEY) and _gemini_failed_count < 3


def reset_cooldown():
    """Reset the cooldown counter."""
    global _gemini_failed_count
    _gemini_failed_count = 0


def gemini_response(command: str, memory: list, save_memory_fn,
                    user_facts: str = "", emotion_context: str = "",
                    fallback_fn=None) -> str:
    """Get a response from Google Gemini with model fallback chain."""
    global _gemini_failed_count, _gemini_last_fail_time

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        memory.append({"role": "user", "parts": [{"text": command}]})
        save_memory_fn()

        facts_text = f"\n\nHere are some things you know about the user:\n{user_facts}" if user_facts else ""
        emotion_text = ""
        if emotion_context:
            emotion_text = f"\n\nThe user's current emotional state appears to be: {emotion_context}. Adjust your tone accordingly — be more supportive if frustrated, match energy if excited, offer encouragement if sad."

        system_instruction = (
            "You are MAZE, an advanced AI assistant inspired by JARVIS from Iron Man. "
            "Intelligent, calm, professional, friendly, and motivating. "
            "Keep responses concise but COMPLETE — always finish your sentences. "
            "Give 3-5 sentence answers. No markdown or formatting. "
            "Never cut off mid-thought. "
            "NEVER include raw code in your responses — if asked for code, "
            "describe what the code does in plain English instead. "
            "Your responses will be spoken aloud, so keep them natural and conversational. "
            "IMPORTANT: You CANNOT make phone calls, send texts, or access contacts. "
            "NEVER pretend to dial numbers, simulate calls, or generate fake transcripts. "
            f"If asked to call or message someone, say you can open WhatsApp for them."
            f"{facts_text}{emotion_text}"
        )

        last_error = None
        for model_name in MODELS_TO_TRY:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=memory[-MAX_MEMORY_TURNS:],
                    config={
                        "system_instruction": system_instruction,
                        "max_output_tokens": 500,
                        "temperature": 0.7,
                    }
                )
                reply = response.text.strip()
                memory.append({"role": "model", "parts": [{"text": reply}]})
                save_memory_fn()
                _gemini_failed_count = 0
                return reply
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    _gemini_failed_count = 3
                    _gemini_last_fail_time = time.time()
                    memory.pop()
                    print(f"   ⚠️  Gemini API rate limited. Using offline brain for {GEMINI_COOLDOWN // 60} minutes.")
                    if fallback_fn:
                        return fallback_fn(command)
                    return "I'm rate limited right now. Let me try again in a few minutes."
                elif "404" in last_error or "NOT_FOUND" in last_error:
                    print(f"   ⚠️  Model {model_name} not found, trying next...")
                    continue
                else:
                    break

        _gemini_failed_count += 1
        _gemini_last_fail_time = time.time()
        memory.pop()
        print(f"   ⚠️  Gemini AI unavailable — using offline brain. (Error: {last_error[:80] if last_error else 'unknown'})")
        if fallback_fn:
            return fallback_fn(command)
        return "I couldn't reach my cloud brain. Using offline mode."

    except Exception as e:
        _gemini_failed_count += 1
        _gemini_last_fail_time = time.time()
        print(f"   ⚠️  Gemini AI unavailable — using offline brain. (Error: {str(e)[:80]})")
        if fallback_fn:
            return fallback_fn(command)
        return "Cloud AI is down. Using offline mode."
