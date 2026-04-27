# 연차 신청 시 이메일 자동 발송 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 부톡봇으로 연차/반차가 등록되면 캘린더 등록 직후 `holiday.uiti@gmail.com`으로 알림 이메일 1통을 자동 발송한다.

**Architecture:** 단일 파일 확장 — `scripts/cal.py`의 기존 OAuth credentials에 `gmail.send` 스코프를 추가하고, `cmd_leave()` 끝에서 `notify_email()`을 호출한다. From display name과 Reply-To 헤더를 활용해 발송은 `cdo.bootalk@gmail.com` 단일 계정에서 하되 시각적으로는 신청자 본인이 보낸 것처럼 표시한다.

**Tech Stack:** Python 3.12, `google-api-python-client`, `google-auth-oauthlib`, `pytz`, `unittest` (built-in, pytest로도 실행 가능)

**관련 spec:** `docs/superpowers/specs/2026-04-27-leave-email-notification-design.md`

---

## File Structure

| 파일 | 작업 | 역할 |
|---|---|---|
| `scripts/cal.py` | Modify | 메인 CLI. SCOPES 확장, 헬퍼 함수 추가, `cmd_leave()` 확장, 반차 시간 변경, 캘린더 제목 형식 변경 |
| `scripts/test_cal.py` | **Create** | 순수 함수에 대한 unit test (`unittest.TestCase` 기반) |
| `skills/bootalk-calendar/SKILL.md` | Modify | 반차 시간 표기 갱신, 이메일 발송 동작 문서화 |
| `scripts/token.json` | Delete (수동) | SCOPES 변경 후 OAuth 재인증을 강제하기 위해 1회 삭제. 다음 실행 시 자동 재발급 |

`cal.py`에 모든 헬퍼/이메일 코드를 같이 두는 이유: 현재 ~250줄로 충분히 작고, 캘린더와 이메일이 같은 OAuth credentials를 공유하기 때문에 분리 비용이 이득보다 큼. 향후 다른 알림 채널이 늘어나면 그때 분리.

---

## Task 1: 테스트 스캐폴딩 + `leave_type_label()` 헬퍼

**Files:**
- Create: `scripts/test_cal.py`
- Modify: `scripts/cal.py` (헬퍼 함수 추가)

순수 함수부터 TDD로 시작. `cmd_leave()` 안에 박혀 있는 라벨 빌딩 로직을 추출.

- [ ] **Step 1: failing test 작성**

`scripts/test_cal.py`를 새로 만들고 다음 내용 작성:

```python
"""scripts/cal.py 의 순수 함수 unit test."""
import unittest
from cal import leave_type_label


class TestLeaveTypeLabel(unittest.TestCase):
    def test_full_day_single(self):
        self.assertEqual(leave_type_label(days=1, half_am=False, half_pm=False), "연차")

    def test_full_day_multi(self):
        self.assertEqual(leave_type_label(days=3, half_am=False, half_pm=False), "연차 3일")

    def test_half_am(self):
        self.assertEqual(leave_type_label(days=1, half_am=True, half_pm=False), "오전반차")

    def test_half_pm(self):
        self.assertEqual(leave_type_label(days=1, half_am=False, half_pm=True), "오후반차")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: test 실행 → fail 확인**

```bash
cd /Users/juucheol/Bootalk/bootalk-openclaw/scripts
python3 -m unittest test_cal -v
```

Expected: `ImportError: cannot import name 'leave_type_label' from 'cal'`

- [ ] **Step 3: minimal 구현**

`scripts/cal.py`의 line 28 직후 (SCOPES 다음 빈 줄 뒤)에 헬퍼 함수 추가:

```python
# ─── 순수 헬퍼 ───────────────────────────────────────────────────────────────
def leave_type_label(days: int, half_am: bool, half_pm: bool) -> str:
    """연차 종류 라벨. 캘린더 이벤트 제목과 이메일 제목/본문에서 공유."""
    if half_am:
        return "오전반차"
    if half_pm:
        return "오후반차"
    if days == 1:
        return "연차"
    return f"연차 {days}일"
```

- [ ] **Step 4: test 실행 → pass 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `OK` (4 tests passed)

- [ ] **Step 5: commit**

```bash
git add scripts/test_cal.py scripts/cal.py
git commit -m "refactor(cal): extract leave_type_label helper with tests"
```

---

## Task 2: `format_email_subject()` 헬퍼

**Files:**
- Modify: `scripts/test_cal.py` (테스트 추가)
- Modify: `scripts/cal.py` (헬퍼 추가)

이메일 제목: `[오전반차] 26.05.01 주우철` 형식.

- [ ] **Step 1: failing test 추가**

`scripts/test_cal.py`의 마지막 `if __name__ == "__main__":` 직전에 다음 클래스 추가:

```python
from datetime import date as _date
from cal import format_email_subject


