import speech_recognition as sr
import pyttsx3
import datetime
import sys
import os
import time
import socket
import json
import threading

# ── Load config ──────────────────────────────────────
sys.path.append(os.path.dirname(__file__))
from config import ASSISTANT_NAME, VOICE_RATE, VOICE_VOLUME
from assistant.brain import get_response

# Global flag to control the assistant
RUNNING = True
_voice_fail_count = 0          # Track consecutive voice failures
MAX_VOICE_FAILS = 5            # Higher tolerance before switching to keyboard
_speech_thread = None          # Thread running the current speech
_stop_speaking = False         # Flag to interrupt speech
_current_engine = None         # Reference to active pyttsx3 engine (for force-stop)

# ── Voice Output Setup ───────────────────────────────
def _create_engine():
    """Create a fresh pyttsx3 engine (fixes Windows hanging bug)."""
    eng = pyttsx3.init()
    eng.setProperty('rate', 155)      # Slower = smoother, calmer voice
    eng.setProperty('volume', 0.9)    # Slightly lower volume
    voices = eng.getProperty('voices')
    # Prefer Zira (soft female voice) for a smoother AI sound
    for v in voices:
        if "zira" in v.name.lower():
            eng.setProperty('voice', v.id)
            break
    return eng

def _speak_worker(text: str):
    """Worker function that runs speech in a thread."""
    global _current_engine
    try:
        eng = _create_engine()
        _current_engine = eng  # Store so stop_speaking() can kill it
        eng.say(text)
        eng.runAndWait()
        _current_engine = None
        eng.stop()
        del eng
    except Exception as e:
        _current_engine = None

def speak(text: str, wait=False):
    """Convert text to speech and print to console.
    wait=False (default): starts speech in background, returns immediately.
    wait=True: blocks until speech is finished."""
    global _speech_thread, _stop_speaking
    if not RUNNING:
        return
    print(f"\n🤖 MAZE: {text}\n")

    # Stop any ongoing speech first
    stop_speaking()

    # Start new speech
    _stop_speaking = False
    if wait:
        _speak_worker(text)
    else:
        _speech_thread = threading.Thread(target=_speak_worker, args=(text,), daemon=True)
        _speech_thread.start()

def stop_speaking():
    """Interrupt current speech immediately by killing the engine."""
    global _stop_speaking, _current_engine
    _stop_speaking = True
    # Force-stop the pyttsx3 engine — this makes runAndWait() exit immediately
    if _current_engine:
        try:
            _current_engine.stop()
        except:
            pass
        _current_engine = None
    if _speech_thread and _speech_thread.is_alive():
        _speech_thread.join(timeout=0.5)

def is_speaking() -> bool:
    """Check if MAZE is currently speaking."""
    return _speech_thread is not None and _speech_thread.is_alive()

def shutdown():
    """Force stop everything immediately."""
    global RUNNING, _stop_speaking
    RUNNING = False
    _stop_speaking = True
    print("\n🤖 MAZE: Shutdown complete. Goodbye.\n")
    os._exit(0)  # Force kill everything including speech

# ── YouTube / Media Control ──────────────────────────
import ctypes
import ctypes.wintypes

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT = 0xB0
VK_MEDIA_PREV = 0xB1
VK_SHIFT = 0x10
VK_N = ord('N')
VK_P = ord('P')
VK_L = ord('L')
VK_J = ord('J')

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.wintypes.WORD),
                ("wScan", ctypes.wintypes.WORD),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.wintypes.DWORD),
                ("ki", KEYBDINPUT),
                ("padding", ctypes.c_ubyte * 8)]

def _send_input(vk_codes, down=True):
    """Helper to send key up/down events."""
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    INPUT_KEYBOARD = 1
    
    inputs = []
    for vk in vk_codes:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.ki.wVk = vk
        
        flags = 0
        # Media keys (0xB0-0xB3) and volume keys (0xAD-0xAF) are extended keys
        if 0xAD <= vk <= 0xB3:
            flags |= KEYEVENTF_EXTENDEDKEY
            
        if not down:
            flags |= KEYEVENTF_KEYUP
        inp.ki.dwFlags = flags
        inputs.append(inp)
    
    n = len(inputs)
    if n > 0:
        ctypes.windll.user32.SendInput(n, ctypes.byref((INPUT * n)(*inputs)), ctypes.sizeof(INPUT))

