<p align="center">
  <img src="https://img.shields.io/badge/MAZE-AI%20Assistant-blueviolet?style=for-the-badge&logo=robot&logoColor=white" alt="MAZE Badge"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/AI-Gemini%20Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
</p>

<h1 align="center">🧠 MAZE — Your Personal AI Desktop Assistant</h1>

<p align="center">
  <b>A voice-controlled AI assistant for Windows — inspired by JARVIS from Iron Man.</b><br/>
  Powered by Google Gemini AI with a fully functional offline fallback brain.
</p>

---

## ✨ What is MAZE?

**MAZE** is a personal AI desktop assistant that listens to your voice (or keyboard) and performs real actions on your computer. It can open apps, search the web, play music, manage tasks, take notes, control system volume/brightness, do math, motivate you, and even crack coding jokes — all hands-free.

It works **100% offline** with a smart command engine, and automatically upgrades to **Google Gemini AI** when an API key is available for natural language conversations.

---

## 🚀 Features

### 🎙️ Voice & Keyboard Input
- **Voice Mode** — Speak naturally; MAZE uses Google Speech Recognition to understand you.
- **Keyboard Mode** — Type commands when you don't have a mic or prefer typing.
- **Seamless Switching** — Say `"switch"` to toggle between voice and keyboard anytime.

### 🖥️ App Launcher
Open **30+ Windows applications** by name:
| Category | Apps |
|----------|------|
| **Productivity** | Notepad, VS Code, Word, Excel, PowerPoint, Outlook |
| **System** | File Explorer, Task Manager, CMD, PowerShell, Settings |
| **Browsers** | Chrome, Brave, Edge, Firefox |
| **Creative** | Paint, Snipping Tool, Camera, Photos |
| **Others** | Calculator, Calendar, Clock, Maps, Store, Xbox |

> 💡 Just say: *"Open VS Code"*, *"Launch Chrome"*, or even just *"Notepad"*

### 🌐 Website Opener
Instantly open **25+ popular websites** with a single command:

- **Social** — Instagram, Twitter, LinkedIn, Facebook, Reddit, Snapchat, Pinterest, Threads
- **Communication** — WhatsApp, Telegram, Discord, Gmail
- **AI Tools** — ChatGPT, Gemini, Claude
- **Entertainment** — Spotify, Netflix, Hotstar, Prime Video
- **Shopping** — Amazon, Flipkart, Myntra
- **Dev Tools** — GitHub, Stack Overflow, LeetCode, GeeksforGeeks
- **Productivity** — Google Drive, Google Docs, Notion, Canva, Figma
- **Learning** — Udemy, Coursera, W3Schools

> 💡 Just say: *"Open GitHub"*, *"Open WhatsApp"*, or *"Instagram"*

### 🎵 YouTube & Music
- **Play music** — *"Play Bohemian Rhapsody"* → auto-plays the first YouTube video.
- **Search YouTube** — *"Search Python tutorial on YouTube"* → opens search results only.
- Works even without saying "YouTube" — *"Play lo-fi beats"* goes straight to YouTube.

### 🔍 Web Search
- **Google Search** — *"Search how to learn Python"*
- **Wikipedia** — *"Wikipedia Albert Einstein"*
- **Learning Mode** — *"Teach me JavaScript"* → opens tutorial search results.

### 📝 Task Manager
- **Add tasks** — *"Add task finish homework"*
- **View tasks** — *"Show my tasks"*
- **Complete tasks** — *"Complete task 1"*
- **Clear all** — *"Clear tasks"*
- Tasks are saved to `memory/tasks.json` and persist across sessions.

### 📒 Note-Taking
- **Take notes** — *"Note down buy groceries tomorrow"*
- **View notes** — *"Show my notes"* → opens in Notepad automatically.
- **Clear notes** — *"Clear notes"*
- Notes are saved to `memory/notes.txt` with timestamps.

### 🔊 System Controls
| Command | Action |
|---------|--------|
| *"Volume up"* / *"Louder"* | Increase volume |
| *"Volume down"* / *"Quieter"* | Decrease volume |
| *"Mute"* / *"Unmute"* | Toggle mute |
| *"Max volume"* | Set volume to 100% |
| *"Brightness up"* / *"Brighter"* | Increase brightness |
| *"Brightness down"* / *"Dimmer"* | Decrease brightness |
| *"Set brightness to 50"* | Set exact brightness level |

### 🧮 Math Calculator
- Natural language math: *"Calculate 25 times 4"*, *"What is 100 divided by 7"*
- Supports: `+`, `-`, `×`, `÷`, `power`, `mod`
- Say *"Open calculator"* to launch the Windows Calculator app instead.

### 💪 Motivation & Fun
- **Motivational quotes** — *"Motivate me"*, *"I feel lazy"*
- **Coding jokes** — *"Tell me a joke"*
- **Status check** — *"How are you?"*
- **Time & Date** — *"What time is it?"*, *"What day is today?"*

### 🤖 AI Brain (Dual Mode)
| Mode | Description |
|------|-------------|
| **Gemini AI** | Natural conversations powered by Google Gemini (2.0 Flash Lite → 2.0 Flash → 1.5 Flash fallback chain) |
| **Offline Brain** | Smart pattern-matching engine that handles all core features without internet |

