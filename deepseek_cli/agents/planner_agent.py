from __future__ import annotations

from typing import List, Dict

from .base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent responsible for decomposing a high-level user request into actionable steps."""

    def __init__(self) -> None:
        super().__init__(
            role="Yazılım Planlayıcısı",
            goal="Kullanıcı isteğini adım adım görev listesine çevirmek",
            backstory=(
                "Tecrübeli bir ürün yöneticisi olarak, gelen isteği net ve takip edilebilir adımlara böler."
            ),
        )

    # override
    def build_prompt(self, user_request: str) -> List[Dict[str, str]]:  # type: ignore[override]
        system_msg = (
            "Sen üst düzey bir yazılım planlayıcısısın. Kullanıcı talebini mantıksal"
            " ve sıralı görevlere parçala. Her adımı açık, kısa ve yapılabilir şekilde"
            " numaralandır. Gerektiğinde ek görevler ekle, ancak gereksiz detay verme."
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_request},
        ] 