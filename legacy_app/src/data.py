from typing import List, Dict

CATEGORIES: List[tuple[str, str]] = [
    ("all", "전체"),
    ("community", "개인, 가족, 공동체"),
    ("politics", "정치와 시민사회"),
    ("education", "교육과 돌봄"),
    ("work", "일과 직업"),
    ("economy", "경제와 생활수준"),
    ("environment", "에너지와 환경"),
    ("technology", "기술과 정보"),
    ("space", "공간과 지역"),
]

LABELS_BY_KEY: Dict[str, str] = {k: v for k, v in CATEGORIES}

