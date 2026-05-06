"""
MAZE — Code Generation
Generate code using AI and save to files.
"""

import os
import re
import subprocess

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import AI_PROVIDER, GEMINI_API_KEY

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_DIR = os.path.join(_PROJECT_DIR, "generated_code")


def handle_code_writing(command: str) -> str:
    """Generate code using AI and save to a file."""
    if not (AI_PROVIDER in ("gemini", "ollama") and (AI_PROVIDER != "gemini" or GEMINI_API_KEY)):
        return "I need the Gemini AI or Ollama connection to write code. Please check your settings."

    # Extract what code to write
    code_request = command
    for remove in ["write code", "write a code", "create code", "create a code",
                    "code for", "generate code", "make code", "make a code",
                    "write program", "write a program", "create program",
                    "write script", "write a script", "create script",
                    "for me", "please", "that"]:
        code_request = code_request.replace(remove, " ")
    code_request = " ".join(code_request.split()).strip()

    if not code_request:
        return "What code do you want me to write? Say 'write code for' followed by what you need."

    try:
        prompt = (
            f"Write clean, well-commented code for: {code_request}. "
            "Provide ONLY the code, no explanations before or after. "
            "Include comments in the code to explain what each part does. "
            "Detect the best programming language for this task. "
            "Start the first line with a comment indicating the language, e.g. # Python or // JavaScript"
        )

        lang_line = ""
        if AI_PROVIDER == "ollama":
            from assistant.ai_providers.ollama import ask_llm
            response_text = ask_llm(prompt, timeout=60)
        else:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "max_output_tokens": 2000,
                    "temperature": 0.3,
                }
            )
            response_text = response.text

        code = response_text.strip()
        if code.startswith("```"):
            lines = code.split("\n")
            lang_line = lines[0].replace("```", "").strip()
            code = "\n".join(lines[1:])
            if code.endswith("```"):
                code = code[:-3].strip()

        ext_map = {
            "python": ".py", "javascript": ".js", "java": ".java",
            "c++": ".cpp", "cpp": ".cpp", "c": ".c", "html": ".html",
            "css": ".css", "rust": ".rs", "go": ".go", "ruby": ".rb",
            "php": ".php", "typescript": ".ts", "bash": ".sh",
            "shell": ".sh", "sql": ".sql", "swift": ".swift",
            "kotlin": ".kt", "r": ".r",
        }
        ext = ".py"
        first_line = code.split("\n")[0].lower() if code else ""
        for lang, e in ext_map.items():
            if lang in first_line or (lang_line and lang in lang_line.lower()):
                ext = e
                break

        os.makedirs(CODE_DIR, exist_ok=True)
        safe_name = re.sub(r'[^\w\s-]', '', code_request)[:40].strip().replace(' ', '_')
        filename = f"{safe_name}{ext}"
        filepath = os.path.join(CODE_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            subprocess.Popen(["code", filepath], shell=True)
        except:
            try:
                subprocess.Popen(["notepad.exe", filepath])
            except:
                pass

        return f"Done! I wrote {code_request} code and saved it as {filename}. Opening it now."

    except Exception as e:
        return f"Sorry, I couldn't generate code right now. Error: {str(e)[:60]}"
