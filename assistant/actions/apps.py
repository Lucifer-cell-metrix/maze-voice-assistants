"""
MAZE — Application Launcher + OS-Wide File/App Finder
Opens apps by name, and scans C:/ and D:/ drives to find executables.
"""

import os
import subprocess
import webbrowser
import json
import time
import threading
from assistant.actions.helpers import has_word

# ── Known Application Registry ──────────────────────────
APPS = {
    "notepad":         "notepad.exe",
    "calculator":      "calc.exe",
    "open calculator": "calc.exe",
    "open calc":       "calc.exe",
    "paint":           "mspaint.exe",
    "explorer":        "explorer.exe",
    "file explorer":   "explorer.exe",
    "files":           "explorer.exe",
    "task manager":    "taskmgr.exe",
    "cmd":             "cmd.exe",
    "command prompt":  "cmd.exe",
    "terminal":        "cmd.exe",
    "powershell":      "powershell.exe",
    "settings":        "ms-settings:",
    "vs code":         "code",
    "vscode":          "code",
    "visual studio":   "code",
    "snipping tool":   "snippingtool.exe",
    "screenshot":      "snippingtool.exe",
    "snip":            "snippingtool.exe",
    "word":            "winword.exe",
    "excel":           "excel.exe",
    "powerpoint":      "powerpnt.exe",
    "outlook":         "outlook.exe",
    "photos":          "ms-photos:",
    "camera":          "microsoft.windows.camera:",
    "clock":           "ms-clock:",
    "calendar":        "outlookcal:",
    "maps":            "bingmaps:",
    "store":           "ms-windows-store:",
    "xbox":            "xbox:",
}

# Browser paths to try on Windows
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]

BRAVE_PATHS = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
]

BROWSER_APPS = {
    "chrome":        CHROME_PATHS,
    "google chrome": CHROME_PATHS,
    "brave":         BRAVE_PATHS,
    "edge":          ["msedge.exe"],
    "microsoft edge":["msedge.exe"],
    "firefox":       ["firefox.exe"],
    "browser":       CHROME_PATHS,  # Default to Chrome
}


# ── OS-Wide App/File Index (cached) ──────────────────────
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_APP_INDEX_FILE = os.path.join(_PROJECT_DIR, "memory", "app_index.json")
_app_index = {}  # {name_lower: full_path}
_index_loaded = False
_index_lock = threading.Lock()

# Directories to SKIP when scanning (speeds up scan dramatically)
_SKIP_DIRS = {
    "windows", "winsxs", "$recycle.bin", "system volume information",
    "programdata", "recovery", "perflogs", "msocache",
    "$windows.~bt", "$windows.~ws", "windows.old",
    "node_modules", ".git", "__pycache__", "venv", ".venv",
    "appdata", "temp", "tmp",
}

# File extensions to index
_INDEX_EXTENSIONS = {".exe", ".lnk", ".msi"}


def _build_app_index():
    """Scan C:/ and D:/ for executable files and cache the results."""
    global _app_index, _index_loaded
    index = {}
    drives = []
    for letter in ["C", "D", "E"]:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)

    # Key directories to scan (fast, high-value)
    scan_dirs = []
    for drive in drives:
        scan_dirs.extend([
            os.path.join(drive, "Program Files"),
            os.path.join(drive, "Program Files (x86)"),
            os.path.join(drive, "Users"),
        ])
        # Also scan top-level folders on D: and E: (user files)
        if drive != "C:\\":
            try:
                for item in os.listdir(drive):
                    full = os.path.join(drive, item)
                    if os.path.isdir(full) and item.lower() not in _SKIP_DIRS:
                        scan_dirs.append(full)
            except PermissionError:
                pass

    # Start Menu shortcuts (high value!)
    start_menu_paths = [
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    ]
    scan_dirs.extend(start_menu_paths)

    for base_dir in scan_dirs:
        if not os.path.exists(base_dir):
            continue
        try:
            for root, dirs, files in os.walk(base_dir, topdown=True):
                # Skip known junk directories
                dirs[:] = [d for d in dirs if d.lower() not in _SKIP_DIRS]

                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in _INDEX_EXTENSIONS:
                        name = os.path.splitext(f)[0].lower()
                        full_path = os.path.join(root, f)
                        # Don't overwrite — prefer Start Menu shortcuts
                        if name not in index:
                            index[name] = full_path
        except (PermissionError, OSError):
            continue

    with _index_lock:
        _app_index = index
        _index_loaded = True

    # Save to cache file
    try:
        with open(_APP_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "apps": index}, f)
    except:
        pass

    print(f"   📂 App index built: {len(index)} applications found.")


