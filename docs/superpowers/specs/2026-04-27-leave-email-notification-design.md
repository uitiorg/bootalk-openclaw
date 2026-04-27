# 연차 신청 시 holiday.uiti@gmail.com 이메일 자동 발송 — 설계

- **작성일:** 2026-04-27
- **상태:** Draft, 사용자 검토 대기
- **범위:** `bootalk-calendar` 스킬 + `scripts/cal.py`에 이메일 알림 부가 기능 추가
- **변경 영향:** 캘린더 등록 동작은 그대로 유지, 등록 직후 이메일 1통 추가 발송. 반차 시간 30분 변경.

---

## 1. 배경

부톡봇은 이미 자연어로 연차/반차를 받아 Google Calendar의 "부톡 연차" 캘린더에 이벤트를 등록한다 (`bootalk-calendar` 스킬 → `scripts/cal.py leave …`). 그러나 HR(holiday.uiti@gmail.com) 측에는 별도 알림이 가지 않아 캘린더를 직접 열어보지 않는 한 신청 사실을 인지하지 못한다.

본 설계는 캘린더 등록 직후 **자동으로 HR 메일함에 알림 메일을 1통 발송**하여, 캘린더 외에도 이메일 트레일을 남기는 것을 목표로 한다.

## 2. 결정 사항

| 항목 | 결정 |
|---|---|
| 승인 절차 | 없음. 신청 즉시 캘린더 등록 + 이메일 발송 |
| 이메일 본문 | 구조화 (신청자·일자·종류·신청일시·신청 경로) |
| 사유 필드 | **없음** |
| 반차 시간 (변경) | 오전 09:30 ~ 13:30 / 오후 13:30 ~ 18:30 (기존 09:00–13:00 / 13:00–18:00 → 30분씩 시프트) |
| 이메일 발송 계정 | 기존 OAuth (`scripts/token.json`) 보유 계정 — `cdo.bootalk@gmail.com` |
| OAuth 변경 | `SCOPES`에 `https://www.googleapis.com/auth/gmail.send` 추가 → 1회 재인증 필요 |
| `From:` 표시 이름 | 신청자의 한국어 이름 (e.g. `주우철 <cdo.bootalk@gmail.com>`) |
| `Reply-To:` | 신청자 본인 이메일 (이름 → 이메일 매핑 dict 기반) |
| 캘린더 이벤트 제목 | `[오전반차] 주우철` (괄호 공백 제거, 날짜 미포함 — 캘린더가 시각적으로 날짜를 보여주므로 중복 제거) |
| 이메일 제목 | `[오전반차] 26.05.01 주우철` (괄호 공백 제거, 날짜 `YY.MM.DD` 포함) |
| 다중일 연차 제목 | `[연차 3일] 26.05.01 주우철` (시작일 + 일수 표시) |
| 실패 처리 | 캘린더 실패 → 종료 코드 1, 이메일 미발송. 이메일 실패 → stderr 경고, 종료 코드 0 (캘린더는 이미 등록됨). |

## 3. 아키텍처

```
Slack 사용자
  │ "내일 오전 반차" / "5월 3일 연차"
  ▼
부톡봇 (OpenClaw gateway, Socket Mode)
  │ bootalk-calendar 스킬 매칭, Slack ID → 한국어 이름
  ▼
python3 scripts/cal.py leave "주우철" "2026-05-03" --half-am
  │
  ├─[a]─ Google Calendar API ─→ "부톡 연차" 캘린더에 이벤트 insert
  │      summary: "[오전반차] 주우철"
  │      time:    09:30 ~ 13:30 KST
  │
  └─[b]─ Gmail API (NEW) ─────→ holiday.uiti@gmail.com
         from:     주우철 <cdo.bootalk@gmail.com>
         reply-to: <신청자 본인 이메일>
         subject:  [오전반차] 26.05.03 주우철
         body:     구조화된 신청 정보
```

[a]와 [b]는 순차 실행. [a] 실패 시 [b] 미실행. [b] 실패는 silent warning.

