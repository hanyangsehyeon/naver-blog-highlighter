import json

import streamlit as st
import streamlit.components.v1 as components

from formatter.claude_client import transform_text
from formatter.hwpx_reader import read_hwpx_bytes

st.set_page_config(page_title="네이버 블로그 서식 변환기", layout="wide")
st.title("네이버 블로그 서식 변환기")

col_left, col_right = st.columns(2, gap="large")

# ── Left: Input ────────────────────────────────────────────────────────────────
with col_left:
    st.subheader("글감 입력")
    tab1, tab2 = st.tabs(["텍스트 입력", "hwpx 업로드"])
    raw_text = ""

    with tab1:
        text_input = st.text_area("글감을 붙여넣으세요", height=500, key="text_input", label_visibility="collapsed")
        if text_input:
            raw_text = text_input

    with tab2:
        uploaded = st.file_uploader("hwpx 파일 업로드", type=["hwpx"])
        if uploaded:
            try:
                raw_text = read_hwpx_bytes(uploaded.read())
                st.success("변환 완료")
                st.text_area("변환된 텍스트 미리보기", value=raw_text, height=400, disabled=True)
            except Exception as e:
                st.error(f"hwpx 변환 실패: {e}")

    if st.button("변환하기", type="primary", disabled=not bool(raw_text), use_container_width=True):
        with st.spinner("Claude AI가 서식을 적용하는 중..."):
            try:
                st.session_state["result_html"] = transform_text(raw_text)
            except Exception as e:
                st.error(f"변환 실패: {e}")

# ── Right: Result ──────────────────────────────────────────────────────────────
with col_right:
    st.subheader("변환 결과")
    st.markdown('<div style="height:58px"></div>', unsafe_allow_html=True)

    if "result_html" in st.session_state:
        html = st.session_state["result_html"]

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

        st.markdown(
            """
            <style>
            .preview-box {
                border: 1.5px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px 24px;
                background: #fafafa;
                min-height: 460px;
                font-family: "맑은 고딕", sans-serif;
                font-size: 15px;
                line-height: 2;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="preview-box">{html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            .preview-empty {
                border: 1.5px dashed #d0d0d0;
                border-radius: 10px;
                padding: 20px 24px;
                background: #fafafa;
                min-height: 460px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
                font-size: 14px;
            }
            </style>
            <div class="preview-empty">변환 결과가 여기에 표시됩니다</div>
            """,
            unsafe_allow_html=True,
        )
