"""IRON MIND — Skills: File Management"""
import os
import shutil
from pathlib import Path

def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    try:
        files = os.listdir(directory)
        if not files:
            return f"The folder '{directory}' is empty."
        return f"Files in {directory}: " + ", ".join(files)
    except FileNotFoundError:
        return f"Directory '{directory}' not found."

def create_folder(folder_name: str, location: str = ".") -> str:
    """Create a new folder."""
    path = os.path.join(location, folder_name)
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder '{folder_name}' created successfully."
    except Exception as e:
        return f"Could not create folder: {str(e)}"

def search_file(filename: str, search_dir: str = ".") -> str:
    """Search for a file by name."""
    matches = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if filename.lower() in file.lower():
                matches.append(os.path.join(root, file))
    if matches:
        return f"Found {len(matches)} file(s): " + ", ".join(matches[:5])
    return f"No files matching '{filename}' found."

def delete_file(filepath: str) -> str:
    """Delete a file with confirmation check."""
    if not os.path.exists(filepath):
        return f"File '{filepath}' does not exist."
    os.remove(filepath)
    return f"File '{filepath}' deleted successfully."
