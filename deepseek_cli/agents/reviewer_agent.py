from __future__ import annotations

from typing import List, Dict

from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """Agent that reviews code for quality, risks and improvements."""

    def __init__(self) -> None:
        super().__init__(
            role="Kod İnceleme Uzmanı",
            goal="Üretilen kodun kalite analizi ve eksiklerinin tespiti",
            backstory="Tecrübeli bir code reviewer olarak güvenlik, performans ve style konularını denetler.",
        )

    def build_prompt(self, code_snippet: str) -> List[Dict[str, str]]:  # type: ignore[override]
        system_msg = (
            "Aşağıdaki kodu detaylıca incele. Hataları, performans sorunlarını ve "
            "güvenlik açıklarını madde madde belirt. Gerektiğinde örnek düzeltme "
            "kodu öner."
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": code_snippet},
        ] 