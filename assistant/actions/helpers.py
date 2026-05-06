"""
MAZE — Shared Helpers
Common utility functions used across all action modules.
"""

import re


def contains_any(command: str, words: list) -> bool:
    """Check if command contains any of the words/phrases."""
    return any(w in command for w in words)


def has_word(command: str, words: list) -> bool:
    """Check if command contains any word as a whole word (not substring).
    Use this for short words like 'hi', 'hey', 'yo' that could match inside other words."""
    cmd_words = command.split()
    return any(w in cmd_words for w in words)


def normalize_command(command: str) -> str:
    """Normalize common speech variations."""
    command = command.lower().strip()
    # Fix common speech-to-text issues
    command = command.replace("you tube", "youtube")
    command = command.replace("you too", "youtube")
    command = command.replace("u tube", "youtube")
    command = command.replace("v s code", "vs code")
    command = command.replace("vs court", "vs code")
    command = command.replace("note pad", "notepad")
    command = command.replace("calculater", "calculator")
    # Fix media control mishearings
    command = command.replace("ms next", "next")
    command = command.replace("miss next", "next")
    command = command.replace("previews", "previous")
    command = command.replace("previse", "previous")
    return command


def extract_after(command: str, keywords: list) -> str:
    """Extract text after any of the given keywords."""
    for kw in keywords:
        if kw in command:
            return command.split(kw, 1)[1].strip()
    return ""


def extract_query(command: str, remove_words: set) -> str:
    """Remove keywords as WHOLE WORDS (not substrings) from command."""
    words = command.split()
    filtered = [w for w in words if w not in remove_words]
    return " ".join(filtered).strip()