## 4. 코드 변경 범위

### 4.1 `scripts/cal.py` — 변경

| 변경 | 세부 |
|---|---|
| `SCOPES` 확장 | 기존 `[calendar]` → `[calendar, gmail.send]`. 첫 실행 시 OAuth 재인증 1회 필요 |
| 반차 시간 시프트 | `cmd_leave()` 내 09:00→09:30, 13:00→13:30, 18:00→18:30 |
| 캘린더 제목 형식 | `[오전 반차] 이름` → `[오전반차] 이름`, `[오후 반차] 이름` → `[오후반차] 이름` (괄호 공백만 제거, 날짜는 캘린더 시각 표시에 위임) |
| **신규** `TEAM_EMAILS` dict | 한국어 이름 → 본인 이메일 매핑 (코드 내 하드코드, docs에 노출하지 않음) |
| **신규** `notify_email(name, leave_type, start_date, days, half_am, half_pm)` | MIME 빌드 → base64url 인코딩 → `gmail.users().messages().send(userId='me', …)` |
| `cmd_leave()` 수정 | 캘린더 insert 성공 후 `notify_email(...)` 호출. 예외 발생 시 stderr 출력 후 정상 종료. |
| **신규** `--no-email` 플래그 | 이메일 발송 스킵 (재실행/디버깅 용도) |

### 4.2 `bootalk-calendar` 스킬 (`SKILL.md`) — 변경

- 반차 시간 표기 업데이트: `(09:00~13:00)` → `(09:30~13:30)`, `(13:00~18:00)` → `(13:30~18:30)`
- 응답 포맷에 "이메일 발송 완료" 문구 가이드 추가
- 그 외 라우팅 규칙은 그대로 유지

### 4.3 `OAuth credentials`

- `scripts/credentials.json`은 변경 불필요 (이미 동일 OAuth 클라이언트로 Gmail API도 사용 가능)
- `scripts/token.json`은 SCOPES 변경 후 자동 재발급. 첫 실행 시 사용자가 브라우저에서 Gmail send 권한을 한 번 승인.

## 5. 상세 동작 — 시나리오 워크스루

**시나리오: 주우철이 #dev에서 "내일 오후 반차"라고 입력 (오늘 = 2026-04-27 월)**

1. 부톡봇이 `bootalk-calendar` 스킬에 매칭
2. 스킬이 발화자 Slack ID `U0APRS4J70B` → "주우철" 변환
3. Shell 호출:
   ```bash
   python3 scripts/cal.py leave "주우철" "2026-04-28" --half-pm
   ```
4. `cal.py` 동작:
   - Calendar API insert: `summary="[오후반차] 주우철"`, start `2026-04-28T13:30:00+09:00`, end `2026-04-28T18:30:00+09:00`
   - `notify_email("주우철", "오후반차", date(2026,4,28), days=1, half_am=False, half_pm=True)`:
     - subject: `[오후반차] 26.04.28 주우철`
     - from: `주우철 <cdo.bootalk@gmail.com>`
     - reply-to: `<주우철 본인 이메일>`
     - body:
       ```
       신청자: 주우철
       일자: 2026-04-28 (화)
       종류: 오후 반차 (13:30–18:30)
       신청일시: 2026-04-27 14:32 KST
       신청 경로: 부톡봇 (Slack)
       ```
   - stdout: `✅ 연차 등록 완료 / 📧 이메일 발송 완료`
5. 부톡봇이 #dev에 응답: "✅ 연차 등록: [오후반차] 주우철 / 📧 holiday.uiti@gmail.com 알림 완료"

## 6. 에러 처리 매트릭스

