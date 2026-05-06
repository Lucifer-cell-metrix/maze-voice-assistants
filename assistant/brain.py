"""
MAZE — AI Brain Module (v4 — Modular Architecture)
Slim router that delegates to action modules and AI providers.
Includes: conversation awareness, emotion-aware responses, smart memory.
"""

import sys
import os
import time
import datetime
import random
import webbrowser
import urllib.parse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import AI_PROVIDER, GEMINI_API_KEY, OPENROUTER_API_KEY

# ── Import Action Modules ────────────────────────────
from assistant.actions.helpers import contains_any, has_word, normalize_command
from assistant.actions.apps import open_app, find_file, APPS, BROWSER_APPS
from assistant.actions.media import handle_media_control, play_on_youtube, _yt_playlist, _yt_current_idx
from assistant.actions.web import handle_search, open_website
from assistant.actions.tasks import handle_tasks
from assistant.actions.notes import handle_notes
from assistant.actions.system import handle_system_control, volume_up, volume_down, volume_mute, get_brightness, set_brightness
from assistant.actions.messaging import handle_messaging, handle_calling
from assistant.actions.code import handle_code_writing
from assistant.actions.math_calc import handle_math
from assistant.actions.internship import handle_internship

# ── Import Memory Modules ────────────────────────────
from assistant.memory_module.short_term import (
    get_memory, save_memory, add_exchange, add_user_message, add_ai_message,
    get_user_profile, handle_remember, get_exchange_count,
    set_last_topic, get_last_topic
)
from assistant.memory_module.long_term import (
    get_context_for_ai, auto_summarize
)

# ── Import AI Providers ──────────────────────────────
from assistant.ai_providers.ollama import get_intent, ollama_chat, ask_llm
from assistant.ai_providers.gemini import gemini_response, is_available as gemini_available, is_on_cooldown as gemini_on_cooldown
from assistant.ai_providers.openrouter import openrouter_response, is_available as openrouter_available

# ── Expose for main.py backward compatibility ────────
# main.py imports _yt_playlist, _yt_current_idx from brain
# Re-export from media module
import assistant.actions.media as _media_module


# ── Motivational Quotes & Jokes ──────────────────────
MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. Keep pushing.",
    "You're one project away from changing your life. Don't stop now.",
    "Discipline beats motivation every single day. Stay consistent.",
    "The code you write today is the career you build tomorrow.",
    "Small daily improvements lead to stunning results. Keep going.",
    "Don't watch the clock. Do what it does. Keep going.",
    "Your future self will thank you for the work you put in today.",
    "Every expert was once a beginner. You're on the right path.",
    "Success is not final, failure is not fatal. Keep coding.",
    "Belief in yourself is the first step to building something great.",
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "There are only 10 types of people in the world. Those who understand binary and those who don't.",
    "A SQL query walks into a bar, walks up to two tables and asks, Can I join you?",
    "Why do Java developers wear glasses? Because they can't C sharp.",
    "What's a programmer's favorite hangout place? Foo Bar.",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
    "How many programmers does it take to change a light bulb? None. That's a hardware problem.",
    "What is a programmer's favorite snack? Microchips.",
    "Why did the developer go broke? Because he used up all his cache.",
]


# ── Smart Offline Brain ──────────────────────────────

