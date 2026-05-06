# 🧠 MAZE: The Complete Guide

Welcome to **MAZE**, your hybrid AI desktop assistant! MAZE is built to be fast, privacy-focused, and highly capable. It doesn't just talk to you—it interacts with your computer natively.

This document explains exactly how MAZE works under the hood and how you can get the most out of it.

---

## 🏗️ How MAZE Works (The Architecture)

MAZE operates on a **Modular Action-Oriented Architecture** combined with a **Hybrid AI Engine**. Here is the step-by-step breakdown of how a command is processed:

### 1. Input Processing
You can talk to MAZE using your microphone, type to it using your keyboard, or message it remotely via Telegram. 
- The **Voice Engine** uses `speech_recognition` to listen and converts your speech to text. 
- The **NLP Engine** (spaCy) analyzes the sentiment of your command to detect if you are happy, frustrated, or sad, allowing MAZE to reply with the appropriate emotional tone.

### 2. The Brain Router (`brain.py`)
Once MAZE has your text command, it gets sent to the central router. The router follows a strict hierarchy:
1. **Keyword Actions:** It first checks if your command matches any fast, local keywords (e.g., "open Chrome", "volume up"). This ensures zero-latency execution for basic tasks.
2. **AI Function Calling:** If it's a complex command (e.g., "Search the web for the latest AI news" or "Send a WhatsApp message to John saying I'll be late"), it gets sent to the AI Provider.

### 3. Native AI Tool Calling
MAZE no longer relies on guessing what you want. It uses **Native Function Calling**.
- We pass a strict JSON schema (`tools_schema.py`) to Google Gemini (or Ollama).
- The AI reads your command and natively executes a programmatic "Tool Call".
- **Example:** You say *"Play interstellar theme on youtube"*. The AI securely executes `search_youtube(query="interstellar theme")` instead of generating a conversational text reply.

### 4. Hybrid AI Providers
MAZE tries to process things locally to protect your privacy and save API costs.
- **Priority 1 (Ollama):** If you have Ollama running, MAZE uses it as the primary brain.
- **Priority 2 (Gemini):** If a local model fails or you need complex reasoning, it falls back to Google Gemini's lightning-fast Flash models.
- **Priority 3 (Offline):** If your internet drops entirely, MAZE falls back to a hardcoded smart-offline brain.

### 5. Smart Memory System
MAZE doesn't suffer from "Goldfish memory". 
- **Short-Term Context:** It remembers the current topic. If you say *"play lo-fi hip hop"* and then later say *"next track"*, it knows you are talking about the music module.
- **Long-Term Summaries:** Every 20 exchanges, MAZE runs a background AI summarization task. It condenses the entire conversation into a short paragraph and saves it to `memory/long_term.json`. This gives MAZE persistent context across system reboots without overloading the AI token limit!

---

## 🛠️ How To Use MAZE (Command Guide)

MAZE supports hundreds of natural language commands. Here are the primary ways you can use it:

### 📂 App & File Management
MAZE indexes your `C:/` and `D:/` drives automatically.
- *"Open VS Code"*
- *"Launch Google Chrome"*
- *"Find the file budget_report.pdf"*
- *"Open Spotify"*

### 🌐 Web & Search
MAZE can fetch live data and open websites natively.
- *"Search Google for Python tutorials"*
- *"What is the latest news in cybersecurity?"*
- *"Who is Elon Musk?"*
- *"Read http://example.com/article"* (MAZE will fetch, strip HTML, and summarize the page for you)
- *"Open GitHub"*

### 🎵 Media Controls
- *"Play some relaxing jazz"* (Autoplays on YouTube)
- *"Next track"*
- *"Pause music"*
- *"Volume up" / "Mute"* / *"Set volume to 50"*

### 💬 Messaging & Communication
MAZE can open social platforms and pre-fill messages for you.
- *"Message Lucifer on WhatsApp saying I will call him later"*
- *"Call Mom on WhatsApp"*
- *"Message Kyan on Instagram"*
- *"Open Telegram"*

### 💼 Internship Finder
MAZE has a built-in web scraper for Internshala.
- *"Find remote Python internships"*
- *"Search internships for cybersecurity"*
*(Note: You can also use the `/internship python remote` command directly from your Telegram bot to get clickable links!)*

### 📝 Notes & Tasks
- *"Add a task to finish the AI project"*
- *"What are my tasks?"*
- *"Take a note that my wifi password is '12345'"*
- *"Read my notes"*

### ⌨️ Changing Modes
If you are in an environment where you cannot speak:
- Just say or type: **"Switch"**
- MAZE will instantly toggle between Voice Input and Keyboard Input modes.

---

## 📱 Telegram Remote Control

You don't even need to be at your computer to use MAZE!
1. Start your Telegram Bot (configured via `.env`).
2. Message your bot from your phone.
3. If you say *"Open Notepad"*, the bot will send the signal to your PC, and Notepad will open on your desktop in real-time.
4. You can also run the internship scraper remotely by typing `/internship [keyword]`.

---

## ⚙️ Advanced Customization

- **Changing Voices:** Modify `_create_engine()` in `main.py` to select different system voices if Microsoft Aria (edge-tts) is unavailable.
- **Adding Contacts:** Open `config.py` and update the `CONTACTS` and `INSTAGRAM_USERS` dictionaries to map your friends' names to their phone numbers or usernames.
- **Disabling Auto-start:** Run `python setup_autostart.py --disable` if you no longer want MAZE to boot with Windows.