def _press_media_key(vk_code):
    """Simulate a media key press (down then up)."""
    _send_input([vk_code], down=True)
    _send_input([vk_code], down=False)

def _send_combination(vk_codes):
    """Send a combination like Shift + N."""
    # Press all down
    for vk in vk_codes:
        _send_input([vk], down=True)
    # Release all in reverse
    for vk in reversed(vk_codes):
        _send_input([vk], down=False)

def _has_media_word(command: str, words: list) -> bool:
    """Check if any word from the list appears in the command."""
    cmd_words = command.lower().split()
    return any(w in cmd_words for w in words)

# ── Vosk Offline Speech Recognition ──────────────────
VOSK_AVAILABLE = False
vosk_model = None

def _init_vosk():
    """Initialize Vosk offline speech recognition model."""
    global VOSK_AVAILABLE, vosk_model
    try:
        from vosk import Model, SetLogLevel
        SetLogLevel(-1)  # Suppress vosk logs BEFORE loading model

        # Use absolute path — Vosk needs it on Windows
        project_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(project_dir, "vosk-model")

        if os.path.exists(model_path):
            vosk_model = Model(model_path)
            VOSK_AVAILABLE = True
            return True

        # Check common download locations
        home_model = os.path.expanduser("~/.vosk/vosk-model-small-en-us-0.15")
        if os.path.exists(home_model):
            vosk_model = Model(home_model)
            VOSK_AVAILABLE = True
            return True

        print("   ⚠️  Vosk model not found. Offline speech won't work.")
        print("   💡 Download from: https://alphacephei.com/vosk/models")
        print(f"   📂 Extract to: {model_path}\\")
        return False
    except ImportError:
        print("   ⚠️  Vosk not installed. Run: pip install vosk")
        return False
    except Exception as e:
        print(f"   ⚠️  Vosk init error: {e}")
        return False

def _listen_vosk() -> str:
    """Offline speech recognition using Vosk."""
    try:
        from vosk import KaldiRecognizer
        import pyaudio

        mic = pyaudio.PyAudio()
        stream = mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=MIC_INDEX,
            frames_per_buffer=8192
        )
        stream.start_stream()

        rec = KaldiRecognizer(vosk_model, 16000)
        print("🎙️  Listening offline... (speak now)")

        timeout_start = time.time()
        heard_something = False

        while True:
            # Timeout after 7 seconds of no speech
            if time.time() - timeout_start > 7 and not heard_something:
                stream.stop_stream()
                stream.close()
                return ""

            # Max listening time 10 seconds
            if time.time() - timeout_start > 10:
                break

            data = stream.read(4096, exception_on_overflow=False)

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    stream.stop_stream()
                    stream.close()
                    print(f"👤 You: {text}")
                    return text.lower()
            else:
                partial = json.loads(rec.PartialResult())
                if partial.get("partial", "").strip():
                    heard_something = True

        # Get final result
        result = json.loads(rec.FinalResult())
        text = result.get("text", "").strip()
        stream.stop_stream()
        stream.close()

        if text:
            print(f"👤 You: {text}")
            return text.lower()
        return ""

    except Exception as e:
        print(f"   ❌ Offline speech error: {e}")
        return ""

# ── Voice Input Setup ────────────────────────────────
recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000      # Higher = needs louder voice (avoid background noise)
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1          # Seconds of silence before phrase is considered complete

# Use Microphone Array (index 2 = Realtek) — change if your mic is different
MIC_INDEX = 2  # Run test_mic.py to see your available microphones

def _check_internet(timeout=1.5) -> bool:
    """Quick internet connectivity check before attempting voice recognition."""
    try:
        socket.create_connection(("www.google.com", 80), timeout=timeout)
        return True
    except OSError:
        return False

MIC_AVAILABLE = True

def test_microphone() -> bool:
    """Quick test to see if a microphone is accessible."""
    try:
        with sr.Microphone(device_index=MIC_INDEX) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
        return True
    except Exception:
        return False

