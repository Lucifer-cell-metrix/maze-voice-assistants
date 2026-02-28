"""
MAZE — AI Brain Module (v3 — Smarter Offline + Gemini)
Works 100% offline with flexible command matching.
Upgrades to Gemini AI automatically when API is available.
"""

import sys, os, time, datetime, webbrowser, subprocess, urllib.parse, json, random, re, ctypes
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import AI_PROVIDER, GEMINI_API_KEY, MAX_MEMORY_TURNS

# Conversation memory
_memory = []
_gemini_failed_count = 0
_tasks = []

# ── Task file for persistence ────────────────────────
TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "tasks.json")

def _load_tasks():
    global _tasks
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                _tasks = json.load(f)
    except:
        _tasks = []

def _save_tasks():
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(_tasks, f, indent=2)
    except:
        pass

_load_tasks()

# ── Helpers ──────────────────────────────────────────

def _contains_any(command: str, words: list) -> bool:
    """Check if command contains any of the words/phrases."""
    return any(w in command for w in words)

def _has_word(command: str, words: list) -> bool:
    """Check if command contains any word as a whole word (not substring).
    Use this for short words like 'hi', 'hey', 'yo' that could match inside other words."""
    cmd_words = command.split()
    return any(w in cmd_words for w in words)

def _normalize_command(command: str) -> str:
    """Normalize common speech variations."""
    command = command.lower().strip()
    # Fix common speech-to-text issues
    command = command.replace("you tube", "youtube")
    command = command.replace("you too", "youtube")
    command = command.replace("u tube", "youtube")
    command = command.replace("v s code", "vs code")
    command = command.replace("vs court", "vs code")
    command = command.replace("note pad", "notepad")
    command = command.replace("calculater", "calculator")
    return command

def _extract_after(command: str, keywords: list) -> str:
    """Extract text after any of the given keywords."""
    for kw in keywords:
        if kw in command:
            return command.split(kw, 1)[1].strip()
    return ""

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

# ── Application Launcher ─────────────────────────────

APPS = {
    "notepad":         "notepad.exe",
    "calculator":      "calc.exe",
    "open calculator": "calc.exe",
    "open calc":       "calc.exe",
    "paint":           "mspaint.exe",
    "explorer":        "explorer.exe",
    "file explorer":   "explorer.exe",
    "files":           "explorer.exe",
    "task manager":    "taskmgr.exe",
    "cmd":             "cmd.exe",
    "command prompt":  "cmd.exe",
    "terminal":        "cmd.exe",
    "powershell":      "powershell.exe",
    "settings":        "ms-settings:",
    "vs code":         "code",
    "vscode":          "code",
    "visual studio":   "code",
    "snipping tool":   "snippingtool.exe",
    "screenshot":      "snippingtool.exe",
    "snip":            "snippingtool.exe",
    "word":            "winword.exe",
    "excel":           "excel.exe",
    "powerpoint":      "powerpnt.exe",
    "outlook":         "outlook.exe",
    "photos":          "ms-photos:",
    "camera":          "microsoft.windows.camera:",
    "clock":           "ms-clock:",
    "calendar":        "outlookcal:",
    "maps":            "bingmaps:",
    "store":           "ms-windows-store:",
    "xbox":            "xbox:",
}

# Browser paths to try on Windows
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]

BRAVE_PATHS = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
]

BROWSER_APPS = {
    "chrome":        CHROME_PATHS,
    "google chrome": CHROME_PATHS,
    "brave":         BRAVE_PATHS,
    "edge":          ["msedge.exe"],
    "microsoft edge":["msedge.exe"],
    "firefox":       ["firefox.exe"],
    "browser":       CHROME_PATHS,  # Default to Chrome
}

def _open_app(app_name: str) -> str:
    """Open a system application by name."""
    app_name = app_name.lower().strip()

    # Check if it's a browser request
    for browser_name, paths in BROWSER_APPS.items():
        if browser_name in app_name:
            for path in paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return f"Opening {browser_name.title()} for you."
            # Try with shell=True as fallback
            try:
                subprocess.Popen(paths[-1], shell=True)
                return f"Opening {browser_name.title()} for you."
            except:
                pass
            # Final fallback — default browser
            webbrowser.open("https://www.google.com")
            return f"{browser_name.title()} not found. Opening default browser."

    # Check regular apps — use whole word matching to avoid 'calc' in 'calculate'
    for key, exe in APPS.items():
        # For short words like 'calc', check as whole word
        if len(key) <= 4:
            if _has_word(app_name, [key]):
                try:
                    if "ms-" in exe:
                        os.startfile(exe)
                    else:
                        subprocess.Popen(exe, shell=True)
                    return f"Opening {key.title()} for you."
                except Exception as e:
                    return f"Couldn't open {key.title()}. Error: {str(e)}"
        else:
            if key in app_name:
                try:
                    if "ms-" in exe:
                        os.startfile(exe)
                    else:
                        subprocess.Popen(exe, shell=True)
                    return f"Opening {key.title()} for you."
                except Exception as e:
                    return f"Couldn't open {key.title()}. Error: {str(e)}"

    return None