| 실패 지점 | 영향 | 동작 |
|---|---|---|
| Calendar API 실패 | 캘린더 등록 안 됨 | `sys.exit(1)`, 이메일 미발송, 부톡봇이 사용자에게 실패 메시지 |
| Gmail API 실패 (네트워크/쿼터) | 캘린더는 등록됨, HR 통지만 누락 | stderr 경고 출력, 종료 코드 0. 사용자 응답에 "이메일 발송 실패" 명시 후 수동 재시도 안내 |
| 이름이 `TEAM_EMAILS`에 없음 (예: 신규 입사자 미등록) | Reply-To 헤더만 누락 | 메일은 정상 발송, stderr에 매핑 누락 경고 |
| OAuth 토큰 스코프 부족 (재인증 필요) | 첫 배포 직후 1회 발생 가능 | `cal.py`가 `token.json` 삭제 후 재실행 안내 메시지 |
| Multi-day 연차 발송 시 일수 오류 | 종일 연차 1건은 잘 등록되었으나 이메일 제목/본문 일수 불일치 | 단일 source-of-truth (`days` 인자)로 둘 다 생성하여 원천적으로 방지 |

## 7. 테스트 계획

### 7.1 CLI 단위 테스트

```bash
# 종일 연차 1일
python3 scripts/cal.py leave "주우철" "2026-05-01"

# 오전 반차
python3 scripts/cal.py leave "주우철" "2026-05-01" --half-am

# 오후 반차
python3 scripts/cal.py leave "주우철" "2026-05-01" --half-pm

# 3일 연속 연차
python3 scripts/cal.py leave "주우철" "2026-05-01" 3

# 이메일 스킵
python3 scripts/cal.py leave "주우철" "2026-05-01" --no-email

# 미등록 이름 (Reply-To 누락 검증)
python3 scripts/cal.py leave "홍길동" "2026-05-01"
```

각 케이스에 대해 검증 항목:
- [ ] "부톡 연차" 캘린더에 이벤트 1건 생성됨
- [ ] 캘린더 제목이 `[오전반차] 주우철` 형식 (공백 없음, 날짜 없음)
- [ ] 시간이 09:30–13:30 / 13:30–18:30 / 종일
- [ ] holiday.uiti@gmail.com 메일함에 메일 수신 (테스트 시 별도 확인 계정 사용 가능)
- [ ] 메일 제목이 `[오전반차] 26.05.01 주우철` 형식
- [ ] 메일 본문 5개 필드 (신청자/일자/종류/신청일시/신청 경로) 모두 채워짐
- [ ] From display name이 신청자 한국어 이름
- [ ] Reply-To가 신청자 본인 이메일

### 7.2 Slack 통합 테스트

부톡봇 DM 또는 #dev 채널에서:
- "내일 오전 반차" — 오늘 기준 +1일, half-am 동작 확인
- "5월 3일 연차" — 절대 날짜 동작 확인
- "5월 1일부터 3일 연차" — multi-day 동작 확인
- "정정일 5월 5일 오후 반차 등록해줘" — 제3자 등록 시 신청자 표시 (현재 발화자 vs 명령 대상자) 동작 확인 → **결정 필요: 제3자 등록 시 이메일 From은 누구로?**

### 7.3 회귀 (regression)

- `cal.py agenda`, `cal.py leaves`, `cal.py add` 명령은 변경 없음 — 기존 동작 유지 확인

## 8. 비-요구사항 (out of scope)

- 승인 워크플로우 (Q1에서 명시적으로 제외)
- 사유 필드 (Q2에서 명시적으로 제외)
- **직책 표기 제외** — `신청자: 주우철 (CDO)` 식으로 직책을 본문에 붙이지 않음. 봇이 직책 정보를 정확히 보유하지 않으므로 추측하지 않고 이름만 표기. 직책이 필요하면 HR이 별도로 매핑.
- 연차 잔여일수 조회/차감
- 이메일 발송 실패 자동 재시도 (수동 재실행으로 충분)
- HR 측에서 메일 회신 시 봇이 처리 (Reply-To는 신청자 본인을 가리키므로 봇 개입 불필요)
- 캘린더 이벤트의 attendee 필드에 holiday.uiti 추가 (Google이 자동 발송하는 invitation 메일은 제목 형식이 다르므로 사용 안 함)

## 9. 제3자 대리 등록 처리 (해결됨)

