from __future__ import annotations

from typing import List, Dict

from .base_agent import BaseAgent


class CoderAgent(BaseAgent):
    """Agent that generates Python code for the requested task."""

    def __init__(self) -> None:
        super().__init__(
            role="Python Kodu Üreticisi",
            goal="Talebe uygun çalışır kod üretmek",
            backstory="Deneyimli bir yazılım geliştiricisi olarak temiz ve test edilebilir kod yaz.",
        )

    def build_prompt(self, user_request: str) -> List[Dict[str, str]]:  # type: ignore[override]
        system_msg = (
            "Sen kıdemli bir Python geliştiricisisin. İstenen özelliği eksiksiz,"
            " PE P8 uyumlu ve yorum satırları ekleyerek yaz. Gerekirse ek dosyalar"
            " ve testler için talimat ver."  # noqa: E501
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_request},
        ] 