# ── Website Opener ───────────────────────────────────

WEBSITES = {
    # Developer
    "github":          "https://github.com",
    "stackoverflow":   "https://stackoverflow.com",
    "stack overflow":   "https://stackoverflow.com",
    # Email & Communication
    "gmail":           "https://mail.google.com",
    "email":           "https://mail.google.com",
    "mail":            "https://mail.google.com",
    "whatsapp":        "https://web.whatsapp.com",
    "telegram":        "https://web.telegram.org",
    "discord":         "https://discord.com/app",
    # Social Media
    "instagram":       "https://instagram.com",
    "twitter":         "https://twitter.com",
    "linkedin":        "https://linkedin.com",
    "facebook":        "https://facebook.com",
    "reddit":          "https://reddit.com",
    "pinterest":       "https://pinterest.com",
    "snapchat":        "https://web.snapchat.com",
    "threads":         "https://threads.net",
    # AI Tools
    "chatgpt":         "https://chat.openai.com",
    "gemini":          "https://gemini.google.com",
    "claude":          "https://claude.ai",
    # Entertainment
    "spotify":         "https://open.spotify.com",
    "netflix":         "https://netflix.com",
    "hotstar":         "https://hotstar.com",
    "prime video":     "https://primevideo.com",
    "amazon prime":    "https://primevideo.com",
    # Shopping
    "amazon":          "https://amazon.in",
    "flipkart":        "https://flipkart.com",
    "myntra":          "https://myntra.com",
    # Productivity
    "google drive":    "https://drive.google.com",
    "google docs":     "https://docs.google.com",
    "notion":          "https://notion.so",
    "canva":           "https://canva.com",
    "figma":           "https://figma.com",
    # Learning
    "udemy":           "https://udemy.com",
    "coursera":        "https://coursera.org",
    "geeksforgeeks":   "https://geeksforgeeks.org",
    "leetcode":        "https://leetcode.com",
    "w3schools":       "https://w3schools.com",
}

def _open_website(command: str) -> str:
    """Open a known website."""
    for key, url in WEBSITES.items():
        if key in command:
            webbrowser.open(url)
            return f"Opening {key.title()} for you."
    return None

# ── Search Handler (YouTube priority over Google) ────

# Words to remove from query (as WHOLE WORDS only, not substrings)
YT_REMOVE_WORDS = {"open", "youtube", "search", "play", "on", "and", "in",
                    "find", "for", "video", "the", "a", "me", "show",
                    "you", "tube", "please", "song", "music"}

def _extract_query(command: str, remove_words: set) -> str:
    """Remove keywords as WHOLE WORDS (not substrings) from command."""
    words = command.split()
    filtered = [w for w in words if w not in remove_words]
    return " ".join(filtered).strip()

def _play_on_youtube(query: str) -> str:
    """Find the first YouTube video for query and play it directly."""
    try:
        import requests as req
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = req.get(search_url, headers=headers, timeout=5)
        # Find the first video ID
        video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', response.text)
        if video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            webbrowser.open(video_url)
            return f"Playing {query} on YouTube."
    except:
        pass
    # Fallback: open search results
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Searching {query} on YouTube."

