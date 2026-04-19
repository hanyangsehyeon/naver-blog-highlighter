import json

import streamlit as st
import streamlit.components.v1 as components

from formatter.claude_client import transform_text_and_hashtags
from formatter.hwpx_reader import read_hwpx_bytes

st.set_page_config(page_title="네이버 블로그 서식 변환기", layout="wide")

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', '맑은 고딕', sans-serif;
    }
    .stApp {
        background-color: #f5f6f7;
    }
    [data-testid="column"] {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 24px !important;
    }
    .block-container {
        padding-top: 3.5rem;
        padding-bottom: 3rem;
    }
    .app-title {
        font-size: 26px;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 4px;
    }
    .app-title span {
        color: #03c75a;
    }
    .app-subtitle {
        font-size: 14px;
        color: #888;
        margin-bottom: 28px;
    }
    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #1a1a1a;
        border-left: 4px solid #03c75a;
        padding-left: 10px;
        margin-bottom: 14px;
        line-height: 1.4;
    }
    .card {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 24px;
        margin-bottom: 16px;
    }
    .preview-box {
        background: #fff;
        border-radius: 10px;
        border: 1.5px solid #e8e8e8;
        padding: 20px 24px;
        min-height: 420px;
        font-size: 15px;
        line-height: 2;
    }
    .preview-empty {
        background: #fff;
        border-radius: 10px;
        border: 1.5px dashed #d5d5d5;
        padding: 20px 24px;
        min-height: 420px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #bbb;
        font-size: 14px;
    }
    .hashtag-box {
        background: #fff;
        border-radius: 10px;
        border: 1.5px solid #e8e8e8;
        padding: 16px 20px;
        min-height: 58px;
        line-height: 2.2;
    }
    .hashtag-box-empty {
        background: #fff;
        border-radius: 10px;
        border: 1.5px dashed #d5d5d5;
        padding: 16px 20px;
        min-height: 58px;
        color: #bbb;
        font-size: 14px;
        display: flex;
        align-items: center;
    }
    .pill {
        display: inline-block;
        background: #e8f9f0;
        color: #03c75a;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 13px;
        font-weight: 500;
        margin: 2px 3px;
    }
    /* 텍스트 입력 배경 */
    .stTextArea textarea {
        background-color: #efefef !important;
        border: 1.5px solid #ddd !important;
        border-radius: 8px !important;
    }
    /* Streamlit primary button → 네이버 그린 */
    .stButton > button[kind="primary"] {
        background-color: #03c75a !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        height: 46px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #02b350 !important;
    }
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        color: #03c75a !important;
    }
    .stTabs {
        margin-top: 12px;
    }
    hr {
        border-color: #eaeaea;
        margin: 28px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-title">네이버 블로그 <span>서식 변환기</span></div>
    <div class="app-subtitle">글감을 붙여넣으면 Claude AI가 형광펜·글자색·볼드 서식을 자동으로 적용해드립니다.</div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns(2, gap="large")

# ── Left: Input ────────────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="section-header">글감 입력</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["텍스트 입력", "hwpx 업로드"])
    raw_text = ""

    with tab1:
        text_input = st.text_area(
            "글감을 붙여넣으세요", height=460, key="text_input", label_visibility="collapsed"
        )
        if text_input:
            raw_text = text_input

    with tab2:
        uploaded = st.file_uploader("hwpx 파일 업로드", type=["hwpx"])
        if uploaded:
            try:
                raw_text = read_hwpx_bytes(uploaded.read())
                st.success("변환 완료")
                st.text_area("변환된 텍스트 미리보기", value=raw_text, height=380, disabled=True)
            except Exception as e:
                st.error(f"hwpx 변환 실패: {e}")

    if st.button("변환하기", type="primary", disabled=not bool(raw_text), use_container_width=True):
        with st.spinner("Claude AI가 서식을 적용하는 중..."):
            try:
                html, hashtags = transform_text_and_hashtags(raw_text)
                st.session_state["result_html"] = html
                st.session_state["result_hashtags"] = hashtags
            except Exception as e:
                st.error(f"변환 실패: {e}")

# ── Right: Result ──────────────────────────────────────────────────────────────
with col_right:
    st.markdown('<div class="section-header">변환 결과</div>', unsafe_allow_html=True)

    if "result_html" in st.session_state:
        html = st.session_state["result_html"]
        html_js = json.dumps(html)

        components.html(
            f"""
            <style>
              body {{ margin: 0; font-family: 'Noto Sans KR', sans-serif; }}
              button {{
                padding: 8px 18px;
                background: #03c75a;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
              }}
              button:hover {{ background: #02b350; }}
              #msg {{ margin-left: 10px; color: #03c75a; font-size: 13px; display: none; }}
            </style>
            <button onclick="copyRichText()">📋 클립보드에 복사 (서식 포함)</button>
            <span id="msg">✅ 복사됨!</span>
            <script>
              const htmlContent = {html_js};
              async function copyRichText() {{
                const plain = htmlContent.replace(/<[^>]+>/g, '');
                await navigator.clipboard.write([
                  new ClipboardItem({{
                    'text/html': new Blob([htmlContent], {{type: 'text/html'}}),
                    'text/plain': new Blob([plain], {{type: 'text/plain'}})
                  }})
                ]);
                const msg = document.getElementById('msg');
                msg.style.display = 'inline';
                setTimeout(() => msg.style.display = 'none', 2000);
              }}
            </script>
            """,
            height=50,
        )
        st.markdown(f'<div class="preview-box">{html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="height:58px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="preview-empty">변환 결과가 여기에 표시됩니다</div>', unsafe_allow_html=True)

# ── Hashtags ───────────────────────────────────────────────────────────────────
FIXED_HASHTAGS = "#우듬지루미북 #검단독서논술 #이음초 #이음초논술 #검단논술 #검단논술학원 #검단글쓰기 #검단그림책수업 #검단문해력 #검단교과연계 #검단우듬지논술 #중등논술 #독서논술 #초등논술 #논술학원추천 #글쓰기지도 #초등글쓰기 #독서논술 #글쓰기교육"

def _render_pills(tag_str: str) -> str:
    return " ".join(
        f'<span class="pill">{t}</span>' for t in tag_str.split() if t.startswith("#")
    )

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-header">해시태그</div>', unsafe_allow_html=True)

col_tag1, col_tag2 = st.columns(2, gap="large")

with col_tag1:
    st.caption("고정 해시태그")
    st.markdown(f'<div class="hashtag-box">{_render_pills(FIXED_HASHTAGS)}</div>', unsafe_allow_html=True)

with col_tag2:
    st.caption("글 내용 기반 해시태그")
    if "result_hashtags" in st.session_state:
        tags = st.session_state["result_hashtags"]
        st.markdown(f'<div class="hashtag-box">{_render_pills(tags)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hashtag-box-empty">변환 후 자동 생성됩니다</div>', unsafe_allow_html=True)

if "result_hashtags" in st.session_state:
    combined = FIXED_HASHTAGS + " " + st.session_state["result_hashtags"]
    combined_js = json.dumps(combined)
    components.html(
        f"""
        <style>
          body {{ margin: 0; font-family: 'Noto Sans KR', sans-serif; }}
          button {{
            padding: 8px 18px;
            background: #03c75a;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
          }}
          button:hover {{ background: #02b350; }}
          #msg {{ margin-left: 10px; color: #03c75a; font-size: 13px; display: none; }}
        </style>
        <button onclick="copyAll()">📋 해시태그 전체 복사</button>
        <span id="msg">✅ 복사됨!</span>
        <script>
          async function copyAll() {{
            await navigator.clipboard.writeText({combined_js});
            const msg = document.getElementById('msg');
            msg.style.display = 'inline';
            setTimeout(() => msg.style.display = 'none', 2000);
          }}
        </script>
        """,
        height=50,
    )