Slack에서 제3자가 다른 사람의 연차를 대신 등록할 때 (예: 전유진이 "정정일 5월 5일 오후 반차 등록해줘"):

- **이메일 From display name**: 신청 대상자 (정정일)
- **Reply-To**: 신청 대상자 본인 이메일
- **본문 `신청자` 필드**: 신청 대상자
- **발화자 정보**: 무시. HR 입장에서는 "정정일이 신청한 것"으로 일관 처리.

근거: 본인이 본인 연차를 신청하는 게 일반적이며, 대리 등록 시에도 HR이 추적해야 할 주체는 연차 사용자 본인. 발화자 추적이 필요하면 별도 audit log를 두는 것이 더 적절 (현 스코프 외).

`bootalk-calendar` 스킬은 이미 `cal.py leave "정정일" …`처럼 명령 인자에 신청 대상자 이름을 넘기므로, 이 결정은 `cal.py` 측 추가 변경 없이 자연스럽게 적용된다.

## 10. 마이그레이션 / 배포 단계

1. `cal.py` 코드 변경
2. `SKILL.md` 텍스트 갱신
3. 로컬에서 `token.json` 삭제 → `python3 scripts/cal.py leave "주우철" "<미래 테스트 날짜>"` 실행 → 브라우저에서 Gmail send 권한 승인
4. 자가 테스트 (Section 7.1 전 케이스)
5. 부톡봇이 `cal.py`를 `extraDirs`로 직접 참조하므로, `git pull` → post-merge hook이 gateway 재시작 → 즉시 반영 (`launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway` 수동 트리거도 가능)
6. Slack에서 통합 테스트 (Section 7.2)

---

## 부록 A — 변경 후 cal.py `cmd_leave()` 의사 코드

```python
def cmd_leave(service, name, date_str, days=1, half_am=False, half_pm=False, send_email=True):
    cal_id = get_calendar_id(service, LEAVE_CAL)
    start_date = parse_date(date_str)

    if half_am:
        leave_type = "오전반차"
        time_range = "09:30~13:30"
        body = build_event_body(name, leave_type, start_date, "09:30", "13:30")
    elif half_pm:
        leave_type = "오후반차"
        time_range = "13:30~18:30"
        body = build_event_body(name, leave_type, start_date, "13:30", "18:30")
    else:
        leave_type = "연차" if days == 1 else f"연차 {days}일"
        time_range = "종일"
        body = build_allday_event_body(name, leave_type, start_date, days)

    event = service.events().insert(calendarId=cal_id, body=body).execute()
    print(f"✅ 연차 등록: {body['summary']}")

    if send_email:
        try:
            notify_email(creds, name, leave_type, start_date, days, time_range)
            print("📧 이메일 발송 완료")
        except Exception as e:
            print(f"⚠️  이메일 발송 실패: {e}", file=sys.stderr)
```

## 부록 B — `notify_email()` 의사 코드

```python
def notify_email(creds, name, leave_type, start_date, days, time_range):
    from email.mime.text import MIMEText
    from email.utils import formataddr
    import base64

    sender_email = "cdo.bootalk@gmail.com"
    reply_to = TEAM_EMAILS.get(name)  # None이면 헤더 생략

    subj_date = start_date.strftime("%y.%m.%d")
    subject = f"[{leave_type}] {subj_date} {name}"

    body_lines = [
        f"신청자: {name}",
        f"일자: {start_date.strftime('%Y-%m-%d')} ({weekday_kr(start_date)})"
        + (f" ~ {(start_date + timedelta(days=days-1)).strftime('%Y-%m-%d')}" if days > 1 else ""),
        f"종류: {leave_type_korean(leave_type)} ({time_range})",
        f"신청일시: {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}",
        "신청 경로: 부톡봇 (Slack)",
    ]
    body = "\n".join(body_lines)

    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = "holiday.uiti@gmail.com"
    msg["From"] = formataddr((name, sender_email))
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["Subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    # Calendar 서비스와 동일한 OAuth credentials 객체 재사용
    gmail = build("gmail", "v1", credentials=creds)
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
```
