from __future__ import annotations

from typing import List, Dict

from .base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Agent that produces pytest unit tests for the generated code."""

    def __init__(self) -> None:
        super().__init__(
            role="Test Yazarı",
            goal="Kod için pytest birim testleri üretmek",
            backstory="Deneyimli bir test mühendisi olarak tüm fonksiyonları kapsayan testler yazar.",
        )

    def build_prompt(self, code_snippet: str) -> List[Dict[str, str]]:  # type: ignore[override]
        system_msg = (
            "Aşağıdaki Python kodu için kapsamlı pytest birim testleri yaz. "
            "Tüm fonksiyonları ve ana senaryoları kapsa. Sadece test kodunu, "
            "```python``` bloğu içinde döndür."
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": code_snippet},
        ] 