def _handle_search(command: str) -> str:
    """Handle search commands. YouTube gets priority when mentioned."""

    # ── YouTube (if "youtube" is in command) ──
    if "youtube" in command:
        query = _extract_query(command, YT_REMOVE_WORDS)
        # If user said "search" → show results only. If "play" → auto-play.
        if query:
            if _has_word(command, ["play"]):
                return _play_on_youtube(query)
            else:
                # Just show search results (don't auto-play)
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                webbrowser.open(url)
                return f"Searching {query} on YouTube."
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."

    # ── "Play X" = Auto-play on YouTube (even without saying youtube) ──
    if command.startswith("play ") or " play " in command:
        query = _extract_query(command, YT_REMOVE_WORDS | {"play"})
        if query:
            return _play_on_youtube(query)
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube. What do you want to play?"

    # ── Wikipedia search ──
    if _contains_any(command, ["wikipedia", "wiki"]):
        wiki_remove = {"wikipedia", "wiki", "search", "open", "on", "about", "for", "the"}
        query = _extract_query(command, wiki_remove)
        if query:
            url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Opening Wikipedia for: {query}"
        return "What should I look up on Wikipedia?"

    # ── Google search (default) ──
    if _contains_any(command, ["search", "google", "look up", "find"]):
        google_remove = {"search", "google", "look", "up", "find", "for", "about", "open", "the"}
        query = _extract_query(command, google_remove)
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching Google for: {query}"
        return "What would you like me to search for?"

    return None

# ── Task Manager ─────────────────────────────────────

def _handle_tasks(command: str) -> str:
    """Handle task management commands."""
    global _tasks

    # Add task
    if _contains_any(command, ["add task", "new task", "create task"]):
        task = _extract_after(command, ["add task", "new task", "create task"])
        if task:
            _tasks.append({"task": task, "done": False, "time": datetime.datetime.now().isoformat()})
            _save_tasks()
            return f"Task added: {task}. You now have {len([t for t in _tasks if not t['done']])} pending tasks."
        return "What task do you want to add? Say 'add task' followed by the task name."

    # Show tasks (flexible matching — singular/plural, various phrasings)
    if (_contains_any(command, ["show task", "my task", "list task", "task list", "all task",
                                "show tasks", "my tasks", "list tasks", "pending task",
                                "what are my task", "tasks", "show me task", "show me tasks",
                                "view task", "view tasks"])
        or ("show" in command and "task" in command)
        or ("task" in command and _has_word(command, ["show", "list", "view", "see", "all", "my", "pending"]))):
        if not _tasks:
            return "You have no tasks yet. Say 'add task' followed by the task name to add one."
        pending = [t for t in _tasks if not t["done"]]
        done = [t for t in _tasks if t["done"]]
        if not pending:
            return f"All tasks completed! You've finished {len(done)} tasks. Great work!"
        result = f"You have {len(pending)} pending tasks. "
        for i, t in enumerate(pending, 1):
            result += f"Task {i}: {t['task']}. "
        if done:
            result += f"And {len(done)} completed."
        return result

    # Complete task
    if _contains_any(command, ["complete task", "done task", "finish task", "mark task"]):
        try:
            num = int(''.join(filter(str.isdigit, command))) - 1
            pending = [t for t in _tasks if not t["done"]]
            if 0 <= num < len(pending):
                pending[num]["done"] = True
                _save_tasks()
                return f"Nice! Task '{pending[num]['task']}' is done. Keep going!"
        except:
            pass
        return "Which task? Say 'complete task 1', 'complete task 2', etc."

    # Clear tasks
    if _contains_any(command, ["clear task", "delete task", "remove task",
                                "clear all task", "delete all task"]):
        _tasks.clear()
        _save_tasks()
        return "All tasks cleared. Fresh start."

    return None

# ── Note-Taking / Type Message ───────────────────────

NOTES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "notes.txt")

def _handle_notes(command: str) -> str:
    """Handle note-taking and message typing."""

    # Note down / Write / Type message
    if _contains_any(command, ["note down", "note this", "write down", "write this",
                                "type message", "type this", "take note", "make note",
                                "remember this", "remember that", "save note",
                                "jot down", "write note"]):
        # Extract the note content
        note = command
        for remove in ["note down", "note this", "write down", "write this",
                        "type message", "type this", "take note", "make note",
                        "remember this", "remember that", "save note",
                        "jot down", "write note", "please", "that"]:
            note = note.replace(remove, " ")
        note = " ".join(note.split()).strip()

        if note:
            # Save to file
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            try:
                with open(NOTES_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {note}\n")
            except:
                pass

            # Open in Notepad
            try:
                subprocess.Popen(["notepad.exe", NOTES_FILE])
            except:
                pass

            return f"Got it. Noted down: {note}. Opening in Notepad."
        return "What do you want me to note down? Say 'note down' followed by your message."

    # Show notes
    if _contains_any(command, ["show note", "show notes", "my notes", "read notes",
                                "read note", "show my notes", "view notes"]):
        try:
            if os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                if lines:
                    # Open in Notepad
                    subprocess.Popen(["notepad.exe", NOTES_FILE])
                    count = len(lines)
                    last_note = lines[-1].strip()
                    return f"You have {count} notes. Latest: {last_note}. Opening in Notepad."
                return "No notes yet. Say 'note down' followed by your message to start."
            return "No notes yet. Say 'note down' followed by your message to start."
        except:
            return "Couldn't read notes file."

    # Clear notes
    if _contains_any(command, ["clear notes", "delete notes", "remove notes",
                                "clear all notes", "erase notes"]):
        try:
            if os.path.exists(NOTES_FILE):
                os.remove(NOTES_FILE)
            return "All notes cleared."
        except:
            return "Couldn't clear notes."

    return None

# ── System Control (Volume & Brightness) ─────────────

def _press_key(vk_code):
    """Simulate a key press using Windows API."""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)       # key down
    ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)  # key up