class TestFormatEmailSubject(unittest.TestCase):
    def test_half_am(self):
        result = format_email_subject("주우철", "오전반차", _date(2026, 5, 1))
        self.assertEqual(result, "[오전반차] 26.05.01 주우철")

    def test_half_pm(self):
        result = format_email_subject("정정일", "오후반차", _date(2026, 4, 28))
        self.assertEqual(result, "[오후반차] 26.04.28 정정일")

    def test_full_day_single(self):
        result = format_email_subject("이현석", "연차", _date(2026, 6, 15))
        self.assertEqual(result, "[연차] 26.06.15 이현석")

    def test_full_day_multi(self):
        result = format_email_subject("배지은", "연차 3일", _date(2026, 7, 1))
        self.assertEqual(result, "[연차 3일] 26.07.01 배지은")
```

- [ ] **Step 2: test 실행 → fail 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `ImportError: cannot import name 'format_email_subject'`

- [ ] **Step 3: 구현**

`scripts/cal.py`의 `leave_type_label()` 다음에 추가:

```python
def format_email_subject(name: str, leave_type: str, start_date) -> str:
    """이메일 제목: [라벨] YY.MM.DD 이름 — 날짜 포함."""
    return f"[{leave_type}] {start_date.strftime('%y.%m.%d')} {name}"
```

- [ ] **Step 4: test 실행 → pass 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `OK` (8 tests passed)

- [ ] **Step 5: commit**

```bash
git add scripts/test_cal.py scripts/cal.py
git commit -m "feat(cal): add format_email_subject helper"
```

---

## Task 3: `format_email_body()` 헬퍼

**Files:**
- Modify: `scripts/test_cal.py`
- Modify: `scripts/cal.py`

본문 5필드: 신청자, 일자, 종류, 신청일시, 신청 경로. 직책은 표기하지 않음 (spec 섹션 8).

- [ ] **Step 1: failing test 추가**

`scripts/test_cal.py`의 `if __name__` 직전에 추가:

```python
from datetime import datetime as _datetime
from cal import format_email_body, KST


class TestFormatEmailBody(unittest.TestCase):
    def setUp(self):
        # 신청일시를 결정적으로 만들기 위해 고정값 주입
        self.now = KST.localize(_datetime(2026, 4, 27, 14, 32))

    def test_half_am(self):
        body = format_email_body(
            name="주우철",
            leave_type="오전반차",
            start_date=_date(2026, 5, 1),
            days=1,
            time_range="09:30–13:30",
            now=self.now,
        )
        self.assertIn("신청자: 주우철", body)
        self.assertIn("일자: 2026-05-01", body)
        self.assertIn("종류: 오전반차 (09:30–13:30)", body)
        self.assertIn("신청일시: 2026-04-27 14:32 KST", body)
        self.assertIn("신청 경로: 부톡봇 (Slack)", body)
        self.assertNotIn("CDO", body)  # 직책 표기 금지

    def test_full_day_multi_includes_end_date(self):
        body = format_email_body(
            name="정정일",
            leave_type="연차 3일",
            start_date=_date(2026, 5, 1),
            days=3,
            time_range="종일",
            now=self.now,
        )
        # 다중일은 "일자: 시작 ~ 종료" 형식
        self.assertIn("2026-05-01", body)
        self.assertIn("2026-05-03", body)
        self.assertIn("~", body)

    def test_full_day_single_no_range(self):
        body = format_email_body(
            name="이현석",
            leave_type="연차",
            start_date=_date(2026, 6, 1),
            days=1,
            time_range="종일",
            now=self.now,
        )
        # 1일은 ~ 표기 없음
        self.assertNotIn("~", body)
```

- [ ] **Step 2: test 실행 → fail 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `ImportError: cannot import name 'format_email_body'`

- [ ] **Step 3: 구현**

`scripts/cal.py`의 `format_email_subject()` 다음에 추가:

```python
_WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def format_email_body(name, leave_type, start_date, days, time_range, now):
    """이메일 본문 5줄. 직책은 의도적으로 표기하지 않음."""
    weekday = _WEEKDAY_KR[start_date.weekday()]
    if days > 1:
        end_date = start_date + timedelta(days=days - 1)
        date_line = f"일자: {start_date.isoformat()} ({weekday}) ~ {end_date.isoformat()}"
    else:
        date_line = f"일자: {start_date.isoformat()} ({weekday})"

    lines = [
        f"신청자: {name}",
        date_line,
        f"종류: {leave_type} ({time_range})",
        f"신청일시: {now.strftime('%Y-%m-%d %H:%M KST')}",
        "신청 경로: 부톡봇 (Slack)",
    ]
    return "\n".join(lines)
