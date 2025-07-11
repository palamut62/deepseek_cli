from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Optional

import subprocess
import tempfile
import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
import click

from deepseek_cli.agents import (
    PlannerAgent,
    TodoAgent,
    CoderAgent,
    ReviewerAgent,
    FixerAgent,
    TestAgent,
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
        self._tester = TestAgent()

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

    def _strip(self, code: str) -> str:
        """Remove markdown code block markers if present."""
        import re as _re
        code = _re.sub(r'^```(?:\w+)?\s*\n?', '', code.strip())
        code = _re.sub(r'\n?```$', '', code)
        return code.strip()

    # helper to run with spinner
    def _run_step(self, msg: str, func, *args):
        with Progress(SpinnerColumn(), "[bold blue]" + msg + "...", TimeElapsedColumn(), transient=True) as progress:
            task = progress.add_task("run")
            result = func(*args)
            progress.update(task, completed=1)
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Execute the requested actions and print results to the console."""
        console.rule("[bold cyan]Crew Runner Başladı")

        if self.plan_enabled:
            plan_output = self._run_step("📝 Plan", self._planner.run, self.prompt)
            console.print(plan_output)
        else:
            plan_output = ""

        todo_output = self._run_step("📋 TODO list", self._todoer.run, self.prompt)
        console.print(todo_output)
        save_todo_markdown(todo_output)

        raw_code = self._run_step("💻 Code", self._coder.run, self.prompt)
        raw_code = self._strip(raw_code)
        console.print(raw_code)

        review_notes = self._run_step("🔍 Review", self._reviewer.run, raw_code)
        console.print(review_notes)

        fixed_code = self._run_step("🛠️ Fix", self._fixer.run, raw_code, review_notes)
        fixed_code = self._strip(fixed_code)
        console.print(fixed_code)

        # -----------------------------------------------------------------
        # Testing phase
        # -----------------------------------------------------------------
        test_code_raw = self._run_step("🧪 Tests", self._tester.run, fixed_code)
        test_code = self._strip(test_code_raw)

        console.print(test_code)

        # run tests with up to 3 attempts
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                main_path = Path(tmpdir) / "main.py"
                test_path = Path(tmpdir) / "test_main.py"
                main_path.write_text(fixed_code, encoding="utf-8")
                test_path.write_text(test_code, encoding="utf-8")
            except IOError as e:
                console.print(f"[red]Dosya yazma hatası: {e}")
                raise

            attempts = 0
            while attempts < 3:
                result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=tmpdir, capture_output=True, text=True)

                if result.returncode == 0:
                    console.print("[bold green]✅ Birim testleri geçti.")
                    break

                console.print("[red]❌ Birim testleri başarısız oldu.")
                console.print(result.stdout + result.stderr)

                choice = click.prompt(
                    "Ne yapmak istersiniz? [a]utomatik düzelt / [m]anuel düzelt / [q]uit",
                    type=click.Choice(["a", "m", "q"], case_sensitive=False),
                    default="a",
                )

                if choice == "q":
                    console.print("[yellow]Çıkış yapılıyor.")
                    raise SystemExit(1)

                if choice == "a":
                    console.print("[cyan]🤖 Fixer otomatik düzeltme uyguluyor...")
                    fixed_code = self._fixer.run(fixed_code, result.stdout + result.stderr)
                    fixed_code = self._strip(fixed_code)
                    console.print(fixed_code)
                    main_path.write_text(fixed_code, encoding="utf-8")
                else:  # manuel
                    console.print(f"[blue]Kod dosyası: {main_path}")
                    console.print("Hata detaylarını yukarıda görebilirsiniz. Düzenlemeyi kaydedip Enter'e basın.")
                    click.prompt("Devam etmek için Enter", default="", show_default=False)
                    fixed_code = main_path.read_text(encoding="utf-8")

                attempts += 1

            if attempts == 3 and result.returncode != 0:
                console.print(
                    "[bold red]Testler 3 denemede de geçmedi. Daha fazla yardım için destekle iletişime geçin veya Manuel olarak düzeltin."
                )
                raise RuntimeError("Tests failed after 3 attempts")

        if self.explicit_save:
            write_text_to_file(self.save_path, self._strip(fixed_code))
            console.print(f"[bold green]Code saved to {self.save_path}.")
        else:
            console.print(f"[yellow]Code not saved yet. Suggested file: {self.save_path}")

        console.rule("[bold cyan]Crew Runner completed")

        # return fixed code and suggested path so that CLI can decide to save
        return fixed_code, self.save_path 