VK_VOLUME_UP   = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

def _volume_up(steps=5):
    for _ in range(steps):
        _press_key(VK_VOLUME_UP)
        time.sleep(0.05)

def _volume_down(steps=5):
    for _ in range(steps):
        _press_key(VK_VOLUME_DOWN)
        time.sleep(0.05)

def _volume_mute():
    _press_key(VK_VOLUME_MUTE)

def _get_brightness():
    """Get current screen brightness (0-100)."""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            capture_output=True, text=True, timeout=5
        )
        return int(result.stdout.strip())
    except:
        return -1

def _set_brightness(level):
    """Set screen brightness (0-100)."""
    level = max(0, min(100, level))
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"],
            capture_output=True, text=True, timeout=5
        )
        return level
    except:
        return -1

def _handle_system_control(command: str) -> str:
    """Handle volume and brightness control."""

    # ── Volume Controls ──
    if _contains_any(command, ["volume up", "increase volume", "louder",
                                "turn up volume", "raise volume", "sound up",
                                "volume increase", "volume high", "volume higher"]):
        _volume_up(5)
        return "Volume increased."

    if _contains_any(command, ["volume down", "decrease volume", "quieter", "softer",
                                "turn down volume", "lower volume", "sound down",
                                "volume decrease", "volume low", "volume lower"]):
        _volume_down(5)
        return "Volume decreased."

    if _contains_any(command, ["mute", "unmute", "silence", "toggle mute",
                                "mute volume", "volume mute", "shut up volume"]):
        _volume_mute()
        return "Volume muted. Say mute again to unmute."

    if _contains_any(command, ["full volume", "max volume", "maximum volume",
                                "volume max", "volume full", "volume 100"]):
        _volume_up(50)  # Press up many times to reach max
        return "Volume set to maximum."

    if _contains_any(command, ["minimum volume", "volume minimum", "volume zero",
                                "volume 0", "no volume", "silent"]):
        _volume_down(50)  # Press down many times to reach min
        return "Volume set to minimum."

    # ── Brightness Controls ──
    if _contains_any(command, ["brightness up", "increase brightness", "brighter",
                                "screen brighter", "turn up brightness",
                                "brightness increase", "brightness high", "brightness higher",
                                "more brightness", "bright up"]):
        current = _get_brightness()
        if current >= 0:
            new = min(100, current + 20)
            _set_brightness(new)
            return f"Brightness increased to {new} percent."
        return "Brightness increased."

    if _contains_any(command, ["brightness down", "decrease brightness", "dimmer",
                                "screen dimmer", "turn down brightness", "dim",
                                "brightness decrease", "brightness low", "brightness lower",
                                "less brightness", "bright down"]):
        current = _get_brightness()
        if current >= 0:
            new = max(0, current - 20)
            _set_brightness(new)
            return f"Brightness decreased to {new} percent."
        return "Brightness decreased."

    if _contains_any(command, ["full brightness", "max brightness", "maximum brightness",
                                "brightness max", "brightness full", "brightness 100"]):
        _set_brightness(100)
        return "Brightness set to maximum."

    if _contains_any(command, ["minimum brightness", "lowest brightness",
                                "brightness minimum", "brightness zero", "brightness 0"]):
        _set_brightness(10)  # Don't go to 0, screen would be invisible
        return "Brightness set to minimum."

    # Check for specific percentage: "set brightness to 50"
    if "brightness" in command:
        try:
            nums = re.findall(r'\d+', command)
            if nums:
                level = int(nums[0])
                if 0 <= level <= 100:
                    _set_brightness(level)
                    return f"Brightness set to {level} percent."
        except:
            pass

    # Check for specific volume percentage: "set volume to 50"
    if "volume" in command:
        try:
            nums = re.findall(r'\d+', command)
            if nums:
                level = int(nums[0])
                if 0 <= level <= 100:
                    # First mute/lower to 0, then raise to target
                    _volume_down(50)
                    steps = level // 2  # Each step is ~2%
                    _volume_up(steps)
                    return f"Volume set to approximately {level} percent."
        except:
            pass

    return None