```

- [ ] **Step 4: test 실행 → pass 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `OK` (11 tests passed)

- [ ] **Step 5: commit**

```bash
git add scripts/test_cal.py scripts/cal.py
git commit -m "feat(cal): add format_email_body helper"
```

---

## Task 4: `TEAM_EMAILS` + `resolve_reply_to()` 헬퍼

**Files:**
- Modify: `scripts/test_cal.py`
- Modify: `scripts/cal.py`

이름 → 본인 이메일 매핑. spec 원칙에 따라 dict는 코드에만, docs에는 노출하지 않음.

- [ ] **Step 1: failing test 추가**

`scripts/test_cal.py`의 `if __name__` 직전에 추가:

```python
from cal import resolve_reply_to


class TestResolveReplyTo(unittest.TestCase):
    def test_known_name(self):
        # 매핑이 있으면 본인 이메일 반환
        self.assertEqual(resolve_reply_to("주우철"), "cdo.bootalk@gmail.com")
        self.assertEqual(resolve_reply_to("이훈구"), "ceo.uiti@gmail.com")
        self.assertEqual(resolve_reply_to("이현석"), "leehs.uiti@gmail.com")
        self.assertEqual(resolve_reply_to("정정일"), "jji.bootalk@gmail.com")
        self.assertEqual(resolve_reply_to("배지은"), "bje.uiti@gmail.com")
        self.assertEqual(resolve_reply_to("전유진"), "cyj.uiti@gmail.com")

    def test_unknown_name_returns_none(self):
        # 매핑에 없으면 None — Reply-To 헤더 자체를 생략하기 위함
        self.assertIsNone(resolve_reply_to("홍길동"))
        self.assertIsNone(resolve_reply_to(""))
```

- [ ] **Step 2: test 실행 → fail 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `ImportError: cannot import name 'resolve_reply_to'`

- [ ] **Step 3: 구현**

`scripts/cal.py`의 `format_email_body()` 다음에 추가:

```python
# 한국어 이름 → 본인 이메일. spec 원칙에 따라 docs에 노출하지 않음.
TEAM_EMAILS = {
    "주우철":  "cdo.bootalk@gmail.com",
    "이훈구":  "ceo.uiti@gmail.com",
    "이현석":  "leehs.uiti@gmail.com",
    "정정일":  "jji.bootalk@gmail.com",
    "배지은":  "bje.uiti@gmail.com",
    "전유진":  "cyj.uiti@gmail.com",
}


def resolve_reply_to(name: str):
    """이름이 매핑에 있으면 이메일, 없으면 None (Reply-To 헤더 생략)."""
    return TEAM_EMAILS.get(name)
```

- [ ] **Step 4: test 실행 → pass 확인**

```bash
python3 -m unittest test_cal -v
```

Expected: `OK` (13 tests passed)

- [ ] **Step 5: commit**

```bash
git add scripts/test_cal.py scripts/cal.py
git commit -m "feat(cal): add TEAM_EMAILS mapping and resolve_reply_to"
```

---

## Task 5: `cmd_leave()` 캘린더 동작 변경 (반차 시간 + 제목 형식)

**Files:**
- Modify: `scripts/cal.py:131-174` (`cmd_leave` 함수)

캘린더 등록 부분만 먼저 변경. 이메일 호출은 Task 8에서 추가.

변경 항목:
1. `[오전 반차]` → `[오전반차]` (괄호 안 공백 제거)
2. `[오후 반차]` → `[오후반차]`
3. 오전 반차 시간 09:00–13:00 → 09:30–13:30
4. 오후 반차 시간 13:00–18:00 → 13:30–18:30
5. `leave_type_label()` 헬퍼 사용으로 라벨 빌딩 일원화

이 단계에서는 자동화된 unit test는 추가하지 않음 (Google Calendar API I/O 포함). 대신 매뉴얼 검증.

- [ ] **Step 1: 코드 변경**

`scripts/cal.py:140-168` 블록 전체를 다음으로 교체:

```python
    leave_type = leave_type_label(int(days), half_am, half_pm)
    label = f"[{leave_type}] {name}"

    if half_am:
        # 오전 반차: 09:30~13:30
        dt_s = KST.localize(datetime.combine(start_date, datetime.strptime("09:30", "%H:%M").time()))
        dt_e = KST.localize(datetime.combine(start_date, datetime.strptime("13:30", "%H:%M").time()))
        body = {
            "summary": label,
            "start": {"dateTime": dt_s.isoformat(), "timeZone": "Asia/Seoul"},
            "end":   {"dateTime": dt_e.isoformat(), "timeZone": "Asia/Seoul"},
        }
    elif half_pm:
        # 오후 반차: 13:30~18:30
        dt_s = KST.localize(datetime.combine(start_date, datetime.strptime("13:30", "%H:%M").time()))
        dt_e = KST.localize(datetime.combine(start_date, datetime.strptime("18:30", "%H:%M").time()))
        body = {
            "summary": label,
            "start": {"dateTime": dt_s.isoformat(), "timeZone": "Asia/Seoul"},
            "end":   {"dateTime": dt_e.isoformat(), "timeZone": "Asia/Seoul"},
        }
    else:
        # 종일 / 연속 연차
        end_date = start_date + timedelta(days=int(days))
        body = {
            "summary": label,
            "start": {"date": start_date.isoformat()},
            "end":   {"date": end_date.isoformat()},
        }
