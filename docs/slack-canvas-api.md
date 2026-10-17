# Slack Canvas API Reference

> 정확한 사용법. 여기서 벗어나면 에러 납니다.

## 엔드포인트 요약

| Method | Scope | 설명 |
|--------|-------|------|
| `canvases.create` | `canvases:write` | 새 캔버스 생성 |
| `canvases.edit` | `canvases:write` | 캔버스 내용 수정 |
| `canvases.sections.lookup` | `canvases:read` | 섹션 ID 조회 (내용 반환 안 됨) |
| `conversations.canvases.create` | `canvases:write` | 채널 전용 캔버스 생성 |
| `canvases.access.set` | `canvases:write` | 접근 권한 설정 |

---

## canvases.create

```bash
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.create" \
  -d '{
    "title": "캔버스 제목",
    "channel_id": "C0APYE7MLEN",
    "document_content": {
      "type": "markdown",
      "markdown": "# 제목\n\n내용입니다.\n\n- 항목 1\n- 항목 2\n"
    }
  }'
# 응답: { "ok": true, "canvas_id": "F0XXXXXX" }
```

**주의사항:**
- `channel_id` — Free 플랜에서는 **필수**
- `document_content.type` — 항상 `"markdown"`
- markdown에서 blockquote(`>`) 안에 list(`-`) 넣으면 에러남

---

## conversations.canvases.create

채널에 고정되는 캔버스 (채널 탭에 나타남):

```bash
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/conversations.canvases.create" \
  -d '{
    "channel_id": "C0APYE7MLEN",
    "title": "채널 캔버스 제목",
    "document_content": {
      "type": "markdown",
      "markdown": "# 내용\n\n..."
    }
  }'
# 에러: channel_canvas_already_exists (이미 있으면)
```

---

## canvases.edit

기존 캔버스에 내용 추가/수정:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.edit" \
  -d '{
    "canvas_id": "F0XXXXXX",
    "changes": [
      {
        "operation": "insert_at_end",
        "document_content": {
          "type": "markdown",
          "markdown": "## 새 섹션\n\n추가 내용\n"
        }
      }
    ]
  }'
```

**operation 종류:**
- `insert_at_start` / `insert_at_end` — section_id 불필요
- `insert_before` / `insert_after` — section_id 필요
- `replace` / `delete` — section_id 필요
- `rename` — title_content 필요

---

## canvases.sections.lookup

섹션 ID 조회 (내용 텍스트는 반환 안 됨):

```bash
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.sections.lookup" \
  -d '{
    "canvas_id": "F0XXXXXX",
    "criteria": {
      "section_types": ["h1", "h2", "h3"]
    }
  }'
# 응답: { "ok": true, "sections": [{ "id": "temp:C:xxx" }] }
```

**주의사항:**
- `contains_text` — 빈 문자열(`""`) 불가, 반드시 1자 이상
- `section_types` — 최대 3개: `h1`, `h2`, `h3`, `any_header`
- 반환값은 section ID만. **텍스트 내용은 읽을 수 없음** (Canvas 읽기 API 없음)

---

## canvases.access.set

```bash
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://slack.com/api/canvases.access.set" \
  -d '{
    "canvas_id": "F0XXXXXX",
    "access_level": "write",
    "user_ids": ["U0APRS4J70B"]
  }'
```

- `access_level`: `read` / `write` / `owner`
- `channel_ids`와 `user_ids`는 동시 사용 불가

---

## 캔버스 내용 읽기 (files.info + url_private_download)

`canvases.sections.lookup`은 섹션 ID만 반환하지만, **캔버스는 Slack 파일(F...)이므로 `files.info`로 다운로드 URL을 얻어 전체 내용을 HTML로 읽을 수 있다.**

```bash
CANVAS_ID="F0APQ0CF81M"

# 1. 다운로드 URL 획득
DOWNLOAD_URL=$(curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/files.info?file=$CANVAS_ID" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['file']['url_private_download'])")

# 2. HTML 내용 다운로드
curl -s -L -H "Authorization: Bearer $SLACK_BOT_TOKEN" "$DOWNLOAD_URL"
```

응답은 HTML 형식. 텍스트만 추출하려면:

```python
import subprocess, json, re

def read_canvas(canvas_id, token):
    r = subprocess.run([
        "curl", "-s", "-H", f"Authorization: Bearer {token}",
        f"https://slack.com/api/files.info?file={canvas_id}"
    ], capture_output=True, text=True)
    dl_url = json.loads(r.stdout)["file"]["url_private_download"]

    r2 = subprocess.run([
        "curl", "-s", "-L", "-H", f"Authorization: Bearer {token}", dl_url
    ], capture_output=True, text=True)

    html = r2.stdout
    html = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r'\2 (\1)', html)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'&amp;', '&', html)
    html = re.sub(r'\s+', ' ', html).strip()
    return html
```

---

## 알려진 제약

| 제약 | 내용 |
|------|------|
| 캔버스 내용 읽기 | `canvases.sections.lookup`은 ID만 반환. 대신 `files.info` → `url_private_download` 사용 |
| Free 플랜 | canvases.create에 channel_id 필수 |
| blockquote + list | 에러 발생 (지원 안 됨) |
| section_types | 최대 3개 |
| contains_text | 빈 문자열 불가 |
| channel_canvas_already_exists | 채널당 캔버스 1개 제한 |