def listen() -> str:
    """Listen from microphone. Uses Google online, falls back to Vosk offline."""
    global _voice_fail_count, INPUT_MODE

    has_internet = _check_internet()

    # ── Try Google (online) first ──
    if has_internet:
        try:
            with sr.Microphone(device_index=MIC_INDEX) as source:
                print("🎙️  Listening... (speak now)")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=7, phrase_time_limit=8)

                print("   ⏳ Processing your voice...")
                command = recognizer.recognize_google(audio)
                print(f"👤 You: {command}")
                _voice_fail_count = 0   # Reset on success
                return command.lower()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            _voice_fail_count += 1
            print("   ⚠️  Couldn't understand. Try again.")
            if _voice_fail_count >= MAX_VOICE_FAILS:
                INPUT_MODE = "type"
                _voice_fail_count = 0
                print("\n🔄 Auto-switched to keyboard mode (too many failed attempts).")
                print("   → Type 'switch' to go back to voice mode.\n")
            return ""
        except sr.RequestError as e:
            # Connection error — fall through to Vosk
            print(f"   ⚠️  Google Speech API error. Trying offline recognition...")
        except KeyboardInterrupt:
            return "__exit__"
        except json.JSONDecodeError:
            _voice_fail_count += 1
            print("   ⚠️  Voice API returned empty response.")
            return ""
        except Exception as e:
            _voice_fail_count += 1
            print(f"   ❌ Mic error: {e}")
            return ""

    # ── Fall back to Vosk (offline) ──
    if VOSK_AVAILABLE:
        if not has_internet:
            print("   📡 No internet — using offline speech recognition.")
        result = _listen_vosk()
        if result:
            _voice_fail_count = 0
            return result
        else:
            _voice_fail_count += 1
            if not result and _voice_fail_count >= MAX_VOICE_FAILS:
                INPUT_MODE = "type"
                _voice_fail_count = 0
                print("\n🔄 Auto-switched to keyboard mode (too many failed attempts).")
                print("   → Type 'switch' to go back to voice mode.\n")
            return ""
    else:
        # No Vosk and no internet
        if not has_internet:
            _voice_fail_count += 1
            print("   ⚠️  No internet and no offline model available.")
            if _voice_fail_count >= MAX_VOICE_FAILS:
                INPUT_MODE = "type"
                _voice_fail_count = 0
                print("\n🔄 Auto-switched to keyboard mode (no connection).")
                print("   → Type 'switch' when internet is back.\n")
        return ""

def listen_keyboard() -> str:
    """Fallback: get command from keyboard input."""
    try:
        command = input("⌨️  Type command → ").strip()
        return command.lower()
    except (EOFError, KeyboardInterrupt):
        return "__exit__"

# ── Input Mode Selection ─────────────────────────────
INPUT_MODE = "voice"  # "voice" or "type"

def get_command() -> str:
    """Get command using the current input mode."""
    global INPUT_MODE
    if INPUT_MODE == "voice":
        return listen()
    else:
        return listen_keyboard()

# ── Greeting ─────────────────────────────────────────
def get_greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    elif hour < 21:
        return "Good evening"
    else:
        return "Good night"

