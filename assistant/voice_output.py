"""IRON MIND — Voice Output Module"""
import pyttsx3
from config import VOICE_RATE, VOICE_VOLUME, ASSISTANT_NAME

engine = pyttsx3.init()
engine.setProperty('rate', VOICE_RATE)
engine.setProperty('volume', VOICE_VOLUME)

# Try to find a good voice
voices = engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower() or "david" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

def speak(text: str):
    """Speak the given text aloud."""
    print(f"\n🤖 {ASSISTANT_NAME}: {text}\n")
    engine.say(text)
    engine.runAndWait()
