from __future__ import annotations

from typing import List, Dict

from .base_agent import BaseAgent


class FixerAgent(BaseAgent):
    """Agent that applies fixes to code based on review feedback."""

    def __init__(self) -> None:
        super().__init__(
            role="Kod Düzeltme Uzmanı",
            goal="İnceleme çıktısındaki sorunları gidermek",
            backstory="Hataları hızlıca bulup düzelten deneyimli bir geliştirici.",
        )

    def build_prompt(self, code_snippet: str, review_notes: str) -> List[Dict[str, str]]:  # type: ignore[override]
        system_msg = (
            "Aşağıda verilen kodu ve inceleme notlarını kullanarak kodu düzelt. "
            "Nihai kodu yalnızca tek bir kod bloğu içinde döndür."
        )
        user_content = (
            f"Kod:\n{code_snippet}\n\nİnceleme Notları:\n{review_notes}"
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ] 