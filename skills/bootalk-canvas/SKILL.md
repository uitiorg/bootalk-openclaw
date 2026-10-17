---
name: bootalk_canvas
description: Slack 캔버스 생성, 수정, 채널 캔버스 관리. "캔버스 만들어줘", "XX 채널에 캔버스 추가", "캔버스 내용 수정", "채널 문서 업데이트" 등.
metadata:
  codex:
    requires:
      env: [SLACK_BOT_TOKEN]
      bins: [curl, python3]
---

# Slack Canvas 관리

참고: [상세 API 레퍼런스](../../docs/slack-canvas-api.md)

## When to Use
- "XX 채널에 캔버스 만들어줘"
- "캔버스에 내용 추가해줘"
- "채널 문서 업데이트"
- 기존 텍스트 메시지를 캔버스 포스트로 전환

## 핵심 제약 (반드시 숙지)

1. **Free 플랜** → `canvases.create`에 `channel_id` 필수
2. **캔버스 읽기**: `canvases.sections.lookup`은 ID만 반환. **실제 내용은 `files.info` → `url_private_download`로 HTML 다운로드**
3. **채널당 캔버스 1개** → `conversations.canvases.create`는 채널에 이미 있으면 에러
4. **blockquote 안에 list 금지** → `canvas_creation_failed` 에러 발생
5. **section_types 최대 3개**, `contains_text` 빈 문자열 불가

---

## Commands

### 캔버스 내용 읽기 (files.info → url_private_download)

```python
python3 - <<PYEOF
import subprocess, json, re

def read_canvas(canvas_id):
    r = subprocess.run([
        "curl", "-s", "-H", f"Authorization: Bearer $SLACK_BOT_TOKEN",
        f"https://slack.com/api/files.info?file={canvas_id}"
    ], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if not d.get("ok"):
        return f"에러: {d.get('error')}"
    dl_url = d["file"]["url_private_download"]
    title = d["file"].get("title", "")

    r2 = subprocess.run([
        "curl", "-s", "-L", "-H", f"Authorization: Bearer $SLACK_BOT_TOKEN", dl_url
    ], capture_output=True, text=True)

    html = r2.stdout
    html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', html, flags=re.DOTALL)
    html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', html, flags=re.DOTALL)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', html, flags=re.DOTALL)
    html = re.sub(r'<b>(.*?)</b>', r'**\1**', html, flags=re.DOTALL)
    html = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.DOTALL)
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'&amp;', '&', html)
    html = re.sub(r'&nbsp;', ' ', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    return f"## {title}\n\n{html.strip()}"

# 여러 캔버스 동시 읽기
canvas_ids = ["F0APQ0CF81M", "F0B18K9JQKV"]  # 원하는 캔버스 ID 목록
for cid in canvas_ids:
    print(read_canvas(cid))
    print("\n---\n")
PYEOF
```

### 새 캔버스 생성

```bash
CHANNEL="C0APYE7MLEN"  # 채널 ID
TITLE="캔버스 제목"
MARKDOWN="# 제목\n\n내용\n\n- 항목 1\n- 항목 2\n"

python3 - <<PYEOF
import subprocess, json

payload = json.dumps({
    "channel_id": "$CHANNEL",
    "title": "$TITLE",
    "document_content": {
        "type": "markdown",
        "markdown": "$MARKDOWN"
    }
})

r = subprocess.run([
    "curl", "-s", "-X", "POST",
    "-H", f"Authorization: Bearer $SLACK_BOT_TOKEN",
    "-H", "Content-Type: application/json; charset=utf-8",
    "https://slack.com/api/canvases.create",
    "-d", payload
], capture_output=True, text=True)

d = json.loads(r.stdout)
if d.get("ok"):
    print("생성 완료:", d["canvas_id"])
else:
    print("에러:", d.get("error"), d.get("detail", ""))
PYEOF
```

### 채널 전용 캔버스 생성 (채널 탭에 고정)