```

- [ ] **Step 2: 회귀 테스트 (기존 unittest 모두 통과)**

```bash
cd /Users/juucheol/Bootalk/bootalk-openclaw/scripts
python3 -m unittest test_cal -v
```

Expected: `OK` (13 tests still pass — 헬퍼는 변경 없음)

- [ ] **Step 3: 매뉴얼 검증 — 캘린더 등록**

가까운 미래 날짜로 테스트 등록:

```bash
python3 scripts/cal.py leave "주우철" "2026-05-01" --half-am
```

Expected stdout:
```
✅ 연차 등록: [오전반차] 주우철
   날짜: 2026-05-01T09:30:00+09:00
   링크: https://www.google.com/calendar/event?eid=...
```

확인:
- "부톡 연차" Google Calendar에 `[오전반차] 주우철` 이벤트가 09:30–13:30로 생성됨 (대괄호 안 공백 없음)
- 출력 링크를 클릭해 시간 확인

오후 반차도 같이 검증:

```bash
python3 scripts/cal.py leave "주우철" "2026-05-02" --half-pm
```

Expected: 13:30–18:30, 제목 `[오후반차] 주우철`

종일 1일도 검증:

```bash
python3 scripts/cal.py leave "주우철" "2026-05-03"
```

Expected: 종일 이벤트, 제목 `[연차] 주우철`

3일 연속도 검증:

```bash
python3 scripts/cal.py leave "주우철" "2026-05-04" 3
```

Expected: 종일 이벤트 (5/4–5/6), 제목 `[연차 3일] 주우철`

검증 후 캘린더에서 테스트 이벤트 4개 모두 삭제.

- [ ] **Step 4: commit**

```bash
git add scripts/cal.py
git commit -m "refactor(cal): use shared label helper, update half-day hours and title format"
```

---

## Task 6: SCOPES 확장 + OAuth 재인증 절차

**Files:**
- Modify: `scripts/cal.py:27` (SCOPES 라인)

Gmail send 권한을 추가하고, 토큰 파일을 한번 삭제해서 재인증 트리거.

- [ ] **Step 1: SCOPES 변경**

`scripts/cal.py:27`을 다음으로 교체:

```python
SCOPES        = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]
```

- [ ] **Step 2: 기존 토큰 삭제 (수동)**

Bash:
```bash
trash /Users/juucheol/Bootalk/bootalk-openclaw/scripts/token.json 2>/dev/null || true
ls /Users/juucheol/Bootalk/bootalk-openclaw/scripts/token.json 2>&1
```

Expected: `No such file or directory`

(주의: `rm` 금지. `trash` 사용 — `~/.Trash`로 이동, 복구 가능. 이미 없으면 무시.)

- [ ] **Step 3: OAuth 재인증 트리거 (브라우저 동의 필요)**

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda 1
```

Expected:
- 브라우저가 자동으로 열려 Google 로그인 화면 표시
- `cdo.bootalk@gmail.com` 계정 선택
- "Calendar" + "Send email on your behalf" 두 권한 동의
- 동의 완료 후 터미널에 `📅 부톡 팀 캘린더 — 향후 1일` 출력
- `scripts/token.json` 새로 생성됨

확인:

```bash
python3 -c "import json; t=json.load(open('/Users/juucheol/Bootalk/bootalk-openclaw/scripts/token.json')); print('scopes:', t.get('scopes'))"
```

Expected: 두 scope 모두 포함된 리스트.

- [ ] **Step 4: commit (코드 변경만)**

```bash
git add scripts/cal.py
git commit -m "feat(cal): add gmail.send scope to OAuth credentials"
```

(token.json은 .gitignore 대상이거나 어차피 커밋 안 됨 — `git status`로 확인)

---

## Task 7: `notify_email()` 함수 구현

**Files:**
- Modify: `scripts/cal.py` (함수 추가)

Gmail API로 이메일 발송. 호출은 Task 8에서 wire-up.

자동화 테스트는 작성하지 않음 (실제 메일 발송이라 부수 효과). Step 3에서 직접 호출해 검증.

- [ ] **Step 1: 함수 추가**

`scripts/cal.py`의 `cmd_leave()` 함수 정의 *직전*에 다음 추가:

```python
# ─── notify_email: HR에 알림 발송 ─────────────────────────────────────────────
def notify_email(creds, name, leave_type, start_date, days, time_range):
    """holiday.uiti@gmail.com으로 연차 신청 알림 1통 발송.

    From display name은 신청자 한국어 이름.
    Reply-To는 매핑된 신청자 본인 이메일 (없으면 헤더 생략).
    """
    from email.mime.text import MIMEText
    from email.utils import formataddr
    import base64
    from googleapiclient.discovery import build

    sender_email = "cdo.bootalk@gmail.com"
    recipient    = "holiday.uiti@gmail.com"

    subject = format_email_subject(name, leave_type, start_date)
    body    = format_email_body(
        name=name,
        leave_type=leave_type,
        start_date=start_date,
        days=days,
        time_range=time_range,
        now=datetime.now(KST),
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["To"]      = recipient
    msg["From"]    = formataddr((name, sender_email))
    msg["Subject"] = subject

    reply_to = resolve_reply_to(name)
    if reply_to:
        msg["Reply-To"] = reply_to
    else:
        print(f"⚠️  매핑에 없는 신청자 — Reply-To 헤더 생략: {name}", file=sys.stderr)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail = build("gmail", "v1", credentials=creds)
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
```

- [ ] **Step 2: 함수가 import 가능한지만 검증**

```bash
cd /Users/juucheol/Bootalk/bootalk-openclaw/scripts
python3 -c "from cal import notify_email; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 3: 매뉴얼 통합 테스트 — 실제 이메일 1통 발송**

OAuth credentials를 직접 가져와서 함수 호출:

```bash
python3 - <<'PY'
import sys, os
sys.path.insert(0, "/Users/juucheol/Bootalk/bootalk-openclaw/scripts")
from datetime import date
from google.oauth2.credentials import Credentials
from cal import notify_email, SCOPES

