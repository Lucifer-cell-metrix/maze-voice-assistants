<p align="center">
  <img src="https://img.shields.io/badge/MAZE-AI%20Assistant-blueviolet?style=for-the-badge&logo=robot&logoColor=white" alt="MAZE Badge"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/AI-Gemini%20Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Fallback-OpenRouter-FF6600?style=for-the-badge&logo=openai&logoColor=white" alt="OpenRouter"/>
</p>

<h1 align="center">🧠 MAZE — Your Advanced AI Desktop Assistant</h1>

<p align="center">
  <b>A powerful, voice-controlled AI assistant for Windows — inspired by JARVIS.</b><br/>
  Featuring <b>Offline Speech Recognition</b>, <b>Telegram Remote Control</b>, <b>Smart Code Generation</b>, and <b>YouTube Music Queue</b>.
</p>

---

## ✨ What's New (Latest Updates)

- **🎵 YouTube Music Queue** — When you say *"Play Arijit Singh songs"*, MAZE builds a queue of 20 tracks from YouTube. Say *"Next"* to skip to the next song, *"Previous"* to go back — no more broken media keys!
- **🔄 AI Fallback Chain** — If Gemini is rate-limited, MAZE auto-switches to **OpenRouter** (free models), then to **offline brain**. You're never left without answers.
- **🎙️ Offline Speech Recognition** — Uses **Vosk** to understand voice even without internet.
- **📱 Telegram Integration** — Control MAZE from your phone! Send commands via Telegram bot.
- **💻 Smart Code Writer** — *"Write Python code for a calculator"* → saves `.py` files and opens them in VS Code.
- **🗣️ Interruptible Speech** — Speak mid-sentence to interrupt MAZE. It listens while it speaks!
- **⏯️ Full Media Control** — Pause, Resume, Next, Previous, Forward/Backward (10s), Volume & Brightness.
- **🚀 Auto-Start on Boot** — Configure MAZE to launch automatically on PC startup.

---

## 🚀 Key Features

### 🎙️ Advanced Voice Control
- **Multimodal Input** — Voice or Keyboard. Say `"switch"` to toggle anytime.
- **Smart Auto-Switch** — After 5 consecutive voice failures, MAZE switches to keyboard mode automatically.
- **Offline Fallback** — Automatically uses **Vosk** offline speech when internet drops.
- **Speech Corrections** — Fixes common speech-to-text errors (`"you tube"` → `"youtube"`, `"previse"` → `"previous"`, etc.).

### 🧠 Triple AI Brain
| Priority | Provider | When Used |
|----------|----------|-----------|
| 1️⃣ | **Google Gemini** | Primary AI — smart, conversational |
| 2️⃣ | **OpenRouter** (Free) | Auto-fallback when Gemini is rate-limited |
| 3️⃣ | **Offline Brain** | Always works — handles apps, search, tasks, math, etc. |

### 📱 Telegram Bot (Remote Access)
Control your PC from anywhere using Telegram:
- Send messages to your bot, and MAZE executes them on your desktop.
- Secure access via `TELEGRAM_ALLOWED_USERS` list.
- Get responses and status updates right on your phone.

### 💻 Code Generation & Automation
- **Write Code** — *"Write Python code for a stopwatch"* → Generates code via Gemini, saves to `generated_code/`, opens in VS Code.
- **Note-Taking** — *"Note down buy milk"* → Saves to `notes.txt` and opens in Notepad.
- **Task Management** — Add, view, complete, and clear tasks. Persists across sessions.

### 🎵 YouTube Music Queue
- **Play Songs** — *"Play Emraan Hashmi songs"* → Searches YouTube, plays the first result, and saves 20 results as a queue.
- **Next / Previous** — Actually opens the next/previous video from the queue (not just media keys).
- **Pause / Resume** — Uses system media key — works with YouTube, Spotify, VLC, etc.
- **Forward / Backward** — Skip 10 seconds forward or backward on YouTube.

