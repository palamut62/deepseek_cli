from __future__ import annotations

from typing import List, Dict

from .base_agent import BaseAgent


class TodoAgent(BaseAgent):
    """Agent that turns user prompt into a TODO markdown list."""

    def __init__(self) -> None:
        super().__init__(
            role="Görev Takip Uzmanı",
            goal="Prompta göre yapılacaklar listesi üretmek",
            backstory="Takımda herkesin görevlerini tanımlar ve düzenler",
        )

    def build_prompt(self, user_request: str) -> List[Dict[str, str]]:  # type: ignore[override]
        system_msg = (
            "Sen proje yöneticisisin. Kullanıcı talebine dayanarak, GitHub markdown"
            " formatında yapılacaklar listesi oluştur. - [ ] checkbox kullan."
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_request},
        ] 