from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class StoryTemplate:
    template_id: str
    label: str
    pdf_filename: str
    workbook_filename: str
    chart_sheet: str
    chart_meta: Dict[str, object]
    markdown: str
    default_title: str

    def matches(self, pdfs: List[Path], workbooks: List[Path]) -> bool:
        pdf_match = any(path.name == self.pdf_filename for path in pdfs)
        workbook_match = any(path.name == self.workbook_filename for path in workbooks)
        return pdf_match and workbook_match

    def find_pdf_path(self, pdfs: List[Path]) -> Optional[Path]:
        for path in pdfs:
            if path.name == self.pdf_filename:
                return path
        return None

    def find_workbook_path(self, workbooks: List[Path]) -> Optional[Path]:
        for path in workbooks:
            if path.name == self.workbook_filename:
                return path
        return None


POPULATION_MARKDOWN = """
# 2022 인구 영역 핵심 진단

## 핵심 메시지
- 2020년부터 한국 인구는 자연감소 국면에 들어섰으며 2060년대에는 4천만 명 이하가 될 가능성이 큽니다.
- 합계출산율은 2000년대 이후 세계 최저 수준을 유지하면서, 2021년에는 0.81명까지 떨어졌습니다.
- 초고령화가 빠르게 진행되면서 사망자 수와 조사망률이 모두 증가했고, 기대수명이 늘어난 만큼 사회·보건 인프라 부담이 커지고 있습니다.
- 수도권과 일부 광역시에 인구가 집중되는 반면, 비수도권은 지속적인 인구 유출과 고령화가 겹치는 이중의 압력을 받고 있습니다.

## 출생과 자연감소의 가속화
도시화·주거비 상승·일자리 불안정이 맞물리며 혼인과 출산이 동시에 감소했습니다. 2021년 출생아 수는 26만 명대로 떨어져 1990년의 절반 수준이며, 합계출산율은 0.81명으로 OECD 최저입니다. 출생 규모 축소는 곧장 학령인구 감소로 이어져 교육, 국방, 지역경제 전반에 파급 효과를 일으키고 있습니다.

## 빠르게 다가온 초고령사회
고령인구(65세 이상)는 2020년 기준 810만 명을 넘겼고, 2030년에는 전체 인구의 25%를 넘길 것으로 전망됩니다. 기대수명 연장에 따라 암·심장질환·치매와 같은 만성질환 부담이 커지고, 돌봄·연금·의료 체계의 재설계를 요구합니다. 특히 사망자 수는 10년 사이 약 30% 늘어 조사망률도 꾸준히 상승하고 있습니다.

## 지역 간 인구 흐름의 분화
서울과 5대 광역시는 이미 마이너스 성장 단계에 진입했지만, 경기도와 세종시는 인구 유입이 계속되고 있습니다. 수도권과 중부권으로 인구가 몰리는 가운데 영남·호남권은 순유출이 이어져 지역 불균형이 확대되는 양상입니다. 지방 중소도시는 고령화와 인구 유출이 동시에 진행되면서 생활 인프라 유지가 점점 어려워질 가능성이 큽니다.

## 정책 시사점
- 초저출산을 완화하려면 주거·돌봄·일자리 정책을 패키지로 묶어 생애주기별 부담을 줄이는 접근이 필요합니다.
- 고령층 의료·돌봄 수요를 대비해 지역 기반의 통합 돌봄 체계를 확대하고, 장기요양서비스 인력과 재정을 미리 확보해야 합니다.
- 수도권 편중을 완화하기 위해 광역 교통망, 혁신도시, 기업 유치를 결합한 인구 순환 전략을 마련해야 합니다.
- 코로나19가 혼인·출생을 더 위축시킨 만큼 향후 감염병 등 외부 충격에 대응할 수 있는 가계 안전망을 강화할 필요가 있습니다.
""".strip()