### 🖥️ Desktop & System Mastery
- **App Launcher** — Open 30+ apps by voice: VS Code, Chrome, Brave, WhatsApp, Telegram, Calculator, Paint, etc.
- **Website Opener** — Open 35+ websites: GitHub, Gmail, Instagram, Discord, ChatGPT, LeetCode, and more.
- **Volume Control** — Volume up/down, mute, set to specific percentage.
- **Brightness Control** — Brightness up/down, set to specific percentage.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.8+** on Windows 10/11.
- A **Gemini API Key** (Free from [Google AI Studio](https://aistudio.google.com/app/apikey)).
- Optional: **OpenRouter API Key** (Free from [OpenRouter](https://openrouter.ai/keys)).
- Optional: **Telegram Bot Token** (From [@BotFather](https://t.me/botfather)).

### 2. Clone & Install
```bash
git clone https://github.com/Lucifer-cell-metrix/maze-voice-assistants.git
cd maze-voice-assistants
pip install -r requirements.txt
```

### 3. Setup Offline Voice (Vosk)
To enable offline speech recognition:
1. Download a model from [Vosk Models](https://alphacephei.com/vosk/models) (recommended: `vosk-model-small-en-us-0.15`).
2. Extract it to a folder named `vosk-model` inside the project directory.

### 4. Configuration
Create a `.env` file (copy from `.env.example`):
```env
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
Update `config.py` with your `TELEGRAM_ALLOWED_USERS` (your numeric Telegram ID).

### 5. Run MAZE
```bash
python main.py
```

---

## 🎮 Command Guide

| Feature | Example Commands |
|---------|-----------------|
| **AI Chat** | *"Who is Elon Musk?"*, *"Explain Quantum Physics"*, *"Tell me a joke"* |
| **Play Music** | *"Play Arijit Singh songs"*, *"Play Lo-Fi"* |
| **Media Control** | *"Next"*, *"Previous"*, *"Pause"*, *"Resume"*, *"Forward"*, *"Backward"* |
| **Open Apps** | *"Open Chrome"*, *"Open VS Code"*, *"Open Calculator"* |
| **Open Websites** | *"Open GitHub"*, *"Open Instagram"*, *"Open WhatsApp"* |
| **Search** | *"Search Python tutorial"*, *"Search on YouTube AI"* |
| **Code Gen** | *"Write code for a calculator"*, *"Create a Python script for a clock"* |
| **Notes** | *"Note down buy groceries"*, *"Show my notes"*, *"Clear notes"* |
| **Tasks** | *"Add task finish project"*, *"Show my tasks"*, *"Complete task 1"* |
| **System** | *"Volume up"*, *"Mute"*, *"Set brightness to 80"* |
| **Motivation** | *"Motivate me"*, *"I feel lazy"*, *"Tell me a joke"* |
| **Control** | *"Switch"* (voice/keyboard), *"Exit"*, *"Shutdown"* |

---

## ⚙️ Auto-Start Setup
To make MAZE start when your PC turns on:
```bash
python setup_autostart.py --enable
```
Disable it anytime with `--disable`.

---

## 📦 Project Structure

```
maze/
├── main.py                    # Main loop — voice, keyboard, media controls
├── config.py                  # All settings — API keys, voice, Telegram
├── requirements.txt           # Python dependencies
├── .env.example               # Template for environment variables
├── test_mic.py                # Microphone testing utility
├── setup_autostart.py         # Windows startup configuration
├── assistant/
│   ├── brain.py               # AI brain — routing, offline skills, Gemini, OpenRouter
│   ├── telegram_bot.py        # Telegram remote control
│   ├── voice_input.py         # Voice input utilities
│   └── voice_output.py        # Voice output utilities
├── memory/
│   ├── tasks.json             # Persistent task list
│   └── notes.txt              # Saved notes
├── vosk-model/                # Offline speech model (download separately)
├── generated_code/            # Code files generated by MAZE
└── logs/                      # Assistant logs
```

---

## 🔧 Configuration Options (`config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `ASSISTANT_NAME` | `"MAZE"` | Assistant's name |
| `AI_PROVIDER` | `"gemini"` | Primary AI: `"gemini"`, `"openai"`, `"openrouter"`, or `"offline"` |
| `VOICE_RATE` | `175` | Speech speed (words per minute) |
| `VOICE_VOLUME` | `1.0` | Speech volume (0.0 to 1.0) |
| `MAX_MEMORY_TURNS` | `10` | How many conversation turns AI remembers |
| `TELEGRAM_ALLOWED_USERS` | `[]` | List of Telegram user IDs allowed to control MAZE |

---

## 📄 License & Credits
Built with ❤️ and Python. Powered by **Google Gemini** & **OpenRouter**.
Open Source under **MIT License**.

---
<p align="center"><i>"The only limit is your imagination."</i></p>
