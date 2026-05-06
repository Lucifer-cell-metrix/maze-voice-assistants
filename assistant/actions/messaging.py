"""
MAZE — Messaging & Calling (WhatsApp + Instagram)
"""

import webbrowser
import urllib.parse
from assistant.actions.helpers import contains_any, has_word

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import CONTACTS, INSTAGRAM_USERS


def handle_messaging(command: str) -> str:
    """Handle message requests — search for person on WhatsApp/Instagram."""
    cmd = command.lower()

    # Detect platform
    platform = "whatsapp"
    if "instagram" in cmd or "ig" in cmd or "dm" in cmd:
        platform = "instagram"

    # Extract person name — try contacts first, then use raw name
    target_person = None
    target_phone = None
    target_username = None

    if platform == "whatsapp":
        for name in CONTACTS:
            if name in cmd:
                target_person = name
                target_phone = CONTACTS[name]
                break
    if platform == "instagram" or (not target_person and "instagram" in cmd):
        platform = "instagram"
        for name in INSTAGRAM_USERS:
            if name in cmd:
                target_person = name
                target_username = INSTAGRAM_USERS[name]
                break

    # If not in contacts, extract name from command
    if not target_person:
        name = cmd
        for remove in ["send message to", "send message", "message to", "message",
                        "text to", "text", "dm to", "dm",
                        "on whatsapp", "on instagram", "on ig",
                        "whatsapp", "instagram", "please", "can you", "could you",
                        "find", "send", "to"]:
            name = name.replace(remove, " ")
        target_person = " ".join(name.split()).strip()

    if not target_person:
        return f"Who do you want to message on {platform.title()}?"

    # Extract message content
    message = ""
    if "saying" in cmd:
        message = cmd.split("saying")[1].strip()
    elif "that" in cmd and not cmd.startswith("that"):
        parts = cmd.split("that")
        if len(parts) > 1:
            message = parts[-1].strip()

    # Execute — open the platform to the person
    if platform == "whatsapp":
        if target_phone:
            url = f"https://wa.me/{target_phone.replace('+', '')}"
            if message:
                url += f"?text={urllib.parse.quote(message)}"
            webbrowser.open(url)
            return f"Opening WhatsApp for {target_person.title()}. Send your message there."
        else:
            webbrowser.open("https://web.whatsapp.com")
            return f"Opening WhatsApp. Search for '{target_person.title()}' in the search bar to find them."

    elif platform == "instagram":
        if target_username:
            url = f"https://ig.me/m/{target_username}"
        else:
            url = f"https://www.instagram.com/{target_person.replace(' ', '')}/"
        webbrowser.open(url)
        return f"Opening Instagram for {target_person.title()}."


def handle_calling(command: str) -> str:
    """Handle call requests — open WhatsApp/phone for the person."""
    cmd = command.lower()

    if contains_any(cmd, ["call recent", "recent call", "recent calls", "last call"]):
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp. Your recent chats are on the left side."

    target_person = None
    target_phone = None

    for name in CONTACTS:
        if name in cmd:
            target_person = name
            target_phone = CONTACTS[name]
            break

    if not target_person:
        name = cmd
        for remove in ["call", "phone", "dial", "on whatsapp", "whatsapp",
                        "please", "can you", "could you", "video"]:
            name = name.replace(remove, " ")
        target_person = " ".join(name.split()).strip()

    if not target_person:
        return "Who do you want to call?"

    if target_phone:
        url = f"https://wa.me/{target_phone.replace('+', '')}"
        webbrowser.open(url)
        return f"Opening WhatsApp for {target_person.title()}. Tap the call button to start the call."
    else:
        webbrowser.open("https://web.whatsapp.com")
        return f"Opening WhatsApp. Search for '{target_person.title()}' and tap the call button."
