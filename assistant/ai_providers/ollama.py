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
    """Ask Ollama to convert user input into a structured list of JSON action steps using native Tool Calling."""
    import requests as req
    from assistant.ai_providers.tools_schema import OLLAMA_TOOLS

    messages = [
        {"role": "system", "content": "You are MAZE, an AI assistant controller. Use the provided tools to execute the user's command. If the user is just chatting or asking a factual question, use the chat tool."},
        {"role": "user", "content": user_input}
    ]

    url = f"{OLLAMA_URL}/api/chat"
    data = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "tools": OLLAMA_TOOLS
    }

    try:
        response = req.post(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        message = result.get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        steps = []
        if tool_calls:
            for tc in tool_calls:
                func = tc.get("function", {})
                action = func.get("name", "")
                args = func.get("arguments", {})
                
                # Map to 'value' for brain router
                value = ""
                for k, v in args.items():
                    if k in ["name", "query", "text", "level", "keyword", "description"]:
                        value = v
                        break
                if not value and args:
                    value = list(args.values())[0]
                    
                steps.append({"action": action, "value": value})
            return steps
            
        if message.get("content"):
             return [{"action": "chat", "value": message["content"]}]

    except Exception as e:
        print(f"   ⚠️  Ollama Intent parse error: {e}")
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