# ── Main Loop ─────────────────────────────────────────
def run():
    global INPUT_MODE, MIC_AVAILABLE

    greeting = get_greeting()
    speak(f"{greeting}. MAZE online. All systems ready.", wait=True)

    # Check microphone
    print("🔍 Checking microphone...")
    MIC_AVAILABLE = test_microphone()

    if MIC_AVAILABLE:
        print("✅ Microphone detected!")
        print("   → Say commands out loud OR type 'switch' to use keyboard.\n")
        INPUT_MODE = "voice"
    else:
        print("⚠️  No microphone detected. Switching to keyboard mode.")
        print("   → Type your commands below.\n")
        INPUT_MODE = "type"

    # Initialize Vosk for offline speech
    print("🔍 Checking offline speech engine...")
    if _init_vosk():
        print("✅ Offline speech ready! Voice works even without internet.\n")
    else:
        print("⚠️  Offline speech not available. Voice needs internet.\n")

    # Start Telegram bot (if configured)
    print("🔍 Checking Telegram bot...")
    try:
        from assistant.telegram_bot import start_telegram_bot
        if start_telegram_bot():
            print("   📱 Telegram bot is running! Control MAZE from your phone.\n")
        else:
            print("   ℹ️  Telegram not configured. See config.py to set it up.\n")
    except Exception as e:
        print(f"   ⚠️  Telegram bot skipped: {e}\n")

    speak("What is your mission?", wait=True)

    idle_count = 0

    while True:
        try:
            command = get_command()
        except KeyboardInterrupt:
            speak("Shutting down. Stay focused.")
            break

        if command == "__exit__":
            print("\n\U0001f916 MAZE: Shutting down. Stay focused.\n")
            shutdown()

        if not command:
            idle_count += 1
            if idle_count >= 5:
                # Only show tip if MAZE is NOT currently speaking
                if not is_speaking():
                    print("💡 Tip: Type 'switch' to use keyboard input instead.\n")
                idle_count = 0
            time.sleep(0.3)
            continue

        idle_count = 0

        # ── ALWAYS stop any ongoing speech when user speaks ──
        if is_speaking():
            stop_speaking()

        # ── Pause / Stop / Resume media ────────
        # Use word-level matching so "image stop", "pause YouTube video", etc. all work
        if _has_media_word(command, ["stop", "pause", "silence", "quiet", "enough"]):
            _press_media_key(VK_MEDIA_PLAY_PAUSE)  # Toggle play/pause on YouTube etc.
            speak("Paused.")
            continue

        # "play" ALONE (no song name) = resume media. "play [song]" goes to YouTube.
        cmd_clean = command.strip()
        play_words = cmd_clean.replace("the", "").replace("a", "").replace("ok", "").strip()
        if play_words in ["play", "play video", "play music", "resume",
                          "resume video", "resume music", "unpause", "continue"]:
            _press_media_key(VK_MEDIA_PLAY_PAUSE)  # Toggle play/pause
            speak("Resumed.")
            continue

        # Next track / Skip forward
        if _has_media_word(command, ["next"]):
            # Use YouTube playlist from brain.py if available
            from assistant.brain import _yt_playlist, _yt_current_idx
            import assistant.brain as _brain
            if _brain._yt_playlist and _brain._yt_current_idx < len(_brain._yt_playlist) - 1:
                _brain._yt_current_idx += 1
                import webbrowser
                video_url = f"https://www.youtube.com/watch?v={_brain._yt_playlist[_brain._yt_current_idx]}"
                webbrowser.open(video_url)
                remaining = len(_brain._yt_playlist) - _brain._yt_current_idx - 1
                speak(f"Next track. {remaining} more in queue.")
            elif _brain._yt_playlist and _brain._yt_current_idx >= len(_brain._yt_playlist) - 1:
                speak("That was the last track. Say 'play' followed by a song name to start fresh.")
            else:
                # No YouTube playlist — try media key + YouTube shortcut
                _press_media_key(VK_MEDIA_NEXT)
                _send_combination([VK_SHIFT, VK_N])
                speak("Next track.")
            continue

        if _has_media_word(command, ["forward", "skip"]):
            _press_media_key(VK_L)  # YouTube shortcut (forward 10s)
            speak("Skipped forward.")
            continue

        # Previous track / Skip backward
        if _has_media_word(command, ["previous"]):
            # Use YouTube playlist from brain.py if available
            import assistant.brain as _brain
            if _brain._yt_playlist and _brain._yt_current_idx > 0:
                _brain._yt_current_idx -= 1
                import webbrowser
                video_url = f"https://www.youtube.com/watch?v={_brain._yt_playlist[_brain._yt_current_idx]}"
                webbrowser.open(video_url)
                speak("Previous track.")
            elif _brain._yt_playlist and _brain._yt_current_idx <= 0:
                speak("Already at the first track.")
            else:
                # No YouTube playlist — try media key + YouTube shortcut
                _press_media_key(VK_MEDIA_PREV)
                _send_combination([VK_SHIFT, VK_P])
                speak("Previous track.")
            continue

        if _has_media_word(command, ["backward", "back", "rewind"]):
            _press_media_key(VK_J)  # YouTube shortcut (backward 10s)
            speak("Skipped backward.")
            continue

        # ── Special commands ──────────────────
        if "switch" in command:
            _voice_fail_count = 0   # Reset fail counter on manual switch
            if INPUT_MODE == "voice":
                INPUT_MODE = "type"
                speak("Switched to keyboard mode. Type your commands.")
            else:
                if MIC_AVAILABLE:
                    INPUT_MODE = "voice"
                    speak("Switched to voice mode. Speak your commands.")
                else:
                    speak("No microphone detected. Staying in keyboard mode.")
            continue

        # Exit commands
        if any(word in command for word in ["exit", "shutdown", "goodbye", "bye", "quit"]):
            stop_speaking()
            print("\n\U0001f916 MAZE: Shutting down. Stay disciplined. See you soon.\n")
            shutdown()

        # Get AI response
        try:
            response = get_response(command)
            speak(response)
        except Exception as e:
            print(f"   ❌ Error getting response: {e}")
            speak("I hit an error processing that. Let me try again.")

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        shutdown()