creds = Credentials.from_authorized_user_file(
    "/Users/juucheol/Bootalk/bootalk-openclaw/scripts/token.json", SCOPES
)
notify_email(
    creds=creds,
    name="주우철",
    leave_type="오전반차",
    start_date=date(2026, 5, 1),
    days=1,
    time_range="09:30–13:30",
)
print("✅ 발송 완료")
PY
```

Expected:
- `✅ 발송 완료`
- `holiday.uiti@gmail.com` 메일함에 1통 도착 (직접 확인 — 메일 클라이언트 또는 web Gmail)
  - 발신자 표시: `주우철`
  - 제목: `[오전반차] 26.05.01 주우철`
  - 본문: 5줄 구조화 정보
  - Reply-To: `cdo.bootalk@gmail.com`

테스트용 메일 1통이 실제로 HR 메일함에 가는 것이므로 본 테스트는 한 번만 수행. 이후는 Task 8에서 자연 발생.

- [ ] **Step 4: commit**

```bash
git add scripts/cal.py
git commit -m "feat(cal): add notify_email for holiday.uiti@gmail.com notifications"
```

---

## Task 8: `cmd_leave()`에 이메일 통합 + `--no-email` 플래그

**Files:**
- Modify: `scripts/cal.py:131-174` (`cmd_leave` 함수)
- Modify: `scripts/cal.py:226-235` (main의 leave 파싱)
- Modify: `scripts/cal.py:30-47` (`get_service()` — creds 반환)

`cmd_leave`가 캘린더 등록 후 자동으로 `notify_email()`을 호출. `get_service()`가 service 외에 creds도 반환하도록 변경 (notify_email이 creds 필요).

- [ ] **Step 1: `get_service()` 시그니처 변경**

`scripts/cal.py:30-47`의 `get_service()` 함수를 다음으로 교체:

```python
def get_service():
    """Calendar service와 OAuth credentials를 함께 반환. credentials는 Gmail용도."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds), creds
```

- [ ] **Step 2: `main()` 호출 부분 변경**

`scripts/cal.py:210` (`service = get_service()`)을 다음으로 변경:

```python
    service, creds = get_service()
```

- [ ] **Step 3: `cmd_leave()` 시그니처 + 본문 확장**

`scripts/cal.py`의 `cmd_leave()` 함수 시그니처를 변경:

```python
def cmd_leave(service, creds, name, date_str, days=1, half_am=False, half_pm=False, send_email=True):
```

함수 마지막의 `print(f"   링크: ...")` 직후에 다음 추가:

```python
    # 이메일 알림 발송 (실패는 stderr 경고만, 종료 코드 0 유지)
    if send_email:
        try:
            if half_am:
                time_range = "09:30–13:30"
            elif half_pm:
                time_range = "13:30–18:30"
            else:
                time_range = "종일"
            notify_email(creds, name, leave_type, start_date, int(days), time_range)
            print(f"📧 이메일 발송 완료: holiday.uiti@gmail.com")
        except Exception as e:
            print(f"⚠️  이메일 발송 실패 (캘린더는 등록됨): {e}", file=sys.stderr)
```

- [ ] **Step 4: `main()`의 leave 파싱에 `--no-email` 추가**

`scripts/cal.py:226-235` (`elif cmd == "leave":` 블록)을 다음으로 교체:

```python
    elif cmd == "leave":
        if len(args) < 3:
            print('사용법: cal.py leave "이름" "YYYY-MM-DD" [일수|--half-am|--half-pm] [--no-email]')
            sys.exit(1)
        name      = args[1]
        date_str  = args[2]
        half_am   = "--half-am" in args
        half_pm   = "--half-pm" in args
        no_email  = "--no-email" in args
        days_args = [a for a in args[3:] if not a.startswith("--")]
        days      = int(days_args[0]) if days_args else 1
        cmd_leave(service, creds, name, date_str, days, half_am, half_pm, send_email=not no_email)
```

- [ ] **Step 5: 모듈 헤더 docstring 업데이트**

`scripts/cal.py:5-15`의 사용법 블록에 `--no-email` 추가:

```python
"""
부톡 팀 캘린더 CLI

사용법:
  python3 cal.py agenda              # 향후 7일 일정
  python3 cal.py agenda 14           # 향후 14일 일정
  python3 cal.py add "회의" "2026-04-03 14:00" 60    # 1시간짜리 이벤트
  python3 cal.py add "데드라인" "2026-04-05" --allday  # 종일 이벤트
  python3 cal.py leave "이름" "2026-04-10"            # 연차 (종일)
  python3 cal.py leave "이름" "2026-04-10" --half-am  # 오전 반차
  python3 cal.py leave "이름" "2026-04-10" --half-pm  # 오후 반차
  python3 cal.py leave "이름" "2026-04-10" 3          # 3일 연차
  python3 cal.py leave "이름" "2026-04-10" --no-email # 이메일 발송 스킵 (테스트용)
  python3 cal.py leaves              # 이번 달 연차 현황

