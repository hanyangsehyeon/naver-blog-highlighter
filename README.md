# 네이버 블로그 서식 변환기

글감을 붙여넣거나 `.hwpx` 파일을 업로드하면 Claude AI가 네이버 블로그에 바로 붙여넣을 수 있는 서식(형광펜, 글자색, 볼드)을 자동으로 적용해줍니다.

## 기능

- 텍스트 직접 입력 또는 `.hwpx` 파일 업로드
- Claude Sonnet이 서식 규칙에 따라 HTML 자동 생성
- 미리보기 + 클립보드에 서식 포함 복사 (네이버 블로그 에디터에 바로 붙여넣기 가능)

## 로컬 실행

```bash
pip install -r requirements.txt
```

`.env` 파일 생성:

```
ANTHROPIC_API_KEY=your_api_key_here
```

```bash
streamlit run app.py
```

## Streamlit Cloud 배포

1. 이 repo를 fork 또는 clone 후 GitHub에 push
2. [share.streamlit.io](https://share.streamlit.io) 에서 repo 연결
3. **Settings → Secrets**에 아래 내용 추가:

```toml
ANTHROPIC_API_KEY = "your_api_key_here"
```
