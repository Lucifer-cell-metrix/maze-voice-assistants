"""Quick test to check microphone and voice"""
import speech_recognition as sr
import pyttsx3

# ── Step 1: List all microphones ──
print("=" * 50)
print("🎤 AVAILABLE MICROPHONES:")
print("=" * 50)
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  [{i}] {name}")
print("=" * 50)

# ── Step 2: Test voice output ──
print("\n🔊 Testing voice output...")
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.say("MAZE voice output test. Can you hear me?")
engine.runAndWait()
print("✅ Voice output working!\n")

# ── Step 3: Test microphone input ──
print("🎙️  Testing microphone input...")
print("   Say something in the next 5 seconds...\n")
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300

try:
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("   Listening NOW → speak!")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        print("   Got audio! Sending to Google for recognition...")
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"\n✅ SUCCESS! You said: \"{text}\"")
            print("\n🎉 Your microphone is working perfectly!")
        except sr.UnknownValueError:
            print("\n⚠️  Audio captured but couldn't understand words.")
            print("   → Try speaking louder or closer to mic.")
        except sr.RequestError as e:
            print(f"\n❌ Google API error: {e}")
            print("   → Check your internet connection.")
            
except sr.WaitTimeoutError:
    print("\n❌ No sound detected in 5 seconds.")
    print("   → Check if your microphone is enabled in Windows Settings.")
    print("   → Right-click speaker icon → Sound Settings → Input")
except OSError as e:
    print(f"\n❌ Microphone error: {e}")
    print("   → No microphone found or it's being used by another app.")
    print("   → Close other apps using mic (Discord, Zoom, etc.)")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