CRIME_MARKDOWN = """
# 코로나19 이후 범죄 발생 변화

## 핵심 메시지
- 2020~2021년 감염병 확산기에 살인을 제외한 대부분의 범죄 유형이 감소했습니다.
- 강도·폭행·성폭력 등 대면 접촉이 필요한 범죄는 사회적 거리두기 강도에 따라 진폭이 크게 움직였습니다.
- 가정폭력과 데이트폭력은 장기적으로 감소세지만, 봉쇄가 완화되면 즉시 다시 증가하는 탄력적 특성이 나타났습니다.
- 절도와 사기는 팬데믹 이전 증가세가 꺾이며 비대면 환경에서의 범죄 대응 전략이 필요함을 시사합니다.

## 범죄 유형별 흐름
### 강력범죄
- **살인**은 일일 신고 건수가 적어 통계적 변동성이 크고 코로나19 추이와의 명확한 상관관계를 찾기 어려웠습니다.
- **강도**는 1차·2차 대유행기에 급격히 줄었고, 봉쇄가 완화돼도 이전 수준으로 회복되지 않았습니다.
- **폭행·상해**는 사회적 활동이 줄었던 2020년 8~9월에 크게 감소했으나, 방역 단계가 완화되자 다시 증가했습니다.

### 성·가정폭력
- **성폭력**은 코로나19 이후 전반적으로 감소했고, 1차 대유행 직후인 4월과 2차 대유행 직후인 12월에 뚜렷한 저점을 기록했습니다.
- **가정폭력**은 이미 감소 추세였는데 팬데믹 이후 감소 폭이 커졌습니다. 이동 제한과 실외 활동 감소가 영향을 준 것으로 보입니다.
- **데이트폭력**은 장기 추세와 크게 다르지 않지만, 봉쇄가 완화되면 곧바로 증가하는 민감한 특성을 보였습니다.

### 생활·재산범죄
- **절도**는 2017~2019년 완만한 증가세였으나, 코로나19 이후 이동량 감소와 매장 폐쇄로 상승세가 꺾였습니다.
- **사기**는 비대면 거래 증가로 늘어날 것이라는 우려와 달리 2020년 들어 증가 폭이 둔화되었습니다.
- **차량·도난 관련 범죄**도 전반적으로 감소해, 보행자·차량 이동량의 축소가 범죄 기회 자체를 줄였음을 시사합니다.

## 감염병 환경이 남긴 과제
- 거리두기와 같은 사회적 조치가 범죄 발생 구조를 빠르게 바꿀 수 있다는 점이 확인되었습니다.
- 감염병 충격이 장기화될 경우 사회적 스트레스 요인이 새로운 폭력 범죄를 자극할 수 있다는 경고도 함께 남았습니다.
- 비대면 환경에 맞는 치안 활동, 신고 시스템, 피해자 보호 체계를 미리 설계해야 다음 위기에 신속히 대응할 수 있습니다.
""".strip()


TEMPLATES: List[StoryTemplate] = [
    StoryTemplate(
        template_id="population-2022",
        label="인구 영역 2022 (출생·고령화)",
        pdf_filename="01-1 인구 영역의 주요 동향(2022)_김두섭_20221111_최종.pdf",
        workbook_filename="01-1 인구 영역의 주요 동향(2022)_김두섭_DATA_20221111_최종.xlsx",
        chart_sheet="2022_데이터",
        chart_meta={
            "chart_type": "선",
            "workbook": "01-1 인구 영역의 주요 동향(2022)_김두섭_DATA_20221111_최종.xlsx",
            "sheet": "2022_데이터",
            "x": 1,
            "y": [2, 3],
            "color": None,
            "transform": {
                "slice_rows": [221, 268],
                "rename": {1: "연도", 2: "출생아수", 3: "합계출산율"},
                "use_columns": ["연도", "출생아수", "합계출산율"],
                "to_numeric": ["연도", "출생아수", "합계출산율"],
                "scale": {"출생아수": 0.001},
                "rename_after_scale": {"출생아수": "출생아수(천 명)"},
                "dropna": ["연도", "출생아수(천 명)", "합계출산율"],
            },
            "labels": {
                "연도": "연도",
                "출생아수(천 명)": "출생아수 (천 명)",
                "합계출산율": "합계출산율",
            },
        },
        markdown=POPULATION_MARKDOWN,
        default_title="한국 인구의 전환점: 출생과 고령화",
    ),
    StoryTemplate(
        template_id="crime-2021",
        label="코로나19 이후 범죄 발생 변화",
        pdf_filename="10-2 코로나19 이후 범죄발생의 변화_박형민_20211123_최종.pdf",
        workbook_filename="10-2 코로나19 이후 범죄발생의 변화_박형민_DATA_20211123_최종.xlsx",
        chart_sheet="그림2_DATA",
        chart_meta={
            "chart_type": "막대",
            "workbook": "10-2 코로나19 이후 범죄발생의 변화_박형민_DATA_20211123_최종.xlsx",
            "sheet": "그림2_DATA",
            "x": "Crime",
            "y": ["ES"],
            "color": None,
            "filters": {"City": ["전체"]},
            "transform": {
                "rename": {
                    "Crime": "범죄 유형",
                    "ES": "발생지수",
                    "95% CI lower": "신뢰구간 하한",
                    "95% CI upper": "신뢰구간 상한",
                },
                "use_columns": ["범죄 유형", "발생지수", "신뢰구간 하한", "신뢰구간 상한"],
                "to_numeric": ["발생지수", "신뢰구간 하한", "신뢰구간 상한"],
                "sort_by": {"column": "발생지수", "ascending": False},
            },
            "labels": {
                "범죄 유형": "범죄 유형",
                "발생지수": "코로나 이후 발생지수",
            },
        },
        markdown=CRIME_MARKDOWN,
        default_title="코로나19가 바꾼 범죄 양상",
    ),
]


def available_templates(pdfs: List[Path], workbooks: List[Path]) -> List[StoryTemplate]:
    return [template for template in TEMPLATES if template.matches(pdfs, workbooks)]


def get_template(template_id: str) -> Optional[StoryTemplate]:
    for template in TEMPLATES:
        if template.template_id == template_id:
            return template
    return None
