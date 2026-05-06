# 🤖 MAZE AI Voice Assistant

MAZE is a fast, lightweight, and completely local-first AI voice assistant designed for Windows. It acts as a highly capable desktop companion, letting you control your PC, write code, search the web, and manage your day using natural language.

---

## ✨ Features

- **⚡ Instant Desktop Control**: Launch applications, find files across your drives, adjust volume/brightness, and control media playback using quick commands.
- **🧠 Hybrid AI Brain**: Uses a fast local model via Ollama for intent parsing and privacy, with fallback to Google Gemini or OpenRouter for complex factual or conversational queries.
- **💬 Seamless Communication**: Integrates with WhatsApp and Instagram for hands-free messaging and calling.
- **📱 Telegram Remote**: Control MAZE directly from your phone using the Telegram bot (`/internship` command included!).
- **💼 Internship Finder**: Find the best internships from Internshala matching your criteria (e.g. "Find remote Python internships").
- **🧩 Modular Architecture**: Highly extensible codebase separated into actions (`apps`, `media`, `web`, `tasks`, etc.) and AI providers (`ollama`, `gemini`, `openrouter`).
- **📝 Persistent Smart Memory**: Automatically summarizes conversations every 20 turns and remembers personal facts to build context across reboots.

---

## 🛠️ Setup & Installation

### 1. Requirements
- **OS**: Windows 10/11
- **Python**: 3.10+
- **Microphone**: Required for voice commands

### 2. Install Dependencies
Clone the repository and install the required packages:

```cmd
git clone https://github.com/yourusername/MAZE.git
cd MAZE
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Rename `.env.example` to `.env` and fill in your API keys:

```env
# Google Gemini (Cloud AI Fallback)
GEMINI_API_KEY=your_gemini_key

# Telegram Bot (Remote Control)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OpenRouter (Optional Fallback)
OPENROUTER_API_KEY=your_openrouter_key
```

### 4. Running MAZE
You can start MAZE using the provided batch script:
```cmd
start_maze.bat
```
Or directly via Python:
```cmd
venv\Scripts\python.exe main.py
```

### 5. Auto-Start on Windows Boot
Want MAZE to be ready as soon as you turn on your PC? Run the setup script:
```cmd
venv\Scripts\python.exe setup_autostart.py --enable
```
*(To disable: `setup_autostart.py --disable`)*

---

## 🗣️ Voice Commands Example

Here are some things you can say to MAZE:

- **Apps & Files**: *"Open VS Code"*, *"Find file report.pdf"*, *"Open YouTube"*
- **Media**: *"Play lo-fi hip hop"*, *"Next track"*, *"Pause music"*
- **System**: *"Volume up"*, *"Set brightness to 50"*, *"Mute"*
- **Tasks & Notes**: *"Add task finish homework"*, *"Note down my meeting is at 5 PM"*
- **Communication**: *"Message John on WhatsApp"*
- **Jobs**: *"Find remote cybersecurity internships"*
- **Coding**: *"Write a Python script for a tic-tac-toe game"*

---

## 🏗️ Architecture

MAZE is designed to be highly modular. The main command flow:
1. `main.py` captures voice/keyboard input.
2. `assistant/brain.py` routes the command.
3. If it's an actionable command, it routes to `assistant/actions/`.
4. If it's a conversational/knowledge query, it goes to `assistant/ai_providers/` (Ollama -> Gemini -> OpenRouter).
5. All context is saved and summarized in `assistant/memory_module/`.

---

## 🤝 Contributing
Contributions are welcome! If you have a cool action module you want to add, feel free to submit a PR.

## 📄 License
This project is open-source and available under the MIT License.
