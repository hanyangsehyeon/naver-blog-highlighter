import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

# Streamlit Cloud secrets override
try:
    import streamlit as st
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

_client = None
_system_prompt = None

SYSTEM_PROMPT = """
너는 블로그 글에 서식을 적용하는 에디터야.

## 출력 형식 (HTML만 출력, 다른 텍스트 금지)
- 단락마다 <div>...</div>로 감싸기
- 형광펜: <span style="background-color:#색코드;font-weight:bold">텍스트</span>
- 글자색: <span style="color:#색코드;font-weight:bold">텍스트</span>
- 볼드만: <span style="font-weight:bold">텍스트</span>
- 서식 없는 텍스트는 태그 없이 그대로

## 색상 규칙
- 형광펜: #ffe3c8 / #fdd5f5 / #e3fdc8 / #bdfbfa / #fff8b2 만 사용
- 글자색: 형광펜 계열에 맞는 색만 사용
  - #ffe3c8 → 글자색: #700001, #830041, #823f00
  - #fdd5f5 → 글자색: #4f0041, #830041, #700001
  - #e3fdc8 → 글자색: #004e22, #00554c, #004e6a
  - #bdfbfa → 글자색: #003960, #004e82, #004e6a

## 적용 범위
- 형광펜: 단락당 1~2개, 핵심 명사구에만 (문장 전체 금지)
- 글자색: 단락당 최대 3개 구간, 부분 적용만
- 형광펜과 글자색 동일 범위 동시 적용 금지
- 형광펜/글자색 적용 시 반드시 볼드 함께 적용

## 단락 분리
- 원문의 줄바꿈 기준으로 단락 분리
- 빈 줄은 <div>&#8203;</div>

## 예시 1
입력: "상대를 설득시켜야 하는 토론 수업이라 앞서 교실의 공기와는 달랐다."
출력: <div><span style="background-color:#ffe3c8;font-weight:bold">상대를 설득시켜야 하는 토론 수업</span>이라 앞서 교실의 공기와는 달랐다.</div>

## 예시 2
입력:
"지난 1월 23일 국회에서 인공지능 시대의 핵심 역량으로 독서를 꼽으며, 국가 교육 패러다임을 '독서 중심'으로 전환하겠다는 '독서국가 선포식 및 추진위원회 출범식'이 열렸다는 소식을 접했다.
이날 국회 교육위에서 발표된 핵심 구상은 크게 세 가지로 나뉜다."
출력:
<div>지난 1월 23일 국회에서 <span style="background-color:#ffe3c8;font-weight:bold">인공지능 시대의 핵심 역량</span>으로 독서를 꼽으며, <span style="color:#700001;font-weight:bold">국가 교육 패러다임을 '독서 중심'으로 전환하겠다는</span> '<span style="background-color:#fff8b2;font-weight:bold">독서국가 선포식 및 추진위원회 출범식</span>'이 열렸다는 소식을 접했다.</div>
<div>이날 <span style="color:#823f00;font-weight:bold">국회 교육위에서 발표된 핵심 구상은 크게 세 가지</span>로 나뉜다.</div>
"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def transform_text(raw_text: str) -> str:
    """Send raw text to Claude API, return formatted HTML string."""
    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": raw_text}],
    )
    return response.content[0].text.strip()
