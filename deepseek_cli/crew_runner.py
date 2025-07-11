from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Optional

from rich.console import Console

from deepseek_cli.agents import (
    PlannerAgent,
    TodoAgent,
    CoderAgent,
    ReviewerAgent,
    FixerAgent,
)
from deepseek_cli.tools.file_tools import write_text_to_file
from deepseek_cli.tools.todo_writer import save_todo_markdown

console = Console()


class CrewRunner:
    """Coordinates the execution flow of all agents depending on CLI options.

    Eğer `save_path` parametresi verilmezse çalışılan dizine, prompt'a dayalı
    otomatik bir dosya adı (.py uzantılı) oluşturulur.
    """

    def __init__(
        self,
        prompt: str,
        save_path: Optional[str] = None,
        plan: bool = False,
    ) -> None:
        self.prompt = prompt
        self.explicit_save = save_path is not None
        self.save_path = save_path or self._generate_default_filename()
        self.plan_enabled = plan

        # initialize agents lazily only when needed
        self._planner = PlannerAgent()
        self._todoer = TodoAgent()
        self._coder = CoderAgent()
        self._reviewer = ReviewerAgent()
        self._fixer = FixerAgent()

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    @staticmethod
    def _sanitize(text: str, max_words: int = 6) -> str:
        """Return a filesystem-safe slug from user prompt."""
        # keep alnum and underscore, convert spaces to underscore
        words = re.split(r"\s+", text.strip())[:max_words]
        rough = "_".join(words)
        slug = re.sub(r"[^A-Za-z0-9_]+", "", rough)
        return slug or "generated_code"

    def _generate_default_filename(self) -> str:
        cwd = Path(os.getcwd())
        slug = self._sanitize(self.prompt)
        filename = f"{slug}.py"
        path = cwd / filename
        # ensure uniqueness to prevent overwrite
        counter = 1
        while path.exists():
            path = cwd / f"{slug}_{counter}.py"
            counter += 1
        return str(path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Execute the requested actions and print results to the console."""
        console.rule("[bold cyan]Crew Runner Başladı")

        if self.plan_enabled:
            console.print("[yellow]📝 Generating plan...")
            plan_output = self._planner.run(self.prompt)
            console.print(plan_output)
        else:
            plan_output = ""

        console.print("[green]📋 Generating TODO list...")
        todo_output = self._todoer.run(self.prompt)
        console.print(todo_output)
        save_todo_markdown(todo_output)

        console.print("[magenta]💻 Generating code...")
        raw_code = self._coder.run(self.prompt)
        console.print(raw_code)

        console.print("[blue]🔍 Reviewing code...")
        review_notes = self._reviewer.run(raw_code)
        console.print(review_notes)

        console.print("[green]🛠️  Applying fixes...")
        fixed_code = self._fixer.run(raw_code, review_notes)
        console.print(fixed_code)

        if self.explicit_save:
            write_text_to_file(self.save_path, fixed_code)
            console.print(f"[bold green]Code saved to {self.save_path}.")
        else:
            console.print(f"[yellow]Code not saved yet. Suggested file: {self.save_path}")

        console.rule("[bold cyan]Crew Runner completed")

        # return fixed code and suggested path so that CLI can decide to save
        return fixed_code, self.save_path 