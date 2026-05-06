"""
MAZE — Task Management
Add, show, complete, and clear tasks with persistent storage.
"""

import os
import json
import datetime
from assistant.actions.helpers import contains_any, has_word, extract_after

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS_FILE = os.path.join(_PROJECT_DIR, "memory", "tasks.json")

_tasks = []


def _load_tasks():
    global _tasks
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                _tasks = json.load(f)
    except:
        _tasks = []


def _save_tasks():
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(_tasks, f, indent=2)
    except:
        pass


# Load tasks on import
_load_tasks()


def handle_tasks(command: str) -> str:
    """Handle task management commands."""
    global _tasks

    # Add task
    if contains_any(command, ["add task", "new task", "create task"]):
        task = extract_after(command, ["add task", "new task", "create task"])
        if task:
            _tasks.append({"task": task, "done": False, "time": datetime.datetime.now().isoformat()})
            _save_tasks()
            return f"Task added: {task}. You now have {len([t for t in _tasks if not t['done']])} pending tasks."
        return "What task do you want to add? Say 'add task' followed by the task name."

    # Show tasks
    if (contains_any(command, ["show task", "my task", "list task", "task list", "all task",
                                "show tasks", "my tasks", "list tasks", "pending task",
                                "what are my task", "tasks", "show me task", "show me tasks",
                                "view task", "view tasks"])
        or ("show" in command and "task" in command)
        or ("task" in command and has_word(command, ["show", "list", "view", "see", "all", "my", "pending"]))):
        if not _tasks:
            return "You have no tasks yet. Say 'add task' followed by the task name to add one."
        pending = [t for t in _tasks if not t["done"]]
        done = [t for t in _tasks if t["done"]]
        if not pending:
            return f"All tasks completed! You've finished {len(done)} tasks. Great work!"
        result = f"You have {len(pending)} pending tasks. "
        for i, t in enumerate(pending, 1):
            result += f"Task {i}: {t['task']}. "
        if done:
            result += f"And {len(done)} completed."
        return result

    # Complete task
    if contains_any(command, ["complete task", "done task", "finish task", "mark task"]):
        try:
            num = int(''.join(filter(str.isdigit, command))) - 1
            pending = [t for t in _tasks if not t["done"]]
            if 0 <= num < len(pending):
                pending[num]["done"] = True
                _save_tasks()
                return f"Nice! Task '{pending[num]['task']}' is done. Keep going!"
        except:
            pass
        return "Which task? Say 'complete task 1', 'complete task 2', etc."

    # Clear tasks
    if contains_any(command, ["clear task", "delete task", "remove task",
                               "clear all task", "delete all task"]):
        _tasks.clear()
        _save_tasks()
        return "All tasks cleared. Fresh start."

    return None
