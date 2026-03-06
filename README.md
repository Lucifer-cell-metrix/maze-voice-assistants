<p align="center">
  <img src="https://img.shields.io/badge/MAZE-AI%20Assistant-blueviolet?style=for-the-badge&logo=robot&logoColor=white" alt="MAZE Badge"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/AI-Gemini%20Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
</p>

<h1 align="center">🧠 MAZE — Your Advanced AI Desktop Assistant</h1>

<p align="center">
  <b>A powerful, voice-controlled AI assistant for Windows — inspired by JARVIS.</b><br/>
  Featuring <b>Offline Speech Recognition</b>, <b>Telegram Remote Control</b>, and <b>Smart Code Generation</b>.
</p>

---

## ✨ New in MAZE (Latest Updates)

- **🎙️ Offline Speech Recognition** — Uses **Vosk** to understand voice even when internet is down.
- **📱 Telegram Integration** — Control MAZE from your phone! Send commands via Telegram bot.
- **💻 Smart Code Writer** — Ask MAZE to *"Write Python code for a calculator"* and it saves `.py` files and opens them in VS Code.
- **🗣️ Interruptible Speech** — Speak mid-sentence or say *"Stop"* to interrupt MAZE. It now listens while it speaks!
- **⏯️ Full Media Control** — Pause, Resume, Next, and Previous track support for YouTube and system media.
- **🚀 Auto-Start on Boot** — Configure MAZE to start automatically when you turn on your PC.

---

## 🚀 Key Features

### 🎙️ Advanced Voice Control
- **Multimodal Input** — Voice or Keyboard. Say `"switch"` to toggle.
- **Non-Blocking Logic** — MAZE listens while it speaks. Interrupt it anytime with a new command.
- **Proactive Offline Model** — Automatically switches to **Vosk** offline brain if internet is disconnected.

### 📱 Telegram Bot (Remote Access)
Control your PC from anywhere using Telegram:
- Send messages to your bot, and MAZE executes them on your desktop.
- Secure access via `TELEGRAM_ALLOWED_USERS` list.
- Get status updates or stop MAZE remotely.

### 💻 Code Generation & Automation
- **Write Code** — Generates scripts using Gemini, saves them to `generated_code/`, and launches VS Code.
- **Note-Taking** — *"Note down buy milk"* saves to `notes.txt` and opens it for you.
- **Task Management** — Full persistent task list handling.

### 🖥️ Desktop & Media Mastery
- **App Launcher** — Launch 30+ apps (VS Code, Chrome, WhatsApp, etc.).
- **Media Controller** — Full control over YouTube/Spotify (Play, Pause, Next, Previous).
- **System Control** — Volume and Brightness control by voice.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.8+** on Windows 10/11.
- A **Gemini API Key** (Free from [Google AI Studio](https://aistudio.google.com)).
- Optional: **Telegram Bot Token** (From [@BotFather](https://t.me/botfather)).

### 2. Install Dependencies
```bash
git clone https://github.com/Lucifer-cell-metrix/maze-voice-assistants.git
cd maze
pip install -r requirements.txt
```

### 3. Setup Offline Voice (Vosk)
To enable offline speech recognition:
1. Download a model from [Vosk Models](https://alphacephei.com/vosk/models) (suggested: `vosk-model-small-en-us-0.15`).
2. Extract it to a folder named `vosk-model` inside the project directory.

### 4. Configuration (.env)
Create a `.env` file (see `.env.example`):
```env
GEMINI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
Update `config.py` with your `TELEGRAM_ALLOWED_USERS` (your numeric Telegram ID).

---

## 🎮 Command Guide

| Feature | Commands |
|---------|----------|
| **AI Conversation** | *"Who is Elon Musk?"*, *"Explain Quantum Physics"* |
| **Media Control** | *"Pause video"*, *"Next track"*, *"Play Saiyaara"* |
| **Automation** | *"Write a Python script for a clock"*, *"Note buy groceries"* |
| **System** | *"Volume up"*, *"Set brightness to 80"*, *"Open VS Code"* |
| **Tasks** | *"Add task finish project"*, *"Show my tasks"* |
| **Control** | *"Stop"*, *"Hey stop"*, *"Switch mode"*, *"Exit"* |

---

## ⚙️ Auto-Start Setup
To make MAZE start when your PC turns on, run:
```bash
python setup_autostart.py --enable
```
You can disable it anytime with `--disable`.

---

## 📦 Project Structure
- `main.py`: The heart of MAZE. Handles the main loop and speech.
- `assistant/brain.py`: The logic center. Routes commands to skills.
- `assistant/telegram_bot.py`: Handles remote Telegram commands.
- `setup_autostart.py`: Easy Windows boot configuration.
- `vosk-model/`: Place your offline voice models here.
- `generated_code/`: Where MAZE saves the code it writes for you.

---

## 📄 License & Credits
Built with ❤️ and Python. Powered by **Google Gemini**.
Open Source under **MIT License**.

---
<p align="center"><i>"The only limit is your imagination."</i></p>
