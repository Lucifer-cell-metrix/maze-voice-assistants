"""
MAZE — Note-Taking
Save, show, and clear notes with timestamp and Notepad integration.
"""

import os
import subprocess
import datetime
from assistant.actions.helpers import contains_any

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTES_FILE = os.path.join(_PROJECT_DIR, "memory", "notes.txt")


def handle_notes(command: str) -> str:
    """Handle note-taking and message typing."""

    # Note down / Write / Type message
    is_note_cmd = contains_any(command, ["note down", "note this", "write down", "write this",
                                "type message", "type this", "take note", "make note",
                                "remember this", "remember that", "save note",
                                "jot down", "write note"])

    # Also match "note [something]" — but NOT "notepad", "show notes", etc.
    if not is_note_cmd and command.startswith("note ") and not contains_any(command, [
            "notepad", "show note", "clear note", "delete note", "my note", "read note", "view note"]):
        is_note_cmd = True

    if is_note_cmd:
        note = command
        for remove in ["note down", "note this", "write down", "write this",
                        "type message", "type this", "take note", "make note",
                        "remember this", "remember that", "save note",
                        "jot down", "write note", "please", "that"]:
            note = note.replace(remove, " ")
        if note.strip().startswith("note "):
            note = note.strip()[5:]
        note = " ".join(note.split()).strip()

        if note:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            try:
                with open(NOTES_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {note}\n")
            except:
                pass
            try:
                subprocess.Popen(["notepad.exe", NOTES_FILE])
            except:
                pass
            return f"Got it. Noted down: {note}. Opening in Notepad."
        return "What do you want me to note down? Say 'note' followed by your message."

    # Show notes
    if contains_any(command, ["show note", "show notes", "my notes", "read notes",
                               "read note", "show my notes", "view notes"]):
        try:
            if os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                if lines:
                    subprocess.Popen(["notepad.exe", NOTES_FILE])
                    count = len(lines)
                    last_note = lines[-1].strip()
                    return f"You have {count} notes. Latest: {last_note}. Opening in Notepad."
                return "No notes yet. Say 'note' followed by your message to start."
            return "No notes yet. Say 'note' followed by your message to start."
        except:
            return "Couldn't read notes file."

    # Clear notes
    if contains_any(command, ["clear notes", "delete notes", "remove notes",
                               "clear all notes", "erase notes"]):
        try:
            if os.path.exists(NOTES_FILE):
                os.remove(NOTES_FILE)
            return "All notes cleared."
        except:
            return "Couldn't clear notes."

    return None
