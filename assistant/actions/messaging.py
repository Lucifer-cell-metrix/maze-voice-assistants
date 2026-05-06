"""
MAZE — Messaging & Calling (WhatsApp + Instagram)
"""

import webbrowser
import urllib.parse
from assistant.actions.helpers import contains_any, has_word

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json


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

    # Load contacts from JSON
    contacts_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory", "contacts.json")
    try:
        with open(contacts_file, "r", encoding="utf-8") as f:
            contacts_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        contacts_data = {"whatsapp": {}, "instagram": {}}

    whatsapp_contacts = contacts_data.get("whatsapp", {})
    instagram_contacts = contacts_data.get("instagram", {})

    if platform == "whatsapp":
        for name in whatsapp_contacts:
            if name in cmd:
                target_person = name
                target_phone = whatsapp_contacts[name]
                break
    if platform == "instagram" or (not target_person and "instagram" in cmd):
        platform = "instagram"
        for name in instagram_contacts:
            if name in cmd:
                target_person = name
                target_username = instagram_contacts[name]
                break

    # Extract message content
    message = ""
    if cmd.startswith("send ") and " to " in cmd:
        part1 = cmd.split("send ", 1)[1]
        msg_part = part1.split(" to ")[0]
        message = msg_part.strip()
        if not target_person:
            person_part = part1.split(" to ", 1)[1]
            for r in ["on whatsapp", "on instagram", "on ig", "whatsapp", "instagram", "please"]:
                person_part = person_part.replace(r, " ")
            target_person = " ".join(person_part.split()).strip()
    elif "saying" in cmd:
        message = cmd.split("saying")[1].strip()
    elif "that" in cmd and not cmd.startswith("that"):
        parts = cmd.split("that")
        if len(parts) > 1:
            message = parts[-1].strip()

    # If not in contacts and not extracted via "send X to Y", extract name from command
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

    # Execute — open the platform to the person
    if platform == "whatsapp":
        if target_phone and message:
            try:
                import pywhatkit as kit
                print(f"   ⏳ Sending WhatsApp message to {target_person.title()}...")
                kit.sendwhatmsg_instantly(
                    phone_no=target_phone,
                    message=message,
                    wait_time=15
                )
                return f"Message sent to {target_person.title()} on WhatsApp."
            except ImportError:
                encoded_msg = urllib.parse.quote(message)
                phone = target_phone.replace('+', '')
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
                webbrowser.open(url)
                return f"WhatsApp opened with message ready to send to {target_person.title()}"
            except Exception as e:
                return f"Failed to send WhatsApp message: {str(e)[:50]}"
        else:
            encoded_msg = urllib.parse.quote(message) if message else ""
            if target_phone:
                phone = target_phone.replace('+', '')
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
                webbrowser.open(url)
                return f"Opening WhatsApp for {target_person.title()}."
            else:
                url = f"https://web.whatsapp.com/send?phone=&text={encoded_msg}"
                webbrowser.open(url)
                return f"I don't have a phone number for '{target_person.title()}' in contacts.json. Opening WhatsApp, please search for them manually to send the message."

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

    # Load contacts from JSON
    contacts_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory", "contacts.json")
    try:
        with open(contacts_file, "r", encoding="utf-8") as f:
            contacts_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        contacts_data = {"whatsapp": {}, "instagram": {}}

    whatsapp_contacts = contacts_data.get("whatsapp", {})

    for name in whatsapp_contacts:
        if name in cmd:
            target_person = name
            target_phone = whatsapp_contacts[name]
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
        phone = target_phone.replace('+', '')
        url = f"https://web.whatsapp.com/send?phone={phone}"
        webbrowser.open(url)
        return f"Opening WhatsApp for {target_person.title()}. Tap the call button to start the call."
    else:
        webbrowser.open("https://web.whatsapp.com")
        return f"Opening WhatsApp. Search for '{target_person.title()}' and tap the call button."