def smart_offline_response(command: str) -> str:
    """Smart offline brain — handles real tasks with flexible matching."""
    command = normalize_command(command)

    # ── Greetings ──
    if (has_word(command, ["hello", "hi", "hey", "heyy", "howdy", "yo", "hola", "namaste"])
        or contains_any(command, ["what's up", "whats up"])
        ) and not contains_any(command, ["open", "search", "youtube", "google", "task",
                                           "calculate", "notepad", "chrome", "show"]):
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good morning! MAZE is ready. What's your mission today?"
        elif hour < 17:
            return "Good afternoon! What can I help you with?"
        elif hour < 21:
            return "Good evening! Ready to get productive?"
        return "Good night! What are we working on?"

    # ── Identity ──
    if contains_any(command, ["who are you", "who r u", "hu r u", "your name",
                               "what are you", "what r u", "what is your name",
                               "tell me about yourself", "introduce yourself"]):
        return ("I am MAZE, your personal AI assistant. Built to help you learn, "
                "build, and grow. I can open apps, search the web, manage tasks, "
                "do math, find internships, and much more. All for free!")

    if contains_any(command, ["what can you do", "your capabilities", "help me",
                               "what do you do", "features"]) or command.strip() == "help":
        return ("I can open apps like Notepad, Chrome, Brave, VS Code, and Paint. "
                "I play songs on YouTube, search Google and Wikipedia. "
                "I manage tasks and notes. I open WhatsApp, Instagram, GitHub. "
                "I control volume and brightness. I find internships on Internshala. "
                "I do math, tell time, motivate you, and tell jokes. Just ask!")

    # ── Time & Date ──
    if (contains_any(command, ["what time", "the time", "current time", "clock"])
        or (command.strip() == "time")
        or (has_word(command, ["time"]) and not contains_any(command, ["task", "open", "youtube", "times"]))):
        now = datetime.datetime.now()
        return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

    if (contains_any(command, ["what day", "today's date", "which day"])
        or (command.strip() in ["date", "today"])):
        return datetime.datetime.now().strftime("Today is %A, %B %d, %Y.")

    # ── Media Controls ──
    result = handle_media_control(command)
    if result:
        set_last_topic("music")
        return result

    # ── YouTube / Play ──
    if "youtube" in command or has_word(command, ["play"]):
        result = handle_search(command)
        if result:
            set_last_topic("music", command)
            return result

    # ── Open commands ──
    if contains_any(command, ["open", "launch", "start", "run"]):
        result = handle_search(command)
        if result:
            return result
        result = open_website(command)
        if result:
            return result
        app_query = command
        for remove in ["open", "launch", "start", "run"]:
            app_query = app_query.replace(remove, " ")
        app_query = app_query.strip()
        result = open_app(app_query)
        if result:
            return result

    # ── Direct app name ──
    for app_name in list(APPS.keys()) + list(BROWSER_APPS.keys()):
        if app_name in command and len(command.split()) <= 3:
            result = open_app(command)
            if result:
                return result

    # ── Web searches ──
    result = handle_search(command)
    if result:
        return result
    result = open_website(command)
    if result:
        return result

    # ── Task management ──
    result = handle_tasks(command)
    if result:
        return result

    # ── Notes ──
    result = handle_notes(command)
    if result:
        return result

    # ── System control ──
    result = handle_system_control(command)
    if result:
        return result

    # ── Math ──
    if contains_any(command, ["calculate", "what is", "what's", "how much",
                               "plus", "minus", "times", "divided", "multiply",
                               "add", "subtract", "solve", " x "]):
        result = handle_math(command)
        if result:
            return result

    # ── Motivation ──
    if contains_any(command, ["motivate", "motivation", "inspire", "lazy",
                               "feeling lazy", "push me", "encourage",
                               "i can't", "i feel bad", "feeling down"]):
        return random.choice(MOTIVATIONAL_QUOTES)

    # ── Jokes ──
    if contains_any(command, ["joke", "funny", "laugh", "humor"]):
        return random.choice(JOKES)

    # ── Status ──
    if contains_any(command, ["how are you", "how r u", "you good", "status",
                               "how do you do", "how you doing"]):
        return "All systems running perfectly. I'm always ready to help. What do you need?"

    # ── Thanks ──
    if contains_any(command, ["thank", "thanks", "thx", "appreciate"]):
        return random.choice(["Anytime! That's what I'm here for.",
                              "Always. Keep building!",
                              "You're welcome. Let's keep going.",
                              "Happy to help. What's next?"])

    # ── Goodbyes ──
    if contains_any(command, ["good morning", "good evening", "good night", "good afternoon"]):
        now = datetime.datetime.now()
        return f"Hey! It's {now.strftime('%I:%M %p')}. What are we working on?"

    # ── Learning ──
    if contains_any(command, ["teach me", "learn about", "explain", "tutorial",
                               "how to", "what is a", "how does", "learn "]):
        query = command
        for remove in ["teach me", "learn about", "learn", "explain",
                        "tutorial", "how to", "how does", "what is a", "about", "me"]:
            query = query.replace(remove, " ")
        query = " ".join(query.split()).strip()
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query + ' tutorial')}"
            webbrowser.open(url)
            return f"Let me find learning resources for {query}. Opening search now."
        return "What topic would you like to learn about?"

    if "tutorial" in command:
        query = command.replace("tutorial", "").strip()
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query + ' tutorial')}"
            webbrowser.open(url)
            return f"Searching for {query} tutorials."
        return "What tutorial are you looking for?"

    # ── Default: search Google for unknown questions ──
    question_words = ["who", "what", "where", "when", "why", "how", "is", "are",
                      "was", "were", "do", "does", "did", "can", "could", "will",
                      "would", "should", "tell me", "define", "meaning"]
    first_word = command.split()[0] if command.split() else ""
    if first_word in question_words or contains_any(command, ["tell me about", "tell me", "who is", "what is"]):
        query = command
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"I'm offline right now, so let me search that for you. Opening Google for: {query}"

    return (f"I heard: '{command}'. I'm not sure what to do with that offline. "
            "Try: open notepad, search python, add task, calculate 25 times 4, "
            "find internship, tell me a joke, or motivate me!")