> MAZE automatically falls back to offline mode if the API is unavailable — you never lose functionality.

---

## 📁 Project Structure

```
maze/
├── main.py                  # 🚀 Entry point — voice/keyboard loop + speech engine
├── config.py                # ⚙️ Configuration (API keys, voice settings, memory)
├── requirements.txt         # 📦 Python dependencies
├── .env.example             # 🔐 Environment variable template
├── test_mic.py              # 🎤 Microphone testing utility
│
├── assistant/
│   ├── __init__.py
│   ├── brain.py             # 🧠 Core AI brain — command routing, Gemini, offline logic
│   ├── voice_input.py       # 🎙️ Voice input module
│   ├── voice_output.py      # 🔊 Voice output module
│   └── skills/
│       ├── __init__.py
│       ├── files.py          # 📂 File management (list, create, search, delete)
│       ├── system.py         # 💻 System control (apps, time, date)
│       └── web.py            # 🌐 Web search (Google, YouTube, Wikipedia)
│
├── memory/
│   ├── __init__.py
│   ├── context.py            # 🧠 Conversation memory (rolling history)
│   ├── tasks.json            # ✅ Persistent task storage
│   └── notes.txt             # 📒 Saved notes (created at runtime)
│
└── logs/
    └── assistant.log         # 📋 Activity log
```

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
- **Windows 10/11** (uses Windows-specific APIs for volume, brightness, and app launching)
- A working **microphone** (optional — keyboard mode available)

### Steps

**1. Clone or download the project:**
```bash
git clone https://github.com/your-username/maze.git
cd maze
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Set up your API key (optional but recommended):**
```bash
copy .env.example .env
```
Edit the `.env` file and add your Google Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
> Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

**4. Test your microphone (optional):**
```bash
python test_mic.py
```
This will list available microphones. Update `MIC_INDEX` in `main.py` if needed.

**5. Run MAZE:**
```bash
python main.py
```

---

## 🎮 Quick Start Commands

Once MAZE is running, try these:

```
"Hey MAZE"                    → Greeting
"Open Chrome"                 → Launch Google Chrome
"Open WhatsApp"               → Open WhatsApp Web
"Play Shape of You"           → Play on YouTube
"Search Python tutorial"      → Google search
"Add task complete project"   → Add a task
"Show my tasks"               → View pending tasks
"Note down call mom at 6pm"   → Save a note + open in Notepad
"Volume up"                   → Increase system volume
"Calculate 15 times 8"        → Quick math
"Motivate me"                 → Inspirational quote
"Tell me a joke"              → Coding humor
"What time is it?"            → Current time
"Switch"                      → Toggle voice ↔ keyboard
"Goodbye"                     → Shut down MAZE
```

---

## ⚙️ Configuration

All settings are in **`config.py`**:

| Setting | Default | Description |
|---------|---------|-------------|
| `ASSISTANT_NAME` | `"MAZE"` | Name of the assistant |
| `VOICE_RATE` | `175` | Speech speed (words per minute) |
| `VOICE_VOLUME` | `1.0` | Speech volume (0.0 – 1.0) |
| `AI_PROVIDER` | `"gemini"` | AI provider: `"gemini"`, `"openai"`, or `"offline"` |
| `MAX_MEMORY_TURNS` | `10` | Number of past messages to remember |
| `ENABLE_LOGGING` | `True` | Enable/disable activity logging |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `SpeechRecognition` | Voice-to-text via Google Speech API |
| `pyttsx3` | Text-to-speech (offline, uses Windows SAPI) |
| `PyAudio` | Microphone input stream |
| `google-generativeai` | Google Gemini AI integration |
| `openai` | OpenAI GPT integration (optional) |
| `python-dotenv` | Load environment variables from `.env` |
| `requests` | HTTP requests (YouTube video lookup) |

---

## 🧩 How It Works

```
┌─────────────────────────────────────────────────┐
│                    USER INPUT                    │
│            (Voice 🎙️  or  Keyboard ⌨️)           │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│               COMMAND ROUTER                     │
│          (assistant/brain.py)                     │
│                                                  │
│  1. Greetings & Identity                         │
│  2. YouTube / Play Music                         │
│  3. Open Apps & Websites                         │
│  4. Web Search (Google / Wikipedia)              │
│  5. Task Management                              │
│  6. Note-Taking                                  │
│  7. System Controls (Volume / Brightness)        │
│  8. Math Calculator                              │
│  9. Motivation & Jokes                           │
│  10. Learning Resources                          │
│  11. Gemini AI (fallback for unknown queries)    │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│                VOICE RESPONSE                    │
│         (pyttsx3 — Zira voice 🔊)                │
└─────────────────────────────────────────────────┘
```

---

## 🛡️ Privacy & Security

- **No data collection** — MAZE runs entirely on your machine.
- **API keys stay local** — Stored in your `.env` file, never transmitted elsewhere.
- **Offline capable** — Works without internet using the smart offline brain.
- **Open source** — Full transparency, inspect every line of code.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <b>Built with ❤️ and Python</b><br/>
  <i>"The only limit is your imagination."</i>
</p>
