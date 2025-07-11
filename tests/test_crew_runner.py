import pytest
from deepseek_cli.crew_runner import CrewRunner
import tempfile
import os
from unittest import mock


def test_generate_default_filename():
    runner = CrewRunner("test prompt")
    assert runner._generate_default_filename().endswith("test_prompt.py")

def test_sanitize():
    assert CrewRunner._sanitize("Hello World!") == "Hello_World" 

def test_run(tmp_path):
    save_file = tmp_path / "test.py"
    runner = CrewRunner("test prompt", save_path=str(save_file))

    # agent stubları
    runner._planner.run = lambda prompt: ""
    runner._todoer.run = lambda prompt: "- [ ] task"
    runner._coder.run = lambda prompt: "```python\nprint('hello')\n```"
    runner._reviewer.run = lambda code: ""
    runner._fixer.run = lambda code, notes: "print('hello')"
    runner._tester.run = lambda code: "```python\ndef test_dummy():\n    assert True\n```"

    fixed_code, path = runner.run()

    assert path == str(save_file)
    assert save_file.exists()
    assert "print('hello')" in fixed_code 