def _load_app_index():
    """Load cached index from file, or build fresh in background."""
    global _app_index, _index_loaded
    try:
        if os.path.exists(_APP_INDEX_FILE):
            with open(_APP_INDEX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            age = time.time() - data.get("timestamp", 0)
            if age < 86400:  # Less than 24 hours old
                with _index_lock:
                    _app_index = data.get("apps", {})
                    _index_loaded = True
                print(f"   📂 App index loaded from cache: {len(_app_index)} apps.")
                return
    except:
        pass

    # Build index in background thread (non-blocking)
    thread = threading.Thread(target=_build_app_index, daemon=True)
    thread.start()


def _find_in_index(query: str) -> str:
    """Search the app index for a matching application. Returns path or None."""
    if not _index_loaded:
        return None

    query_lower = query.lower().strip()
    with _index_lock:
        # Exact match
        if query_lower in _app_index:
            return _app_index[query_lower]

        # Partial match — find closest
        best_match = None
        best_score = 0
        for name, path in _app_index.items():
            if query_lower in name:
                score = len(query_lower) / len(name)  # Prefer exact-length matches
                if score > best_score:
                    best_score = score
                    best_match = path
            elif name in query_lower:
                score = len(name) / len(query_lower) * 0.8
                if score > best_score:
                    best_score = score
                    best_match = path

    return best_match


def open_app(app_name: str) -> str:
    """Open a system application by name.
    Priority: known apps → browsers → OS-wide file index."""
    app_name = app_name.lower().strip()

    # Check if it's a browser request
    for browser_name, paths in BROWSER_APPS.items():
        if browser_name in app_name:
            for path in paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return f"Opening {browser_name.title()} for you."
            # Try with shell=True as fallback
            try:
                subprocess.Popen(paths[-1], shell=True)
                return f"Opening {browser_name.title()} for you."
            except:
                pass
            # Final fallback — default browser
            webbrowser.open("https://www.google.com")
            return f"{browser_name.title()} not found. Opening default browser."

    # Check regular apps — use whole word matching to avoid 'calc' in 'calculate'
    for key, exe in APPS.items():
        # For short words like 'calc', check as whole word
        if len(key) <= 4:
            if has_word(app_name, [key]):
                try:
                    if ":" in exe:
                        os.startfile(exe)
                    else:
                        subprocess.Popen(exe, shell=True)
                    return f"Opening {key.title()} for you."
                except Exception as e:
                    return f"Couldn't open {key.title()}. Error: {str(e)}"
        else:
            if key in app_name:
                try:
                    # Use startfile for protocols (ms-settings:, tg://, etc.) or executables
                    if ":" in exe:
                        os.startfile(exe)
                    else:
                        subprocess.Popen(exe, shell=True)
                    return f"Opening {key.title()} for you."
                except Exception as e:
                    return f"Couldn't open {key.title()}. Error: {str(e)}"

    # ── OS-Wide Search — scan C: and D: for the app ──
    found_path = _find_in_index(app_name)
    if found_path:
        try:
            ext = os.path.splitext(found_path)[1].lower()
            if ext == ".lnk":
                os.startfile(found_path)
            elif ext == ".exe":
                subprocess.Popen([found_path])
            else:
                os.startfile(found_path)
            app_display = os.path.splitext(os.path.basename(found_path))[0]
            return f"Found and opening {app_display} from your system."
        except Exception as e:
            return f"Found {os.path.basename(found_path)} but couldn't open it. Error: {str(e)}"

    return None


def find_file(query: str) -> str:
    """Search for a file on the system by name.
    Scans common directories on C: and D: drives."""
    query_lower = query.lower().strip()
    results = []

    # Quick search in common user directories
    search_dirs = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Pictures"),
        os.path.expanduser("~\\Videos"),
        os.path.expanduser("~\\Music"),
    ]
    # Add D: drive top-level folders
    if os.path.exists("D:\\"):
        try:
            for item in os.listdir("D:\\"):
                full = os.path.join("D:\\", item)
                if os.path.isdir(full):
                    search_dirs.append(full)
        except:
            pass

    for base in search_dirs:
        if not os.path.exists(base):
            continue
        try:
            for root, dirs, files in os.walk(base, topdown=True):
                # Limit depth to 3 levels
                depth = root.replace(base, "").count(os.sep)
                if depth >= 3:
                    dirs[:] = []
                    continue
                dirs[:] = [d for d in dirs if d.lower() not in _SKIP_DIRS]

                for f in files:
                    if query_lower in f.lower():
                        results.append(os.path.join(root, f))
                        if len(results) >= 5:
                            break
                if len(results) >= 5:
                    break
        except (PermissionError, OSError):
            continue
        if len(results) >= 5:
            break

    if results:
        # Open the first result
        first = results[0]
        try:
            os.startfile(first)
        except:
            pass

        if len(results) == 1:
            return f"Found and opening: {os.path.basename(first)}"
        else:
            names = [os.path.basename(r) for r in results[:5]]
            return f"Found {len(results)} matches. Opening {names[0]}. Others: {', '.join(names[1:])}"
    return f"I couldn't find any file matching '{query}' on your system."


# Initialize the app index on import
_load_app_index()
