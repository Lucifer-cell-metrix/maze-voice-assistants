"""
MAZE — Web Search & Website Opener
Handles Google, YouTube, Wikipedia searches and opening known websites.
"""

import os
import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from assistant.actions.helpers import contains_any, has_word, extract_query
from assistant.actions.media import play_on_youtube, YT_REMOVE_WORDS

# ── Known Websites ───────────────────────────────────
WEBSITES = {
    # Developer
    "github":          "https://github.com",
    "stackoverflow":   "https://stackoverflow.com",
    "stack overflow":   "https://stackoverflow.com",
    # Email & Communication
    "gmail":           "https://mail.google.com",
    "email":           "https://mail.google.com",
    "mail":            "https://mail.google.com",
    "whatsapp":        "https://web.whatsapp.com",
    "telegram":        "https://web.telegram.org",
    "discord":         "https://discord.com/app",
    # Social Media
    "instagram":       "https://instagram.com",
    "twitter":         "https://twitter.com",
    "linkedin":        "https://linkedin.com",
    "facebook":        "https://facebook.com",
    "reddit":          "https://reddit.com",
    "pinterest":       "https://pinterest.com",
    "snapchat":        "https://web.snapchat.com",
    "threads":         "https://threads.net",
    # AI Tools
    "chatgpt":         "https://chat.openai.com",
    "gemini":          "https://gemini.google.com",
    "claude":          "https://claude.ai",
    # Entertainment
    "spotify":         "https://open.spotify.com",
    "netflix":         "https://netflix.com",
    "hotstar":         "https://hotstar.com",
    "prime video":     "https://primevideo.com",
    "amazon prime":    "https://primevideo.com",
    # Shopping
    "amazon":          "https://amazon.in",
    "flipkart":        "https://flipkart.com",
    "myntra":          "https://myntra.com",
    # Productivity
    "google drive":    "https://drive.google.com",
    "google docs":     "https://docs.google.com",
    "notion":          "https://notion.so",
    "canva":           "https://canva.com",
    "figma":           "https://figma.com",
    # Learning
    "udemy":           "https://udemy.com",
    "coursera":        "https://coursera.org",
    "geeksforgeeks":   "https://geeksforgeeks.org",
    "leetcode":        "https://leetcode.com",
    "w3schools":       "https://w3schools.com",
    # Jobs & Internships
    "internshala":     "https://internshala.com",
    "naukri":          "https://naukri.com",
    "linkedin jobs":   "https://linkedin.com/jobs",
}

# Desktop app protocols — try native app before browser
APP_PROTOCOLS = {
    "whatsapp": "whatsapp://",
    "discord": "discord://",
    "spotify": "spotify:",
    "netflix": "netflix:",
    "instagram": "instagram://",
    "twitter": "twitter://",
    "telegram": "tg://",
    "notion": "notion://",
    "figma": "figma://",
    "canva": "canva-desktop://",
}


def open_website(command: str) -> str:
    """Open a known website (tries desktop app first, falls back to browser)."""
    for key, url in WEBSITES.items():
        if key in command:
            # Try to open the desktop app first
            if key in APP_PROTOCOLS:
                try:
                    os.startfile(APP_PROTOCOLS[key])
                    return f"Opening {key.title()} app."
                except Exception:
                    pass  # Fall back to opening the website

            webbrowser.open(url)
            return f"Opening {key.title()} in browser."
    return None


def handle_search(command: str) -> str:
    """Handle search commands. YouTube gets priority when mentioned."""

    # ── YouTube (if "youtube" is in command) ──
    if "youtube" in command:
        query = extract_query(command, YT_REMOVE_WORDS)
        if query:
            if has_word(command, ["play"]):
                return play_on_youtube(query)
            else:
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                webbrowser.open(url)
                return f"Searching {query} on YouTube."
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."

    # ── "Play X" = Auto-play on YouTube ──
    if command.startswith("play ") or " play " in command:
        query = extract_query(command, YT_REMOVE_WORDS | {"play"})
        if query:
            return play_on_youtube(query)
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube. What do you want to play?"

    # ── Wikipedia search ──
    if contains_any(command, ["wikipedia", "wiki"]):
        wiki_remove = {"wikipedia", "wiki", "search", "open", "on", "about", "for", "the"}
        query = extract_query(command, wiki_remove)
        if query:
            url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Opening Wikipedia for: {query}"
        return "What should I look up on Wikipedia?"

    # ── Google search (default) ──
    if contains_any(command, ["search", "google", "look up", "find"]):
        google_remove = {"search", "google", "look", "up", "find", "for", "about", "open", "the"}
        query = extract_query(command, google_remove)
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching Google for: {query}"
        return "What would you like me to search for?"

    return None

def web_search(query):
    """Search web and return summary"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                return results[0]['body']
            return "No results found"
    except Exception as e:
        return f"Search failed: {str(e)}"

def fetch_webpage(url):
    """Fetch and read any webpage"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, 
                               headers=headers, 
                               timeout=10)
        soup = BeautifulSoup(response.content, 
                            "html.parser")
        
        # Remove scripts and styles
        for tag in soup(["script", "style"]):
            tag.decompose()
            
        text = soup.get_text(separator=' ')
        # Clean whitespace
        lines = [l.strip() for l in text.splitlines() 
                 if l.strip()]
        return ' '.join(lines)[:1000]
    except Exception as e:
        return f"Could not fetch page: {str(e)}"