연차 등록 시 holiday.uiti@gmail.com 으로 자동 알림 메일 1통 발송 (--no-email 옵션으로 끄기 가능).
"""
```

- [ ] **Step 6: unit test 회귀 (모두 pass)**

```bash
cd /Users/juucheol/Bootalk/bootalk-openclaw/scripts
python3 -m unittest test_cal -v
```

Expected: `OK` (13 tests pass)

- [ ] **Step 7: 매뉴얼 통합 테스트 — `--no-email`**

```bash
python3 scripts/cal.py leave "주우철" "2026-05-10" --half-am --no-email
```

Expected stdout:
```
✅ 연차 등록: [오전반차] 주우철
   날짜: 2026-05-10T09:30:00+09:00
   링크: https://...
```
(📧 라인이 **없어야** 함)

`holiday.uiti@gmail.com` 메일함에 새 메일 도착하지 않음 확인.

- [ ] **Step 8: 매뉴얼 통합 테스트 — 정상 발송**

```bash
python3 scripts/cal.py leave "주우철" "2026-05-11" --half-pm
```

Expected stdout:
```
✅ 연차 등록: [오후반차] 주우철
   날짜: 2026-05-11T13:30:00+09:00
   링크: https://...
📧 이메일 발송 완료: holiday.uiti@gmail.com
```

`holiday.uiti@gmail.com`에 메일 1통 도착, 제목 `[오후반차] 26.05.11 주우철`.

테스트용 캘린더 이벤트 2건 삭제.

- [ ] **Step 9: commit**

```bash
git add scripts/cal.py
git commit -m "feat(cal): integrate notify_email into cmd_leave with --no-email flag"
```

---

## Task 9: `bootalk-calendar` SKILL.md 갱신

**Files:**
- Modify: `skills/bootalk-calendar/SKILL.md`

반차 시간 표기 갱신 + 이메일 발송 동작 문서화.

- [ ] **Step 1: 반차 시간 표기 변경**

`skills/bootalk-calendar/SKILL.md`에서 `09:00~13:00` → `09:30~13:30`, `13:00~18:00` → `13:30~18:30` 일괄 치환:

```bash
cd /Users/juucheol/Bootalk/bootalk-openclaw
python3 - <<'PY'
import pathlib
p = pathlib.Path("skills/bootalk-calendar/SKILL.md")
text = p.read_text()
text = text.replace("09:00~13:00", "09:30~13:30")
text = text.replace("13:00~18:00", "13:30~18:30")
p.write_text(text)
print("✅ 시간 표기 갱신")
PY
```

- [ ] **Step 2: 이메일 발송 섹션 추가**

`skills/bootalk-calendar/SKILL.md`의 `### 연차 등록 → 부톡 연차 캘린더` 블록 마지막 코드펜스 직후, `### 연차 현황 조회 → 반드시 leaves` 직전에 새 섹션을 삽입한다. Python heredoc으로 안전하게 수행:

```bash
python3 - <<'PY'
import pathlib
p = pathlib.Path("/Users/juucheol/Bootalk/bootalk-openclaw/skills/bootalk-calendar/SKILL.md")
text = p.read_text()

new_section = """### 자동 이메일 알림

연차/반차 등록 시 자동으로 `holiday.uiti@gmail.com`에 알림 메일 1통이 발송된다.

- 발신: `<신청자 이름> <cdo.bootalk@gmail.com>` (display name = 신청자 본인)
- 제목: `[오전반차] 26.05.01 주우철` 형식
- 본문: 신청자, 일자, 종류, 신청일시, 신청 경로 5줄
- Reply-To: 신청자 본인 이메일 (HR이 답장 시 신청자에게 직접 도달)

이메일 발송 실패는 stderr 경고만 출력하고 캘린더 등록은 유지된다 — 사용자에게 발송 실패 안내 후 수동 재시도 가능.

이메일 발송을 끄려면 `--no-email` 플래그 추가 (테스트/디버그 용도):

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --no-email
```

제3자가 다른 사람의 연차를 등록할 때(예: "정정일 5월 5일 오후 반차 등록해줘")는 발화자가 아니라 **신청 대상자(정정일)** 기준으로 메일 발송.

---

"""

anchor = "### 연차 현황 조회 → 반드시 leaves"
assert anchor in text, f"앵커를 찾을 수 없음: {anchor}"
text = text.replace(anchor, new_section + anchor, 1)
p.write_text(text)
print("✅ 이메일 알림 섹션 삽입")
PY
```

Expected stdout: `✅ 이메일 알림 섹션 삽입`

- [ ] **Step 3: 응답 포맷 가이드 보강**

`skills/bootalk-calendar/SKILL.md`의 `## Response Format` 섹션 끝에 다음 문구 추가:

```markdown
- 연차 등록 응답: 캘린더 등록 결과 + "📧 holiday.uiti@gmail.com 알림 완료" 한 줄. 이메일 발송 실패 시 그 사실을 명시.
```

- [ ] **Step 4: commit**

```bash
git add skills/bootalk-calendar/SKILL.md
git commit -m "docs(skill): document email notification on leave registration"
```

---

## Task 10: End-to-end 통합 테스트 + 부톡봇에 반영

**Files:**
- (변경 없음) `scripts/cal.py`, `skills/bootalk-calendar/SKILL.md`

부톡봇이 `extraDirs`로 cal.py와 SKILL.md를 직접 참조하므로 git pull + post-merge hook이 gateway 재시작. 매뉴얼 트리거도 가능.

- [ ] **Step 1: gateway 재시작 (즉시 반영)**

```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway && sleep 12 && grep -E "gateway.*ready|telegram.*starting|slack.*socket mode connected" ~/.openclaw/logs/gateway.log | tail -5
```