# ── Intent Step Executor ─────────────────────────────

def _handle_intent_steps(steps: list, original_command: str) -> str:
    """Execute structured action steps returned by get_intent()."""
    responses = []

    for step in steps:
        action = step.get("action", "").lower().strip()
        value = str(step.get("value", "")).strip()

        if action == "open_app":
            r = open_app(value)
            responses.append(r or f"Tried to open {value}.")

        elif action in ("search_youtube", "play_music"):
            r = play_on_youtube(value)
            set_last_topic("music", value)
            responses.append(r)

        elif action == "search_google":
            url = f"https://www.google.com/search?q={urllib.parse.quote(value)}"
            webbrowser.open(url)
            responses.append(f"Searching Google for: {value}.")

        elif action == "open_website":
            r = open_website(value)
            responses.append(r or f"Tried to open {value}.")

        elif action == "set_volume":
            val = value.lower()
            if val == "up":
                volume_up(5); responses.append("Volume increased.")
            elif val == "down":
                volume_down(5); responses.append("Volume decreased.")
            elif val == "mute":
                volume_mute(); responses.append("Volume muted.")
            else:
                try:
                    lvl = int(val)
                    volume_down(50)
                    volume_up(max(0, lvl // 2))
                    responses.append(f"Volume set to approximately {lvl} percent.")
                except:
                    responses.append("Volume adjusted.")

        elif action == "set_brightness":
            val = value.lower()
            if val == "up":
                cur = get_brightness()
                new = min(100, (cur if cur >= 0 else 60) + 20)
                set_brightness(new); responses.append(f"Brightness increased to {new} percent.")
            elif val == "down":
                cur = get_brightness()
                new = max(10, (cur if cur >= 0 else 60) - 20)
                set_brightness(new); responses.append(f"Brightness decreased to {new} percent.")
            else:
                try:
                    lvl = int(val)
                    set_brightness(lvl)
                    responses.append(f"Brightness set to {lvl} percent.")
                except:
                    responses.append("Brightness adjusted.")

        elif action == "add_task":
            r = handle_tasks(f"add task {value}")
            responses.append(r or f"Task added: {value}.")

        elif action == "get_weather":
            try:
                import requests
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(value)}&count=1&language=en&format=json"
                geo_data = requests.get(geo_url).json()
                if "results" in geo_data and len(geo_data["results"]) > 0:
                    lat = geo_data["results"][0]["latitude"]
                    lon = geo_data["results"][0]["longitude"]
                    city_name = geo_data["results"][0]["name"]
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                    w_data = requests.get(weather_url).json()
                    current = w_data.get("current_weather", {})
                    temp = current.get("temperature", "unknown")
                    wind = current.get("windspeed", "unknown")
                    result = f"The current weather in {city_name} is {temp}°C with a wind speed of {wind} km/h."
                else:
                    result = f"I couldn't find the city '{value}' to get the weather."
            except Exception as e:
                result = f"There was an error fetching the weather: {e}"
            responses.append(result)

        elif action == "take_note":
            r = handle_notes(f"note down {value}")
            responses.append(r or f"Noted: {value}.")

        elif action == "write_code":
            r = handle_code_writing(f"write code for {value}")
            responses.append(r or f"Working on code for: {value}.")

        elif action == "call_person":
            r = handle_calling(f"call {value}")
            responses.append(r or f"Opening WhatsApp for {value}.")

        elif action == "send_message":
            r = handle_messaging(f"message {value} on whatsapp")
            responses.append(r or f"Opening WhatsApp to message {value}.")

        elif action == "find_internship":
            r = handle_internship(f"find internship {value}")
            responses.append(r or f"Searching internships for: {value}.")

        elif action == "find_file":
            r = find_file(value)
            responses.append(r)

        elif action == "chat":
            memory = get_memory()
            user_facts = get_user_profile()
            r = ollama_chat(value or original_command, memory, user_facts)
            responses.append(r)

        else:
            r = smart_offline_response(original_command)
            responses.append(r)
            break

    return " ".join(responses) if responses else smart_offline_response(original_command)


# ── Action Handler ───────────────────────────────────

def _try_actions(command: str) -> str:
    """Try to execute actionable commands (apps, websites, music, tasks, etc.).
    Returns response if an action was taken, None if no action matched."""
    cmd = normalize_command(command)

    # ── Follow-up Awareness ──
    # If the user says something vague, check if it relates to last topic
    last_topic, last_query = get_last_topic()
    if last_topic == "music" and len(cmd.split()) <= 4:
        music_followups = ["something", "more", "another", "different", "similar",
                           "energetic", "chill", "loud", "soft", "happy", "sad"]
        if any(w in cmd for w in music_followups):
            new_query = f"{last_query} {cmd}" if last_query else cmd
            result = play_on_youtube(new_query)
            if result:
                set_last_topic("music", new_query)
                return result

    # ── Remember / Memory ──
    if contains_any(cmd, ["remember that", "remember", "memorize that", "memorize", "note that"]):
        if cmd.strip().startswith("remember") or cmd.strip().startswith("memorize") or cmd.strip().startswith("note that"):
            result = handle_remember(cmd)
            if result:
                return result

    # ── Internship Finder ──
    if contains_any(cmd, ["internship", "intern"]):
        result = handle_internship(cmd)
        if result:
            return result

    # ── Find file on system ──
    if contains_any(cmd, ["find file", "locate file", "where is", "find my"]):
        query = cmd
        for remove in ["find file", "locate file", "where is", "find my", "find", "locate",
                        "the file", "file", "please", "for me"]:
            query = query.replace(remove, " ")
        query = " ".join(query.split()).strip()
        if query:
            return find_file(query)

    # ── Media Controls (HIGHEST PRIORITY) ──
    result = handle_media_control(cmd)
    if result:
        set_last_topic("music")
        return result

    # ── Messaging & Calling ──
    is_call_cmd = has_word(cmd, ["call", "dial", "phone"])
    is_msg_cmd = contains_any(cmd, ["send message", "message", "text ", "dm "]) or \
                 (has_word(cmd, ["find"]) and contains_any(cmd, ["whatsapp", "instagram"]))

    if is_call_cmd and not contains_any(cmd, ["call of", "call it", "call this"]):
        result = handle_calling(cmd)
        if result:
            return result

    if is_msg_cmd:
        result = handle_messaging(cmd)
        if result:
            return result

    # ── YouTube / Play ──
    if "youtube" in cmd or has_word(cmd, ["play"]):
        result = handle_search(cmd)
        if result:
            set_last_topic("music", cmd)
            return result

    # ── Open commands ──
    if contains_any(cmd, ["open", "launch", "start", "run"]):
        result = handle_search(cmd)
        if result:
            return result
        result = open_website(cmd)
        if result:
            return result
        app_query = cmd
        for remove in ["open", "launch", "start", "run"]:
            app_query = app_query.replace(remove, " ")
        app_query = app_query.strip()
        result = open_app(app_query)
        if result:
            return result

    # ── Direct app name ──
    for app_name in list(APPS.keys()) + list(BROWSER_APPS.keys()):
        if app_name in cmd and len(cmd.split()) <= 3:
            result = open_app(cmd)
            if result:
                return result

    # ── Web searches ──
    if contains_any(cmd, ["search", "google", "look up", "find", "wikipedia", "wiki"]):
        result = handle_search(cmd)
        if result:
            return result

    # ── Website opening ──
    result = open_website(cmd)
    if result:
        return result

    # ── Task management ──
    result = handle_tasks(cmd)
    if result:
        return result

    # ── Notes ──
    result = handle_notes(cmd)
    if result:
        return result

    # ── System control ──
    result = handle_system_control(cmd)
    if result:
        return result

    # ── Code writing ──
    _code_actions = {"write", "create", "make", "generate", "build", "code"}
    _code_nouns = {"code", "program", "script"}
    cmd_words = set(cmd.split())
    has_code_action = bool(cmd_words & _code_actions)
    has_code_noun = bool(cmd_words & _code_nouns)
    has_exact = contains_any(cmd, ["write code", "create code", "code for", "generate code",
                                    "make code", "write program", "create program",
                                    "write script", "create script"])
    is_code_request = (has_exact or (has_code_action and has_code_noun)) \
                       and not (cmd.strip() in ["vs code", "open vs code", "open code", "launch code"])
    if is_code_request:
        result = handle_code_writing(cmd)
        if result:
            return result

    # ── Math ──
    if contains_any(cmd, ["calculate", "what is", "what's", "how much",
                           "plus", "minus", "times", "divided", "multiply",
                           "add", "subtract", "solve", " x "]):
        result = handle_math(cmd)
        if result:
            return result

    # No actionable command matched
    return None


# ── Main Router ──────────────────────────────────────

def get_response(command: str, emotion: str = "calm") -> str:
    """Try actions first (they actually DO things), then use AI for conversation.
    AI Priority: Ollama (local) → Gemini → OpenRouter → Offline Brain.

    Args:
        command: The user's command/question.
        emotion: Detected emotion from NLP (used in AI system prompt).
    """
    # Build emotion context for AI
    emotion_context = ""
    if emotion and emotion != "calm":
        emotion_map = {
            "happy": "happy and excited",
            "sad": "sad or down — be extra supportive and encouraging",
            "angry": "frustrated — be calm, patient, and helpful",
            "excited": "excited and energetic — match their enthusiasm",
            "fearful": "anxious or worried — be reassuring",
        }
        emotion_context = emotion_map.get(emotion, emotion)

    # ── STEP 1: Always try actionable commands first ──
    action_result = _try_actions(command)
    if action_result:
        # Store in memory
        add_exchange(command, action_result)
        # Auto-summarize if needed
        auto_summarize(get_memory(), get_exchange_count())
        return action_result

    # ── STEP 2: No action matched → use AI for conversation/questions ──
    memory = get_memory()
    user_facts = get_user_profile()
    long_term_context = get_context_for_ai()
    combined_facts = user_facts
    if long_term_context:
        combined_facts = f"{user_facts}\n\n{long_term_context}" if user_facts else long_term_context

    # ── Priority 1: Ollama (fully local) ──
    if AI_PROVIDER == "ollama":
        try:
            # Try intent detection first
            steps = get_intent(command)
            if steps:
                if len(steps) == 1 and steps[0].get("action") == "chat":
                    reply = ollama_chat(command, memory, combined_facts, emotion_context)
                else:
                    reply = _handle_intent_steps(steps, command)
            else:
                reply = ollama_chat(command, memory, combined_facts, emotion_context)

            add_exchange(command, reply)
            auto_summarize(get_memory(), get_exchange_count())
            return reply
        except Exception as e:
            err = str(e)
            if any(k in err.lower() for k in ["connectionerror", "connection refused",
                                               "connect", "timeout", "refused"]):
                print("   ⚠️  Ollama not running — falling back to cloud AI...")
            else:
                print(f"   ⚠️  Ollama error: {err[:80]}")

    # ── Priority 2: Google Gemini ──
    if gemini_available() and not gemini_on_cooldown():
        reply = gemini_response(command, memory, save_memory,
                                combined_facts, emotion_context, smart_offline_response)
        auto_summarize(get_memory(), get_exchange_count())
        return reply

    # ── Priority 3: OpenRouter ──
    if openrouter_available():
        if gemini_on_cooldown():
            print("   🔄 Using OpenRouter AI (Gemini on cooldown)...")
        reply = openrouter_response(command, memory, save_memory,
                                    combined_facts, emotion_context, smart_offline_response)
        auto_summarize(get_memory(), get_exchange_count())
        return reply

    # ── Priority 4: Smart offline brain ──
    reply = smart_offline_response(command)
    add_exchange(command, reply)
    return reply
