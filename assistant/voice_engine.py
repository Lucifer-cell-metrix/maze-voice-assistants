"""
MAZE — Neural Voice Engine (edge-tts)
Uses Microsoft Edge TTS for natural, human-like girl voice.
Falls back to pyttsx3 if edge-tts is unavailable.
"""

import asyncio
import os
import sys
import tempfile
import threading
import time
import subprocess

# ── Edge-TTS Configuration ────────────────────────────
# Aria = confident, mature, professional woman (JARVIS-style)
# Other options: en-US-JennyNeural (warm), en-US-AnaNeural (young),
#                en-GB-SoniaNeural (British), en-US-MichelleNeural (smooth)
DEFAULT_VOICE = "en-US-AriaNeural"
FALLBACK_VOICE = "en-US-JennyNeural"

# Voice style settings
VOICE_RATE = "+3%"         # Slightly faster for natural feel
VOICE_PITCH = "-1Hz"       # Slightly lower pitch = mature, confident tone
VOICE_VOLUME = "+0%"       # Normal volume

_edge_tts_available = False
_pygame_available = False
_playback_lock = threading.Lock()
_current_playback_process = None  # Track current playback for interruption
_stop_flag = False

def _check_dependencies():
    """Check if edge-tts and a playback method are available."""
    global _edge_tts_available, _pygame_available
    try:
        import edge_tts
        _edge_tts_available = True
    except ImportError:
        _edge_tts_available = False
        print("   ⚠️  edge-tts not installed. Run: pip install edge-tts")
    
    try:
        import pygame
        _pygame_available = True
    except ImportError:
        _pygame_available = False
        # We'll use subprocess playback as fallback

_check_dependencies()


def _get_event_loop():
    """Get or create an event loop that works in threads."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def _generate_speech_async(text: str, output_path: str, voice: str = None) -> bool:
    """Generate speech audio file using edge-tts."""
    try:
        import edge_tts
        
        voice = voice or DEFAULT_VOICE
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=VOICE_RATE,
            pitch=VOICE_PITCH,
            volume=VOICE_VOLUME
        )
        await communicate.save(output_path)
        return True
    except Exception as e:
        # Try fallback voice
        if voice != FALLBACK_VOICE:
            try:
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=FALLBACK_VOICE,
                    rate=VOICE_RATE,
                    pitch=VOICE_PITCH,
                    volume=VOICE_VOLUME
                )
                await communicate.save(output_path)
                return True
            except:
                pass
        print(f"   ❌ TTS generation error: {e}")
        return False


def generate_speech(text: str, output_path: str = None) -> str:
    """Generate speech audio file. Returns path to the audio file."""
    if not _edge_tts_available:
        return None
    
    if output_path is None:
        # Use temp file
        fd, output_path = tempfile.mkstemp(suffix=".mp3", prefix="maze_tts_")
        os.close(fd)
    
    loop = _get_event_loop()
    success = loop.run_until_complete(_generate_speech_async(text, output_path))
    
    if success and os.path.exists(output_path):
        return output_path
    return None


def play_audio(filepath: str) -> bool:
    """Play an audio file. Returns True if playback started successfully."""
    global _current_playback_process, _stop_flag
    _stop_flag = False
    
    if not os.path.exists(filepath):
        return False
    
    with _playback_lock:
        # Method 1: pygame (best quality, non-blocking possible)
        if _pygame_available:
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                # Wait for playback to finish (but check stop flag)
                while pygame.mixer.music.get_busy():
                    if _stop_flag:
                        pygame.mixer.music.stop()
                        return True
                    time.sleep(0.05)
                return True
            except Exception as e:
                print(f"   ⚠️  pygame playback error: {e}")
        
        # Method 2: Windows Media Player via PowerShell (hidden)
        if sys.platform == "win32":
            try:
                # Use PowerShell to play audio silently
                cmd = [
                    "powershell", "-WindowStyle", "Hidden", "-Command",
                    f'$player = New-Object System.Media.SoundPlayer; '
                    f'Add-Type -AssemblyName PresentationCore; '
                    f'$mp = New-Object System.Windows.Media.MediaPlayer; '
                    f'$mp.Open([System.Uri]::new("{filepath}")); '
                    f'$mp.Play(); '
                    f'Start-Sleep -Milliseconds 500; '
                    f'while ($mp.Position -lt $mp.NaturalDuration.TimeSpan) {{ Start-Sleep -Milliseconds 100 }}; '
                    f'$mp.Close()'
                ]
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _current_playback_process = proc
                proc.wait()
                _current_playback_process = None
                return True
            except Exception as e:
                _current_playback_process = None
                # Fallback: use ffplay if available
                try:
                    proc = subprocess.Popen(
                        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    _current_playback_process = proc
                    proc.wait()
                    _current_playback_process = None
                    return True
                except:
                    _current_playback_process = None
        
        return False


def speak_neural(text: str) -> bool:
    """Full pipeline: generate speech with edge-tts and play it.
    Returns True if successful, False if fallback needed."""
    if not _edge_tts_available:
        return False
    
    try:
        # Generate audio
        audio_path = generate_speech(text)
        if not audio_path:
            return False
        
        # Play audio
        success = play_audio(audio_path)
        
        # Cleanup temp file
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass
        
        return success
    except Exception as e:
        print(f"   ⚠️  Neural voice error: {e}")
        return False


def stop_neural():
    """Stop any ongoing neural speech playback."""
    global _stop_flag, _current_playback_process
    _stop_flag = True
    
    # Stop pygame if playing
    if _pygame_available:
        try:
            import pygame
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except:
            pass
    
    # Kill subprocess if running
    if _current_playback_process:
        try:
            _current_playback_process.terminate()
        except:
            pass
        _current_playback_process = None


def is_neural_available() -> bool:
    """Check if neural voice engine is ready."""
    return _edge_tts_available


# ── Emotion-based voice adjustments ──────────────────
# Toned down pitch adjustments so she never sounds childish
EMOTION_VOICES = {
    "happy":    {"rate": "+8%",   "pitch": "+2Hz",  "volume": "+3%"},
    "sad":      {"rate": "-8%",   "pitch": "-3Hz",  "volume": "-5%"},
    "excited":  {"rate": "+12%",  "pitch": "+3Hz",  "volume": "+5%"},
    "calm":     {"rate": "-3%",   "pitch": "-1Hz",  "volume": "-3%"},
    "serious":  {"rate": "-5%",   "pitch": "-3Hz",  "volume": "+0%"},
}

def speak_with_emotion(text: str, emotion: str = "calm") -> bool:
    """Speak with emotion-adjusted voice parameters."""
    global VOICE_RATE, VOICE_PITCH, VOICE_VOLUME
    
    # Save originals
    orig_rate, orig_pitch, orig_vol = VOICE_RATE, VOICE_PITCH, VOICE_VOLUME
    
    # Apply emotion settings
    if emotion in EMOTION_VOICES:
        settings = EMOTION_VOICES[emotion]
        VOICE_RATE = settings["rate"]
        VOICE_PITCH = settings["pitch"]
        VOICE_VOLUME = settings["volume"]
    
    result = speak_neural(text)
    
    # Restore originals
    VOICE_RATE, VOICE_PITCH, VOICE_VOLUME = orig_rate, orig_pitch, orig_vol
    
    return result