# ── Math Calculator ──────────────────────────────────

def _handle_math(command: str) -> str:
    """Handle calculations."""
    # Clean the command
    expr = command
    for remove in ["calculate", "what is", "what's", "how much is", "solve", "equals"]:
        expr = expr.replace(remove, " ")

    # Replace math words with operators
    math_words = {
        " plus ": "+", " add ": "+", " added to ": "+",
        " minus ": "-", " subtract ": "-", " subtracted from ": "-",
        " times ": "*", " multiply ": "*", " multiplied by ": "*", " into ": "*",
        " x ": "*", " × ": "*", " X ": "*",
        " divided by ": "/", " divide ": "/", " over ": "/",
        " power ": "**", " to the power of ": "**", " square ": "**2",
        " mod ": "%", " modulo ": "%", " remainder ": "%",
    }
    for word, op in math_words.items():
        expr = expr.replace(word, op)

    # Also handle cases like "25x4" or "25*4"
    expr = expr.replace("x", "*").replace("×", "*").replace("X", "*")

    # Keep only math characters
    expr = ''.join(c for c in expr if c in '0123456789.+-*/() %')
    expr = expr.strip()

    if expr and any(c.isdigit() for c in expr):
        try:
            result = eval(expr)
            # Format nicely
            if isinstance(result, float) and result == int(result):
                result = int(result)
            return f"The answer is {result}."
        except:
            return "I couldn't calculate that. Try saying it like 'calculate 25 times 4'."
    return None

# ── Smart Offline Brain ──────────────────────────────