```bash
python3 - <<PYEOF
import subprocess, json

r = subprocess.run([
    "curl", "-s", "-X", "POST",
    "-H", "Authorization: Bearer $SLACK_BOT_TOKEN",
    "-H", "Content-Type: application/json; charset=utf-8",
    "https://slack.com/api/conversations.canvases.create",
    "-d", json.dumps({
        "channel_id": "C0APYE7MLEN",
        "title": "채널 캔버스",
        "document_content": {"type": "markdown", "markdown": "# 내용\n\n..."}
    })
], capture_output=True, text=True)

d = json.loads(r.stdout)
print("OK:", d["canvas_id"]) if d.get("ok") else print("에러:", d.get("error"))
PYEOF
```

### 캔버스 끝에 내용 추가

```bash
CANVAS_ID="F0XXXXXX"

curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.edit" \
  -d "{
    \"canvas_id\": \"$CANVAS_ID\",
    \"changes\": [{
      \"operation\": \"insert_at_end\",
      \"document_content\": {
        \"type\": \"markdown\",
        \"markdown\": \"## 새 섹션\n\n추가 내용\n\"
      }
    }]
  }" | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if d.get('ok') else d.get('error'))"
```

### 섹션 ID 조회 (edit 전에 필요할 때)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.sections.lookup" \
  -d "{\"canvas_id\": \"$CANVAS_ID\", \"criteria\": {\"section_types\": [\"h1\", \"h2\", \"h3\"]}}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(s['id']) for s in d.get('sections',[])]"
```

### 캔버스 접근 권한 설정

```bash
# 특정 사용자에게 write 권한
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.access.set" \
  -d "{\"canvas_id\": \"$CANVAS_ID\", \"access_level\": \"write\", \"user_ids\": [\"U0APRS4J70B\"]}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if d.get('ok') else d.get('error'))"
```

## 부톡 채널-캔버스 매핑

> 마지막 동기화: 2026-05-06. 활성 채널 10개. 채널/캔버스 변경 시 함께 갱신.

### 전사 채널

| 채널 | 채널 ID | 캔버스 |
|------|---------|--------|
| #전체메세지 | C0B1T0GSP89 | F0B1TTD3VSM (공지사항 필수 정보), F0B1TT7GUU9 ([아카이브] 네이버 바로가기) |
| #부톡-온보딩 | C0APW641YA2 | F0APZ1GRWMR (온보딩 가이드), F0B18K9JQKV (업무 규칙), F0B299C95CY (핵심 가치 & 철학), F0B1TTAPWC9 (연차 규정) |
| #cs | C0APWC7RSSJ | — |
| #중개팀 | C0AQ226BMSQ | F0AQ91JMF2Q (중개사 운영 가이드), F0APQ06US79 ([아카이브] 중개사 계정 등록), F0B1TTJD40H (중개팀 외부업무 보고 가이드) — 외부 공인중개사가 함께 있는 채널 (부톡 서비스 운영 파트너) |
| #zerro제로 | C0B1B3YNSGM | F0B1Y4B2B2N (ZERRO 서비스 종합 정리) |

### 직군별 채널

| 채널 | 채널 ID | 캔버스 |
|------|---------|--------|
| #bootalk-products | C0APYE7MLEN | F0APQ0CF81M (개발팀 핵심 참조), F0AQZMPL5TJ (앱 테스트 방법), F0B1JAAL1KN (개발팀 TODO) |
| 🔒#dev-private | C0APWC6KXQE | F0B1889URS7 (개발서버 정보) |
| #mktg-sales | C0APV20P03X | F0AR0A45X8Q (단지 링크 공유 가이드), F0AQKCN9WE5 (마케팅/영업 참조) |
| #design | C0APT0W6B43 | — |
| 🔒#admin | C0AQSN4B680 | F0AQ9KJ64CU (대표이사 중임 신청서류), F0AQKCR4SHF (어드민 참조 자료) |

### 아카이브된 채널 (참고)

| 채널 | 채널 ID | 비고 |
|------|---------|------|
| #회사내규 | C0AQSN880NL | 캔버스 #부톡-온보딩 으로 통합 (2026-05-04) |
| #업무규칙 | C0AQSN8AEGY | 캔버스 #부톡-온보딩 으로 통합 (2026-05-04) |
| #공지사항 | C0APYE86NAW | 캔버스 #전체메세지 로 이전 (2026-05-04) |
| #developers | C0AQSUFK5Q9 | #dev-private 으로 통합 (2026-04-28) |

## Response Format
결과를 한국어로:
- 생성/수정 성공 여부 + canvas_id
- 에러 시 원인과 해결 방법
