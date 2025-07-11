from __future__ import annotations

import os
from pathlib import Path
from typing import Union


def write_text_to_file(path: Union[str, Path], content: str) -> None:
    """Create or overwrite a text file with the given content.

    Parameters
    ----------
    path : Union[str, Path]
        Destination file path.
    content : str
        Content to be written.
    """
    path = Path(path)
    # ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_text_to_file(path: Union[str, Path], content: str) -> None:
    """Append text to a file, creating it if necessary."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(content) 