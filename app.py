import json

import streamlit as st
import streamlit.components.v1 as components

from formatter.claude_client import transform_text
from formatter.hwpx_reader import read_hwpx_bytes

st.set_page_config(page_title="네이버 블로그 서식 변환기", layout="wide")
st.title("네이버 블로그 서식 변환기")

# ── Input ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["텍스트 입력", "hwpx 업로드"])
raw_text = ""

with tab1:
    text_input = st.text_area("글감을 붙여넣으세요", height=300, key="text_input")
    if text_input:
        raw_text = text_input

with tab2:
    uploaded = st.file_uploader("hwpx 파일 업로드", type=["hwpx"])
    if uploaded:
        try:
            raw_text = read_hwpx_bytes(uploaded.read())
            st.success("변환 완료")
            st.text_area("변환된 텍스트 미리보기", value=raw_text, height=200, disabled=True)
        except Exception as e:
            st.error(f"hwpx 변환 실패: {e}")

# ── Transform ──────────────────────────────────────────────────────────────────
if st.button("변환하기", type="primary", disabled=not bool(raw_text)):
    with st.spinner("Claude AI가 서식을 적용하는 중..."):
        try:
            st.session_state["result_html"] = transform_text(raw_text)
        except Exception as e:
            st.error(f"변환 실패: {e}")

# ── Result ─────────────────────────────────────────────────────────────────────
if "result_html" in st.session_state:
    html = st.session_state["result_html"]

    st.subheader("변환 결과")

    # Copy as rich text button (uses Clipboard API with text/html MIME type)
    html_js = json.dumps(html)
    components.html(
        f"""
        <style>
          button {{
            padding: 8px 16px;
            background: #03c75a;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
          }}
          button:hover {{ background: #02a84a; }}
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
        height=55,
    )

    # Preview
    st.subheader("미리보기")
    components.html(
        f"<div style='font-family:\"맑은 고딕\",sans-serif;font-size:15px;line-height:2;padding:16px'>{html}</div>",
        height=600,
        scrolling=True,
    )
