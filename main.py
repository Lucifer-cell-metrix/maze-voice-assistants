import speech_recognition as sr
import pyttsx3
import datetime
import sys
import os
import time

# ── Load config ──────────────────────────────────────
sys.path.append(os.path.dirname(__file__))
from config import ASSISTANT_NAME, VOICE_RATE, VOICE_VOLUME
from assistant.brain import get_response

# Global flag to control the assistant
RUNNING = True

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

def speak(text: str):
    """Convert text to speech and print to console."""
    if not RUNNING:
        return
    print(f"\n🤖 MAZE: {text}\n")
    try:
        eng = _create_engine()
        eng.say(text)
        eng.runAndWait()
        eng.stop()
        del eng
    except Exception as e:
        print(f"   (Voice error: {e} — text shown above)")

def shutdown():
    """Force stop everything immediately."""
    global RUNNING
    RUNNING = False
    print("\n🤖 MAZE: Shutdown complete. Goodbye.\n")
    os._exit(0)  # Force kill everything including speech

# ── Voice Input Setup ────────────────────────────────
recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000      # Higher = needs louder voice (avoid background noise)
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1          # Seconds of silence before phrase is considered complete

# Use Microphone Array (index 2 = Realtek) — change if your mic is different
MIC_INDEX = 2  # Run test_mic.py to see your available microphones

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
    """Listen from microphone and return recognized text."""
    try:
        with sr.Microphone(device_index=MIC_INDEX) as source:
            print("🎙️  Listening... (speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=8)

            print("   ⏳ Processing your voice...")
            command = recognizer.recognize_google(audio)
            print(f"👤 You: {command}")
            return command.lower()

    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        print("   ⚠️  Couldn't understand. Try again.")
        return ""
    except sr.RequestError as e:
        print(f"   ❌ Google API error: {e}")
        return ""
    except KeyboardInterrupt:
        return "__exit__"
    except Exception as e:
        print(f"   ❌ Mic error: {e}")
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
    speak(f"{greeting}. MAZE online. All systems ready.")

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

    speak("What is your mission?")

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
                print("💡 Tip: Type 'switch' to use keyboard input instead.\n")
                idle_count = 0
            time.sleep(0.3)
            continue

        idle_count = 0

        # ── Special commands ──────────────────
        if "switch" in command:
            if INPUT_MODE == "voice":
                INPUT_MODE = "type"
                speak("Switched to keyboard mode. Type your commands.")
            else:
                INPUT_MODE = "voice"
                speak("Switched to voice mode. Speak your commands.")
            continue

        # Exit commands
        if any(word in command for word in ["stop", "exit", "shutdown", "goodbye", "bye", "quit"]):
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
