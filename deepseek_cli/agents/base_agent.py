from __future__ import annotations

import abc
import importlib
from typing import List, Dict, Any

import openai
from deepseek_cli import config

# ---------------------------------------------------------------------------
# OpenAI client setup compatible with both <1.0 and >=1.0 versions
# ---------------------------------------------------------------------------

_HAS_NEW_CLIENT = False

try:
    # openai >=1.0 provides OpenAI class
    from openai import OpenAI  # type: ignore

    _client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_API_BASE)
    _HAS_NEW_CLIENT = True
except ImportError:  # pragma: no cover
    # older version fallback will use module-level api
    pass

if not _HAS_NEW_CLIENT:
    # configure legacy client
    openai.api_key = config.DEEPSEEK_API_KEY
    openai.api_base = config.DEEPSEEK_API_BASE


class BaseAgent(abc.ABC):
    """Abstract base class for all agents in the system."""

    role: str
    goal: str
    backstory: str

    def __init__(self, role: str, goal: str, backstory: str) -> None:
        self.role = role
        self.goal = goal
        self.backstory = backstory

    @abc.abstractmethod
    def build_prompt(self, *args: Any, **kwargs: Any) -> List[Dict[str, str]]:
        """Return a list of chat messages to send to the LLM."""

    def _chat(self, messages: List[Dict[str, str]]) -> str:
        """Call DeepSeek model via OpenAI-compatible API, handling both client versions."""
        if _HAS_NEW_CLIENT:
            response = _client.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=messages,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()

        # legacy path
        response = openai.ChatCompletion.create(
            model=config.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    def run(self, *args: Any, **kwargs: Any) -> str:
        """High-level method executed by the crew runner."""
        messages = self.build_prompt(*args, **kwargs)
        return self._chat(messages) 