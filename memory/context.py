"""Maze — Conversation Memory Module"""
from config import MAX_MEMORY_TURNS

class Memory:
    def __init__(self):
        self._history = []

    def add(self, role: str, content: str):
        """Add a message to memory."""
        self._history.append({"role": role, "content": content})
        # Keep only the last N turns
        if len(self._history) > MAX_MEMORY_TURNS * 2:
            self._history = self._history[-(MAX_MEMORY_TURNS * 2):]

    def get_history(self) -> list:
        """Return the full conversation history."""
        return self._history.copy()

    def clear(self):
        """Clear conversation memory."""
        self._history = []
        return "Memory cleared. Fresh start."

    def summary(self) -> str:
        """Return a short summary of memory status."""
        count = len(self._history)
        return f"I have {count} messages in memory from this session."

# Shared memory instance
memory = Memory()
