"""
MAZE — Tool Definitions (Function Calling Schema)
"""

# Gemini-compatible Python function definitions
def open_app(name: str):
    """Open an application or program like chrome, notepad, vscode, calculator, etc."""
    pass

def search_youtube(query: str):
    """Search or play something on YouTube."""
    pass

def search_google(query: str):
    """Search on Google for general queries."""
    pass

def open_website(name: str):
    """Open a known website like github, gmail, spotify, facebook."""
    pass

def play_music(query: str):
    """Play music or a song on YouTube."""
    pass

def set_volume(level: str):
    """Set the system volume. Level can be 'up', 'down', 'mute', or a number 0-100."""
    pass

def set_brightness(level: str):
    """Set the system brightness. Level can be 'up', 'down', or a number 0-100."""
    pass

def add_task(text: str):
    """Add a task to the user's task list."""
    pass

def take_note(text: str):
    """Save a note to the user's notepad."""
    pass

def write_code(description: str):
    """Generate code for a specific task."""
    pass

def call_person(name: str):
    """Call a person (opens WhatsApp)."""
    pass

def send_message(name: str, message: str = ""):
    """Send a message to a person (opens WhatsApp/Instagram)."""
    pass

def find_internship(keyword: str):
    """Find internships on Internshala."""
    pass

def find_file(name: str):
    """Find and open a file on the computer."""
    pass

def chat(text: str):
    """Answer a question, explain something, or have a general conversation (use this as a fallback)."""
    pass

# Gemini tools list
GEMINI_TOOLS = [
    open_app, search_youtube, search_google, open_website, play_music,
    set_volume, set_brightness, add_task, take_note, write_code,
    call_person, send_message, find_internship, find_file, chat
]

# Ollama native tools JSON schema
OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open an application or program like chrome, notepad, vscode, calculator",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the app to open"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search or play something on YouTube",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_google",
            "description": "Search on Google for general queries",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a known website like github, gmail, spotify",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the website to open"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Play music or a song on YouTube",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The song name"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set the system volume",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "description": "up, down, mute, or a number 0-100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Set the system brightness",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "description": "up, down, or a number 0-100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a task to the user's task list",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The task description"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_note",
            "description": "Save a note to the user's notepad",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The note content"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_code",
            "description": "Generate code for a specific task",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "The code description"}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_person",
            "description": "Call a person (opens WhatsApp)",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the person"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a message to a person (opens WhatsApp/Instagram)",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the person"},
                    "message": {"type": "string", "description": "The message content (optional)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_internship",
            "description": "Find internships on Internshala",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "The job role, eg. cybersecurity"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_file",
            "description": "Find and open a file on the computer",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The file name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": "Answer a question, explain something, or have a general conversation",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The user's original query"}
                },
                "required": ["text"]
            }
        }
    }
]
