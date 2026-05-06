"""
MAZE — Ollama (Local AI Brain)
Handles intent detection and conversational responses using local Mistral model.
"""

import json
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import OLLAMA_URL, OLLAMA_MODEL, MAX_MEMORY_TURNS


def ask_llm(prompt: str, timeout: int = 30) -> str:
    """Send a raw prompt to local Ollama server and return the response text.
    Raises requests.ConnectionError if Ollama is not running."""
    import requests as req
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    response = req.post(url, json=data, timeout=timeout)
    response.raise_for_status()
    return response.json()["response"].strip()


def get_intent(user_input: str) -> list:
    """Ask Ollama to convert user input into a structured list of JSON action steps.
    Returns a list of dicts like [{"action": "...", "value": "..."}].
    Falls back to empty list on any parse failure."""
    prompt = (
        "You are MAZE, an AI assistant controller running on the user's PC.\n\n"
        "Convert the user input into a JSON list of steps to execute.\n\n"
        "Available actions (use ONLY these):\n"
        "- open_app(name)          open apps like chrome, notepad, vscode, calculator\n"
        "- search_youtube(query)   search or play something on YouTube\n"
        "- search_google(query)    search on Google\n"
        "- open_website(name)      open sites like github, gmail, spotify\n"
        "- play_music(query)       play music or song on YouTube\n"
        "- set_volume(level)       level = up, down, mute, or a number 0-100\n"
        "- set_brightness(level)   level = up, down, or a number 0-100\n"
        "- add_task(text)          add a task to the task list\n"
        "- take_note(text)         save a note\n"
        "- write_code(description) generate code for a task\n"
        "- get_weather(city)       get real-time weather for a city\n"
        "- call_person(name)       call someone (opens WhatsApp)\n"
        "- send_message(name)      message someone (opens WhatsApp/Instagram)\n"
        "- find_internship(keyword) find internships on Internshala\n"
        "- find_file(name)         find and open a file on the computer\n"
        "- chat(text)              answer a question or have a conversation (fallback)\n\n"
        f"User input: \"{user_input}\"\n\n"
        "Rules:\n"
        "- Return ONLY a valid JSON array, nothing else.\n"
        "- Use as many steps as needed.\n"
        "- For conversational or factual questions, use a single chat action.\n\n"
        "Example for open chrome and search python tutorials:\n"
        '[{"action": "open_app", "value": "chrome"}, {"action": "search_google", "value": "python tutorials"}]\n\n'
        "Return JSON array:"
    )
    try:
        raw = ask_llm(prompt, timeout=20)

        # Cleanup markdown formatting
        if "```json" in raw:
            raw = raw.split("```json")[-1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].strip()

        data = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\[\s*\{.*?\}\s*\]', raw, re.DOTALL)
            if match:
                data = json.loads(match.group())

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            valid_steps = [item for item in data if isinstance(item, dict)]
            if valid_steps:
                return valid_steps

    except Exception as e:
        print(f"   ⚠️  Intent parse error: {e}")
    return []


def ollama_chat(command: str, memory: list, user_facts: str = "",
                emotion_context: str = "") -> str:
    """Get a conversational reply from Ollama using structured chat endpoint."""
    import requests as req

    facts_text = f"\n\nHere are some things you know about the user:\n{user_facts}" if user_facts else ""
    emotion_text = ""
    if emotion_context:
        emotion_text = f"\n\nThe user's current emotional state appears to be: {emotion_context}. Adjust your tone accordingly."

    system = (
        "You are MAZE, an advanced AI assistant inspired by JARVIS from Iron Man. "
        "Intelligent, calm, professional, friendly, and motivating. "
        "Keep responses concise but COMPLETE — always finish your sentences. "
        "Give 2-4 sentence answers. No markdown or bullet points. "
        "Your responses will be spoken aloud, so keep them natural and conversational. "
        "IMPORTANT: You CANNOT make phone calls, send texts, or access contacts. "
        "NEVER pretend to dial numbers, simulate calls, or generate fake call transcripts. "
        f"If asked to call or message someone, say you can open WhatsApp for them to do it."
        f"{facts_text}{emotion_text}"
    )

    messages = [{"role": "system", "content": system}]

    for m in memory[-MAX_MEMORY_TURNS:]:
        role = "assistant" if m["role"] == "model" else "user"
        text = m["parts"][0]["text"] if isinstance(m["parts"], list) else str(m["parts"])
        messages.append({"role": role, "content": text})

    messages.append({"role": "user", "content": command})

    url = f"{OLLAMA_URL}/api/chat"
    data = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }

    try:
        response = req.post(url, json=data, timeout=30)
        response.raise_for_status()
        reply = response.json()["message"]["content"].strip()
        return reply
    except Exception as e:
        return f"I encountered an error connecting to my local brain. Error: {str(e)[:50]}"
