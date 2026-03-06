"""
MAZE — Auto-Start Setup
Adds/removes MAZE from Windows startup so it launches when you turn on your PC.

Usage:
    python setup_autostart.py --enable     Add to startup
    python setup_autostart.py --disable    Remove from startup
    python setup_autostart.py --status     Check if enabled
"""

import os
import sys
import winreg

STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "MAZE Voice Assistant"
PYTHON_PATH = sys.executable
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")


def _get_startup_command():
    """Get the command that will run on startup."""
    # Use pythonw.exe for silent startup (no terminal window flash)
    pythonw = PYTHON_PATH.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = PYTHON_PATH  # Fallback to regular python
    return f'"{pythonw}" "{SCRIPT_PATH}"'


def enable_autostart():
    """Add MAZE to Windows startup registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
        command = _get_startup_command()
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print(f"✅ MAZE will now start automatically when you turn on your PC!")
        print(f"   Command: {command}")
        return True
    except Exception as e:
        print(f"❌ Failed to enable auto-start: {e}")
        return False


def disable_autostart():
    """Remove MAZE from Windows startup registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print("✅ MAZE auto-start has been disabled.")
        return True
    except FileNotFoundError:
        print("ℹ️  MAZE was not in startup. Nothing to remove.")
        return True
    except Exception as e:
        print(f"❌ Failed to disable auto-start: {e}")
        return False


def check_status():
    """Check if MAZE is set to auto-start."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"✅ MAZE auto-start is ENABLED")
        print(f"   Command: {value}")
        return True
    except FileNotFoundError:
        print("❌ MAZE auto-start is DISABLED")
        return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("MAZE Auto-Start Setup")
        print("=" * 40)
        print()
        check_status()
        print()
        print("Usage:")
        print("  python setup_autostart.py --enable     Add to startup")
        print("  python setup_autostart.py --disable    Remove from startup")
        print("  python setup_autostart.py --status     Check if enabled")
    elif sys.argv[1] == "--enable":
        enable_autostart()
    elif sys.argv[1] == "--disable":
        disable_autostart()
    elif sys.argv[1] == "--status":
        check_status()
    else:
        print(f"Unknown option: {sys.argv[1]}")
        print("Use --enable, --disable, or --status")