def smart_offline_response(command: str) -> str:
    """Smart offline brain — handles real tasks with flexible matching."""
    command = _normalize_command(command)

    # ── Greetings (use _has_word to avoid matching 'yo' inside 'youtube' etc.) ──
    if (_has_word(command, ["hello", "hi", "hey", "heyy", "howdy", "yo", "hola", "namaste"])
        or _contains_any(command, ["what's up", "whats up"])
        ) and not _contains_any(command, ["open", "search", "youtube", "google", "task",
                                           "calculate", "notepad", "chrome", "show"]):
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good morning! MAZE is ready. What's your mission today?"
        elif hour < 17:
            return "Good afternoon! What can I help you with?"
        elif hour < 21:
            return "Good evening! Ready to get productive?"
        return "Good night! What are we working on?"

    # ── Identity ────────────────────────────
    if _contains_any(command, ["who are you", "who r u", "hu r u", "your name",
                                "what are you", "what r u", "what is your name",
                                "tell me about yourself", "introduce yourself"]):
        return ("I am MAZE, your personal AI assistant. Built to help you learn, "
                "build, and grow. I can open apps, search the web, manage tasks, "
                "do math, motivate you, and much more. All for free!")

    if _contains_any(command, ["what can you do", "your capabilities", "help me",
                                "what do you do", "features"]) or command.strip() == "help":
        return ("I can open apps like Notepad, Chrome, Brave, VS Code, and Paint. "
                "I play songs on YouTube, search Google and Wikipedia. "
                "I manage tasks and notes. I open WhatsApp, Instagram, GitHub. "
                "I control volume and brightness. "
                "I do math, tell time, motivate you, and tell jokes. Just ask!")

    # ── Time & Date (check ONLY if not a task/app command) ──
    if (_contains_any(command, ["what time", "the time", "current time", "clock"])
        or (command.strip() == "time")
        or (_has_word(command, ["time"]) and not _contains_any(command, ["task", "open", "youtube", "times"]))):
        now = datetime.datetime.now()
        return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

    if (_contains_any(command, ["what day", "today's date", "which day"])
        or (command.strip() in ["date", "today"])):
        return datetime.datetime.now().strftime("Today is %A, %B %d, %Y.")

    # ── YouTube / Play (HIGHEST PRIORITY) ───
    if "youtube" in command or _has_word(command, ["play"]):
        result = _handle_search(command)
        if result:
            return result

    # ── Open commands ───────────────────────
    if _contains_any(command, ["open", "launch", "start", "run"]):
        # Check for web searches first
        result = _handle_search(command)
        if result:
            return result
        # Then websites
        result = _open_website(command)
        if result:
            return result
        # Then apps
        app_query = command
        for remove in ["open", "launch", "start", "run"]:
            app_query = app_query.replace(remove, " ")
        app_query = app_query.strip()
        result = _open_app(app_query)
        if result:
            return result

    # ── Direct app name (without "open") ────
    for app_name in list(APPS.keys()) + list(BROWSER_APPS.keys()):
        if app_name in command and len(command.split()) <= 3:
            result = _open_app(command)
            if result:
                return result

    # ── Web searches ────────────────────────
    result = _handle_search(command)
    if result:
        return result

    # ── Website opening ─────────────────────
    result = _open_website(command)
    if result:
        return result

    # ── Task management ─────────────────────
    result = _handle_tasks(command)
    if result:
        return result

    # ── Note-taking / Type message ───────────
    result = _handle_notes(command)
    if result:
        return result

    # ── System control (volume/brightness) ───
    result = _handle_system_control(command)
    if result:
        return result

    # ── Math ────────────────────────────────
    if _contains_any(command, ["calculate", "what is", "what's", "how much",
                                "plus", "minus", "times", "divided", "multiply",
                                "add", "subtract", "solve", " x "]):
        result = _handle_math(command)
        if result:
            return result

    # ── Motivation ──────────────────────────
    if _contains_any(command, ["motivate", "motivation", "inspire", "lazy",
                                "feeling lazy", "push me", "encourage",
                                "i can't", "i feel bad", "feeling down"]):
        return random.choice(MOTIVATIONAL_QUOTES)

    # ── Jokes ───────────────────────────────
    if _contains_any(command, ["joke", "funny", "laugh", "humor"]):
        return random.choice(JOKES)

    # ── Status ──────────────────────────────
    if _contains_any(command, ["how are you", "how r u", "you good", "status",
                                "how do you do", "how you doing"]):
        return "All systems running perfectly. I'm always ready to help. What do you need?"

    # ── Thanks ──────────────────────────────
    if _contains_any(command, ["thank", "thanks", "thx", "appreciate"]):
        return random.choice(["Anytime! That's what I'm here for.",
                              "Always. Keep building!",
                              "You're welcome. Let's keep going.",
                              "Happy to help. What's next?"])

    # ── Goodbyes (not exit) ─────────────────
    if _contains_any(command, ["good morning", "good evening", "good night", "good afternoon"]):
        now = datetime.datetime.now()
        return f"Hey! It's {now.strftime('%I:%M %p')}. What are we working on?"

    # ── Learning requests ───────────────────
    if _contains_any(command, ["teach me", "learn about", "explain", "tutorial",
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

    # ── Direct topic + 'tutorial' (e.g. 'python tutorial') ──
    if "tutorial" in command:
        query = command.replace("tutorial", "").strip()
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query + ' tutorial')}"
            webbrowser.open(url)
            return f"Searching for {query} tutorials."
        return "What tutorial are you looking for?"

    # ── Default ─────────────────────────────
    return (f"I heard: '{command}'. I'm not sure what to do with that. "
            "Try commands like: open notepad, search python, add task, "
            "calculate 25 times 4, tell me a joke, or motivate me!")


# ── Gemini Response Engine ────────────────────────────
MODELS_TO_TRY = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def _gemini_response(command: str) -> str:
    global _gemini_failed_count
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        _memory.append({"role": "user", "parts": [{"text": command}]})

        system_instruction = (
            "You are MAZE, an advanced AI assistant inspired by JARVIS from Iron Man. "
            "Intelligent, calm, professional, friendly, and motivating. "
            "Keep responses BRIEF for voice. No markdown or formatting. "
            "Max 2-3 sentences unless asked for detail."
        )

        last_error = None
        for model_name in MODELS_TO_TRY:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=_memory[-MAX_MEMORY_TURNS:],
                    config={
                        "system_instruction": system_instruction,
                        "max_output_tokens": 200,
                        "temperature": 0.7,
                    }
                )
                reply = response.text.strip()
                _memory.append({"role": "model", "parts": [{"text": reply}]})
                _gemini_failed_count = 0
                return reply
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    continue
                else:
                    break

        _gemini_failed_count += 1
        _memory.pop()
        return smart_offline_response(command)

    except Exception:
        _gemini_failed_count += 1
        return smart_offline_response(command)


# ── Main Router ───────────────────────────────────────
def get_response(command: str) -> str:
    """Route to Gemini if available, otherwise smart offline."""
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY and _gemini_failed_count < 3:
        return _gemini_response(command)
    else:
        return smart_offline_response(command)
