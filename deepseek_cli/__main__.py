from __future__ import annotations

"""Interactive terminal arayüzü (REPL) for DeepSeek CLI.

Kullanım:
    python -m deepseek_cli

Bu modül, Claude benzeri bir deneyim için Rich tabanlı bir REPL sunar.
Komutlar:
    :quit / :q / exit  → oturumu sonlandırır
    :help              → komut listesini gösterir

Prompt girildiğinde plan/todo seçenekleri sorulur ve CrewRunner çalıştırılır.
"""

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path.cwd() / ".env")
except ImportError:
    pass

from typing import Tuple

from rich.console import Console
from rich.prompt import Prompt, Confirm

from deepseek_cli.crew_runner import CrewRunner
from deepseek_cli.tools.file_tools import write_text_to_file

console = Console()

# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

ASCII_BANNER = r"""


!  ██████╗ ███████╗███████╗██████╗      ██████╗ ██████╗ ██████╗ ███████╗    ██╗   ██╗ ██╗    ██████╗ 
!  ██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝    ██║   ██║███║   ██╔═████╗
!  ██║  ██║█████╗  █████╗  ██████╔╝    ██║     ██║   ██║██║  ██║█████╗      ██║   ██║╚██║   ██║██╔██║
!  ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝     ██║     ██║   ██║██║  ██║██╔══╝      ╚██╗ ██╔╝ ██║   ████╔╝██║
!  ██████╔╝███████╗███████╗██║         ╚██████╗╚██████╔╝██████╔╝███████╗     ╚████╔╝  ██║██╗╚██████╔╝
!  ╚═════╝ ╚══════╝╚══════╝╚═╝          ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝      ╚═══╝   ╚═╝╚═╝ ╚═════╝ 
!                                                                                                    
                                                                                    
"""


def print_banner() -> None:
    """Render ASCII banner with color gradient-like effect using rich markup."""
    gradient_colors = ["blue", "cyan", "magenta", "bright_magenta"]
    lines = ASCII_BANNER.splitlines()
    for idx, line in enumerate(lines):
        color = gradient_colors[idx % len(gradient_colors)]
        console.print(line, style=color)


def print_tips() -> None:
    console.print("\n[bold]Tips for getting started:[/bold]")
    console.print(" 1. Ask questions, generate code, or run commands.")
    console.print(" 2. Be specific for the best results.")
    console.print(" 3. Type :help for more information.\n")


CONFIG_PATH = Path.home() / ".deepseek_cli_config.json"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg))

def ensure_api_key() -> None:
    """Ensure DEEPSEEK_API_KEY env var is present; if not, ask user."""
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[yellow]No API key found. Please enter it to continue.")
        key = Prompt.ask("[bold]🔑 DeepSeek API key[/bold] (blank to quit)")
        if key:
            os.environ["DEEPSEEK_API_KEY"] = key
            # persist to .env
            env_file = Path.cwd() / ".env"
            with env_file.open("a", encoding="utf-8") as f:
                f.write(f"\nDEEPSEEK_API_KEY={key}\n")
        else:
            console.print("[red]API anahtarı ayarlanmadı, oturum kapatılıyor.")
            raise SystemExit(1)

def interactive_save(code: str, path: str, cfg: dict) -> None:
    always = cfg.get("always_save", False)
    if always:
        write_text_to_file(path, code)
        console.print(f"[bold green]Kod {path} dosyasına kaydedildi (auto).")
        return

    choice = Prompt.ask(
        "Kod dosya olarak kaydedilsin mi? (y/n/a)",
        choices=["y", "n", "a"],
        default="y",
    )
    if choice == "y" or choice == "a":
        write_text_to_file(path, code)
        console.print(f"[bold green]Kod {path} dosyasına kaydedildi.")
    if choice == "a":
        cfg["always_save"] = True
        save_config(cfg)


def main_loop() -> None:
    cfg = load_config()

    console.clear()
    print_banner()
    print_tips()

    ensure_api_key()

    console.print("[bold green]Features:")
    console.print("""
• Natural language prompt → Code generation
• Plan mode               → Task breakdown
• Code review             → Detect issues & improvements
• Code fix                → Apply automatic fixes
• File save               → Interactive or automatic

Commands:
  :help       → show this help message
  :features   → list available features
  :quit / :q  → exit the session
  exit        → exit the session
""")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]> ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]Çıkış yapılıyor...")
            break

        stripped = user_input.strip()

        if stripped in {":q", ":quit", "exit"}:
            break

        if stripped == ":help":
            console.print("""
Commands:
  :help         → show this help message
  :features     → list available features
  :quit / :q    → exit the session
  exit          → exit the session
""")
            continue
        if stripped == ":features":
            console.print("""
Features:
  • Natural language prompt → Code generation
  • Plan mode               → Task breakdown
  • Code review             → Detect issues & improvements
  • Code fix                → Apply automatic fixes
  • File save               → Interactive or automatic
""")
            continue

        plan = Confirm.ask("Generate plan output?", default=False)

        runner = CrewRunner(prompt=user_input, save_path=None, plan=plan)
        code, suggested_path = runner.run()

        interactive_save(code, suggested_path, cfg)

    console.rule("[bold cyan]Görüşmek üzere!")


if __name__ == "__main__":
    main_loop() 