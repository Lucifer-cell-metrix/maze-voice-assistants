"""IRON MIND — Voice Input Module"""
import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

def listen(timeout: int = 7) -> str:
    with sr.Microphone() as source:
        print("🎙️  Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            command = recognizer.recognize_google(audio)
            print(f"👤 You: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return "__unrecognized__"
        except sr.RequestError:
            return "__error__"
