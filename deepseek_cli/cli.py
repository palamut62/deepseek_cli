from __future__ import annotations

import sys
import os
import importlib
import json
from pathlib import Path

import click
from rich import print as rprint

import openai

from deepseek_cli.crew_runner import CrewRunner
from deepseek_cli.tools.file_tools import write_text_to_file

# user preference file to remember 'always save' choice
CONFIG_PATH = Path.home() / ".deepseek_cli_config.json"


def _load_user_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_user_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg))


# try to access config module for updating constant dynamically
try:
    config_module = importlib.import_module("deepseek_cli.config")
except ModuleNotFoundError:
    config_module = None


try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path.cwd() / ".env")
except ImportError:
    pass


@click.command()
@click.argument("prompt", type=str)
@click.option("--save", "save_path", type=click.Path(dir_okay=False), help="File path to save the output (default: auto name in current directory).")
@click.option("--plan/--no-plan", default=False, help="Generate plan output.")
@click.option("--api-key", "api_key", type=str, help="Provide your DeepSeek API key.")

def main(prompt: str, save_path: str | None, plan: bool, api_key: str | None) -> None:
    """Use Claude-like code capabilities powered by DeepSeek from the terminal."""
    # apply api key if provided
    if api_key:
        openai.api_key = api_key
        os.environ["DEEPSEEK_API_KEY"] = api_key
        if config_module is not None:
            setattr(config_module, "DEEPSEEK_API_KEY", api_key)
        # persist to .env for future sessions
        env_file = Path.cwd() / ".env"
        with env_file.open("a", encoding="utf-8") as f:
            f.write(f"\nDEEPSEEK_API_KEY={api_key}\n")

    pref_cfg = _load_user_config()
    always_save_pref = pref_cfg.get("always_save", False)

    runner = CrewRunner(prompt=prompt, save_path=save_path, plan=plan)
    try:
        fixed_code, suggested_path = runner.run()

        # ask to save if user didn't explicitly provide --save and no always-save pref
        if save_path is None and not always_save_pref:
            choice = click.prompt(
                "Save code to file? [y]es / [n]o / [a]lways",
                type=click.Choice(["y", "n", "a"], case_sensitive=False),
                default="y",
            )
            if choice.lower() in {"y", "a"}:
                write_text_to_file(suggested_path, fixed_code)
                rprint(f"[bold green]Code saved to {suggested_path}.")
            if choice.lower() == "a":
                pref_cfg["always_save"] = True
                _save_user_config(pref_cfg)
    except Exception as exc:  # broad catch for CLI stability; logged below
        rprint(f"[bold red]Hata oluştu:[/bold red] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter 