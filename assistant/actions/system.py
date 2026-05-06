"""
MAZE — System Controls (Volume & Brightness)
"""

import ctypes
import re
import time
from assistant.actions.helpers import contains_any
import subprocess

# ── Key Constants ────────────────────────────────────
VK_VOLUME_UP   = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD


def _press_key(vk_code):
    """Simulate a key press using Windows API."""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)


def volume_up(steps=5):
    for _ in range(steps):
        _press_key(VK_VOLUME_UP)
        time.sleep(0.05)


def volume_down(steps=5):
    for _ in range(steps):
        _press_key(VK_VOLUME_DOWN)
        time.sleep(0.05)


def volume_mute():
    _press_key(VK_VOLUME_MUTE)


def get_brightness():
    """Get current screen brightness (0-100)."""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            capture_output=True, text=True, timeout=5
        )
        return int(result.stdout.strip())
    except:
        return -1


def set_brightness(level):
    """Set screen brightness (0-100)."""
    level = max(0, min(100, level))
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"],
            capture_output=True, text=True, timeout=5
        )
        return level
    except:
        return -1


def handle_system_control(command: str) -> str:
    """Handle volume and brightness control."""
    # Strip filler words
    for filler in [" the ", " a ", " my ", " please "]:
        command = command.replace(filler, " ")
    command = " ".join(command.split())

    # ── Volume Controls ──
    if contains_any(command, ["volume up", "increase volume", "louder",
                               "turn up volume", "raise volume", "sound up",
                               "volume increase", "volume high", "volume higher"]):
        volume_up(5)
        return "Volume increased."

    if contains_any(command, ["volume down", "decrease volume", "quieter", "softer",
                               "turn down volume", "lower volume", "sound down",
                               "volume decrease", "volume low", "volume lower"]):
        volume_down(5)
        return "Volume decreased."

    if contains_any(command, ["mute", "unmute", "silence", "toggle mute",
                               "mute volume", "volume mute", "shut up volume"]):
        volume_mute()
        return "Volume muted. Say mute again to unmute."

    if contains_any(command, ["full volume", "max volume", "maximum volume",
                               "volume max", "volume full", "volume 100"]):
        volume_up(50)
        return "Volume set to maximum."

    if contains_any(command, ["minimum volume", "volume minimum", "volume zero",
                               "volume 0", "no volume", "silent"]):
        volume_down(50)
        return "Volume set to minimum."

    # ── Brightness Controls ──
    if contains_any(command, ["brightness up", "increase brightness", "brighter",
                               "screen brighter", "turn up brightness",
                               "brightness increase", "brightness high", "brightness higher",
                               "more brightness", "bright up"]):
        current = get_brightness()
        if current >= 0:
            new = min(100, current + 20)
            set_brightness(new)
            return f"Brightness increased to {new} percent."
        return "Brightness increased."

    if contains_any(command, ["brightness down", "decrease brightness", "dimmer",
                               "screen dimmer", "turn down brightness", "dim",
                               "brightness decrease", "brightness low", "brightness lower",
                               "less brightness", "bright down"]):
        current = get_brightness()
        if current >= 0:
            new = max(0, current - 20)
            set_brightness(new)
            return f"Brightness decreased to {new} percent."
        return "Brightness decreased."

    if contains_any(command, ["full brightness", "max brightness", "maximum brightness",
                               "brightness max", "brightness full", "brightness 100"]):
        set_brightness(100)
        return "Brightness set to maximum."

    if contains_any(command, ["minimum brightness", "lowest brightness",
                               "brightness minimum", "brightness zero", "brightness 0"]):
        set_brightness(10)
        return "Brightness set to minimum."

    # Specific percentage: "set brightness to 50"
    if "brightness" in command:
        try:
            nums = re.findall(r'\d+', command)
            if nums:
                level = int(nums[0])
                if 0 <= level <= 100:
                    set_brightness(level)
                    return f"Brightness set to {level} percent."
        except:
            pass

    # Specific volume percentage: "set volume to 50"
    if "volume" in command:
        try:
            nums = re.findall(r'\d+', command)
            if nums:
                level = int(nums[0])
                if 0 <= level <= 100:
                    volume_down(50)
                    steps = level // 2
                    volume_up(steps)
                    return f"Volume set to approximately {level} percent."
        except:
            pass

    return None
