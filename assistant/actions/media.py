"""
MAZE — Media Controls (YouTube playlist, play/pause, next/prev)
"""

import re
import ctypes
import time
import webbrowser
import urllib.parse
from assistant.actions.helpers import contains_any, has_word, extract_query

# ── YouTube Playlist Tracking ────────────────────────
_yt_playlist = []          # List of video IDs from last search
_yt_current_idx = -1       # Current video index in the playlist
_yt_last_query = ""        # What was searched

# Words to remove from YouTube query (as WHOLE WORDS only)
YT_REMOVE_WORDS = {"open", "youtube", "search", "play", "on", "and", "in",
                    "find", "for", "video", "the", "a", "me", "show",
                    "you", "tube", "please", "song", "music"}

# ── System Key Constants ─────────────────────────────
VK_VOLUME_UP   = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD
VK_MEDIA_NEXT  = 0xB0
VK_MEDIA_PREV  = 0xB1
VK_MEDIA_STOP  = 0xB2
VK_MEDIA_PLAY  = 0xB3


def _press_key(vk_code):
    """Simulate a key press using Windows API."""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)


def play_on_youtube(query: str) -> str:
    """Find YouTube videos for query, play first one, save results for next/prev."""
    global _yt_playlist, _yt_current_idx, _yt_last_query
    try:
        import requests as req
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = req.get(search_url, headers=headers, timeout=5)
        raw_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', response.text)
        seen = set()
        unique_ids = []
        for vid in raw_ids:
            if vid not in seen:
                seen.add(vid)
                unique_ids.append(vid)
        if unique_ids:
            _yt_playlist = unique_ids[:20]
            _yt_current_idx = 0
            _yt_last_query = query
            video_url = f"https://www.youtube.com/watch?v={unique_ids[0]}"
            webbrowser.open(video_url)
            return f"Playing {query} on YouTube. {len(unique_ids)} tracks in queue."
    except:
        pass
    _yt_playlist = []
    _yt_current_idx = -1
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Searching {query} on YouTube."


def handle_media_control(command: str) -> str:
    """Handle media playback controls (next, previous, pause, stop).
    Uses YouTube playlist for next/prev, media keys for pause/play."""
    global _yt_current_idx

    cmd = command
    for filler in [" the ", " a ", " my ", " please "]:
        cmd = cmd.replace(filler, " ")
    cmd = " ".join(cmd.split()).strip()

    # Fix speech-to-text mishearings
    cmd = cmd.replace("ms next", "next")
    cmd = cmd.replace("am next", "next")
    cmd = cmd.replace("and next", "next")
    cmd = cmd.replace("is next", "next")
    cmd = cmd.replace("miss next", "next")

    # ── Next Track ──
    if contains_any(cmd, ["next track", "next song", "next music",
                          "skip track", "skip song", "skip this"]) \
       or cmd.strip() in ["next", "skip"]:
        if _yt_playlist and _yt_current_idx < len(_yt_playlist) - 1:
            _yt_current_idx += 1
            video_url = f"https://www.youtube.com/watch?v={_yt_playlist[_yt_current_idx]}"
            webbrowser.open(video_url)
            remaining = len(_yt_playlist) - _yt_current_idx - 1
            return f"Playing next track. {remaining} more in queue."
        elif _yt_playlist and _yt_current_idx >= len(_yt_playlist) - 1:
            return "That was the last track in the queue. Say 'play' followed by a song name to start fresh."
        else:
            _press_key(VK_MEDIA_NEXT)
            return "Skipping to next track."

    # ── Previous Track ──
    if contains_any(cmd, ["previous track", "previous song", "previous music",
                          "last track", "last song", "go back track",
                          "prev track", "prev song"]) \
       or cmd.strip() in ["previous", "prev", "go back"]:
        if _yt_playlist and _yt_current_idx > 0:
            _yt_current_idx -= 1
            video_url = f"https://www.youtube.com/watch?v={_yt_playlist[_yt_current_idx]}"
            webbrowser.open(video_url)
            return "Playing previous track."
        elif _yt_playlist and _yt_current_idx <= 0:
            return "Already at the first track. No previous track available."
        else:
            _press_key(VK_MEDIA_PREV)
            return "Going to previous track."

    # ── Pause / Resume ──
    if contains_any(cmd, ["pause music", "pause song", "pause track",
                          "resume music", "resume song", "resume track",
                          "pause media", "resume media", "pause play",
                          "play pause", "toggle pause"]) \
       or cmd.strip() in ["pause", "resume", "unpause"]:
        _press_key(VK_MEDIA_PLAY)
        return "Toggled play/pause."

    # ── Stop ──
    if contains_any(cmd, ["stop music", "stop song", "stop track",
                          "stop playing", "stop media"]):
        _press_key(VK_MEDIA_STOP)
        return "Stopping playback."

    return None
