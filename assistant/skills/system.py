"""IRON MIND — Skills: System Control"""
import subprocess
import webbrowser
import datetime

def open_website(url: str) -> str:
    """Open a URL in the default browser."""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url} in your browser."

def open_application(app_name: str) -> str:
    """Open a system application by name."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "chrome": "chrome.exe",
        "vs code": "code",
        "spotify": "spotify.exe",
    }
    app = apps.get(app_name.lower())
    if app:
        try:
            subprocess.Popen(app)
            return f"Opening {app_name}."
        except Exception as e:
            return f"Could not open {app_name}: {str(e)}"
    return f"I don't have '{app_name}' in my app list yet."

def get_time() -> str:
    """Return current time as a string."""
    now = datetime.datetime.now()
    return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

def get_date() -> str:
    """Return today's date."""
    return datetime.datetime.now().strftime("Today is %A, %B %d, %Y.")
