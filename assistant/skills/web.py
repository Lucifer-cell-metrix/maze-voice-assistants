"""IRON MIND — Skills: Web Search"""
import webbrowser
import urllib.parse

def search_google(query: str) -> str:
    """Open a Google search in the browser."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url)
    return f"Searching Google for: {query}"

def search_youtube(query: str) -> str:
    """Open a YouTube search in the browser."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(url)
    return f"Opening YouTube search for: {query}"

def open_wikipedia(query: str) -> str:
    """Open a Wikipedia page search."""
    encoded = urllib.parse.quote(query)
    url = f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}"
    webbrowser.open(url)
    return f"Opening Wikipedia for: {query}"
