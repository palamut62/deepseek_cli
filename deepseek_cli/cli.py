from __future__ import annotations

import sys
import os
import importlib
import json
from pathlib import Path
import re

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


def print_quick_usage():
    rprint("[bold cyan]Kullanım:[/bold cyan] özellik seç → açıklama yaz → (isteğe bağlı plan) → kod & TODO → kaydet? [e/h/a]")

@click.command()
@click.option('--feature', 'feature', type=str, default=None, help='Bir özellik seçin (örn: auth, api, db, ui, ...).')
@click.option('--save', 'save_path', type=click.Path(dir_okay=False), help='File path to save the output (default: auto name in current directory).')
@click.option('--plan/--no-plan', default=False, help='Generate plan output.')
@click.option('--api-key', 'api_key', type=str, help='Provide your DeepSeek API key.')

def main(feature: str | None, save_path: str | None, plan: bool, api_key: str | None) -> None:
    print_quick_usage()
    """Use Claude-like code capabilities powered by DeepSeek from the terminal."""
    # Özellik menüsü
    FEATURES = [
        'auth', 'api', 'db', 'ui', 'test', 'ci', 'cache', 'logging', 'config', 'utils', 'other'
    ]
    if not feature:
        rprint("[bold cyan]Lütfen bir özellik seçin:")
        for idx, f in enumerate(FEATURES, 1):
            rprint(f"[bold yellow]{idx}[/] - {f}")
        secim = click.prompt("Seçiminiz (numara veya isim)", default="", show_default=False)
        if not secim:
            rprint("[bold red]Hiçbir özellik seçilmedi! Çıkılıyor...")
            sys.exit(1)
        if secim.isdigit() and 1 <= int(secim) <= len(FEATURES):
            feature = FEATURES[int(secim)-1]
        elif secim in FEATURES:
            feature = secim
        else:
            rprint(f"[bold red]Geçersiz seçim: {secim}")
            sys.exit(1)
    rprint(f"[bold green]Seçilen özellik: {feature}")

    # Promptu kullanıcıdan iste
    prompt = click.prompt("Lütfen bu özellik için ne yapılacağını yazın", default="", show_default=False)
    if not prompt.strip():
        rprint("[bold red]Prompt girilmedi! Çıkılıyor...")
        sys.exit(1)

    # API key işlemleri
    if api_key:
        openai.api_key = api_key
        os.environ["DEEPSEEK_API_KEY"] = api_key
        if config_module is not None:
            setattr(config_module, "DEEPSEEK_API_KEY", api_key)
        env_file = Path.cwd() / ".env"
        with env_file.open("a", encoding="utf-8") as f:
            f.write(f"\nDEEPSEEK_API_KEY={api_key}\n")

    # anahtar yoksa prompt et
    _ensure_api_key(api_key)

    pref_cfg = _load_user_config()
    always_save_pref = pref_cfg.get("always_save", False)

    runner = CrewRunner(prompt=f"[{feature}] {prompt}", save_path=save_path, plan=plan)
    try:
        # Plan oluşturulacaksa önce planı göster
        if plan:
            rprint("[yellow]📝 Plan oluşturuluyor...")
            plan_output = runner._planner.run(f"[{feature}] {prompt}")
            rprint(plan_output)
            devam = click.prompt("Devam edilsin mi? (e/h)", type=str, default="e")
            if devam.lower() != "e":
                rprint("[bold red]İşlem iptal edildi.")
                sys.exit(0)
        # Plan yoksa veya devam edilsin dendi ise normal akış
        fixed_code, _ = runner.run()

        # dil ve dosya adı tespiti
        lang = _detect_language(fixed_code)
        ext = _ext_map.get(lang, ".txt")
        project_slug = CrewRunner._sanitize(prompt)
        project_dir = Path.cwd() / "projeler" / project_slug
        default_filename = _template_map.get(ext, f"{project_slug}{ext}")
        suggested_path = str(project_dir / default_filename)

        if save_path is None and not always_save_pref:
            choice = click.prompt(
                f"Dosyalar {suggested_path} konumuna kaydedilsin mi? [e]vet / [h]ayır / [a]lways",
                type=click.Choice(["e", "h", "a"], case_sensitive=False),
                default="e",
            )
            if choice.lower() in {"e", "a"}:
                clean_code = _strip_code_block_markers(fixed_code)
                write_text_to_file(suggested_path, clean_code)
                rprint(f"[bold green]Kod kaydedildi: {suggested_path}.")
            if choice.lower() == "a":
                pref_cfg["always_save"] = True
                _save_user_config(pref_cfg)
        elif save_path:  # kullanıcı --save ile verdi
            clean_code = _strip_code_block_markers(fixed_code)
            write_text_to_file(save_path, clean_code)
            rprint(f"[bold green]Kod kaydedildi: {save_path}.")
        else:
            # always_save_pref geçerli ise otomatik kaydet
            if always_save_pref:
                clean_code = _strip_code_block_markers(fixed_code)
                write_text_to_file(suggested_path, clean_code)
                rprint(f"[bold green]Kod otomatik kaydedildi: {suggested_path}.")
    except Exception as exc:
        rprint(f"[bold red]Hata oluştu:[/bold red] {exc}")
        sys.exit(1)


def _detect_language(code: str) -> str:
    match = re.search(r"```(\w+)", code)
    if match:
        return match.group(1).lower()
    # fallback: python
    return "python"

_ext_map = {
    "python": ".py",
    "py": ".py",
    "javascript": ".js",
    "js": ".js",
    "typescript": ".ts",
    "ts": ".ts",
    "tsx": ".tsx",
    "html": ".html",
}

_template_map = {
    ".py": "main.py",
    ".js": "index.js",
    ".ts": "index.ts",
    ".tsx": "App.tsx",
    ".html": "index.html",
}

def _strip_code_block_markers(code: str) -> str:
    """Return only the contents inside the first markdown code block.

    If no code block is found, return the original string stripped.
    """
    match = re.search(r"```(?:\w+)?\s*\n(.*?)```", code, re.DOTALL)
    if match:
        return match.group(1).strip()

    # fallback to previous simple stripping
    lines = code.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def _ensure_api_key(provided_key: str | None) -> None:
    """Ensure DEEPSEEK_API_KEY is set; otherwise prompt user once."""
    # 1) if user passed --api-key, we already handled in caller
    import deepseek_cli.config as cfg  # local import to get latest value

    if cfg.DEEPSEEK_API_KEY:
        return  # already set

    if provided_key:
        return  # handled earlier but fallback safety

    key = click.prompt("DEEPSEEK_API_KEY bulunamadı. Lütfen API anahtarınızı girin", hide_input=True, default="", show_default=False)
    if not key:
        rprint("[bold red]API anahtarı girilmedi. Çıkılıyor...")
        sys.exit(1)
    # set env and update config
    os.environ["DEEPSEEK_API_KEY"] = key
    cfg.DEEPSEEK_API_KEY = key  # type: ignore[attr-defined]
    # persist to .env
    env_file = Path.cwd() / ".env"
    with env_file.open("a", encoding="utf-8") as f:
        f.write(f"\nDEEPSEEK_API_KEY={key}\n")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter 