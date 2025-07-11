from __future__ import annotations

from pathlib import Path
from typing import List

from .file_tools import write_text_to_file


DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TODO_FILE = DATA_DIR / "todo.md"


def save_todo_markdown(todo_markdown: str) -> Path:
    """Save the given TODO markdown to the project's data/todo.md file.

    Returns the Path to the saved file for convenience.
    """
    write_text_to_file(TODO_FILE, todo_markdown)
    return TODO_FILE


def append_todo_items(items: List[str]) -> Path:
    """Append new TODO items to the existing todo.md file."""
    if TODO_FILE.exists():
        existing = TODO_FILE.read_text(encoding="utf-8")
    else:
        existing = ""
    new_markdown = "\n".join(f"- [ ] {item}" for item in items)
    combined = f"{existing}\n{new_markdown}" if existing else new_markdown
    write_text_to_file(TODO_FILE, combined)
    return TODO_FILE 