Expected: 
- `[gateway] ready (7 plugins: …)` 신규 라인 출력
- `[slack] socket mode connected` 신규 라인 출력

- [ ] **Step 2: Slack에서 부톡봇과 자연어 대화 테스트**

DM으로 부톡봇에게:

> "5월 13일 오전 반차"

Expected:
- 봇이 `cal.py leave "주우철" "2026-05-13" --half-am` 실행
- 봇이 응답: 캘린더 등록 메시지 + "📧 holiday.uiti@gmail.com 알림 완료"
- 캘린더에 `[오전반차] 주우철` 09:30–13:30 이벤트 생성
- HR 메일함에 메일 1통 도착, 제목 `[오전반차] 26.05.13 주우철`

테스트 후 캘린더 이벤트 삭제. 메일은 HR이 받았어도 테스트라 무시.

- [ ] **Step 3: Slack에서 종일 연차 테스트**

> "5월 14일 연차 등록해줘"

Expected: `[연차] 주우철` 종일 이벤트 + 메일 `[연차] 26.05.14 주우철`.

- [ ] **Step 4: Slack에서 multi-day 테스트**

> "5월 15일부터 3일 연차"

Expected: `[연차 3일] 주우철` 종일 이벤트 (5/15–5/17) + 메일 `[연차 3일] 26.05.15 주우철`.

- [ ] **Step 5: Slack에서 제3자 등록 테스트**

> "정정일 5월 18일 오후 반차 등록해줘"

Expected:
- 캘린더에 `[오후반차] 정정일` 13:30–18:30 이벤트
- 메일 발신자 표시 `정정일`, 제목 `[오후반차] 26.05.18 정정일`, Reply-To `jji.bootalk@gmail.com`

(발화자가 주우철이지만 메일은 정정일 기준 — spec 섹션 9 검증)

- [ ] **Step 6: 회귀 테스트 (기존 기능 영향 없음)**

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda 7
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leaves
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "테스트 회의" "2026-05-20 14:00" 30
```

Expected:
- `agenda`/`leaves` 정상 출력 (이메일 발송 없음 — leave 명령에만 적용)
- `add`도 정상 — 팀 캘린더에 30분 회의 등록

`add` 테스트로 만든 이벤트 삭제.

- [ ] **Step 7: 최종 점검**

`git log --oneline` 확인:

```bash
git log --oneline -10
```

Expected: 본 plan에 의해 만들어진 커밋들이 시간순으로 보임:
- `refactor(cal): extract leave_type_label helper with tests`
- `feat(cal): add format_email_subject helper`
- `feat(cal): add format_email_body helper`
- `feat(cal): add TEAM_EMAILS mapping and resolve_reply_to`
- `refactor(cal): use shared label helper, update half-day hours and title format`
- `feat(cal): add gmail.send scope to OAuth credentials`
- `feat(cal): add notify_email for holiday.uiti@gmail.com notifications`
- `feat(cal): integrate notify_email into cmd_leave with --no-email flag`
- `docs(skill): document email notification on leave registration`

- [ ] **Step 8: 마지막 커밋 (필요 시)**

`git status` clean하면 추가 커밋 없음. 만약 통합 테스트에서 사소한 수정 발생하면:

```bash
git add -A  # 명시적으로 추가된 파일만 — 새 untracked 파일 없는지 git status 확인
git commit -m "fix(cal): <간단한 수정 설명>"
```

---

## Spec 커버리지 요약

| Spec 섹션 | 다루는 Task |
|---|---|
| § 2 결정 사항 | Task 1–9 전반 |
| § 3 아키텍처 | Task 7 (notify_email), Task 8 (wire-up) |
| § 4.1 cal.py 변경 | Task 1–8 |
| § 4.2 SKILL.md 변경 | Task 9 |
| § 4.3 OAuth | Task 6 |
| § 5 시나리오 워크스루 | Task 8 step 7–8, Task 10 step 2 |
| § 6 에러 처리 매트릭스 | Task 8 step 3 (try/except), Task 7 (Reply-To 누락) |
| § 7.1 CLI 단위 테스트 | Task 5 step 3, Task 8 step 7–8 |
| § 7.2 Slack 통합 테스트 | Task 10 |
| § 7.3 회귀 | Task 10 step 6 |
| § 8 비-요구사항 | (해당 없음 — 의도적으로 구현 안 함) |
| § 9 제3자 대리 등록 | Task 10 step 5 |
| § 10 마이그레이션 | Task 6 (re-auth), Task 10 step 1 (gateway) |
