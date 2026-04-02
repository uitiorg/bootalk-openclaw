#!/usr/bin/env python3
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
  python3 cal.py leaves              # 이번 달 연차 현황
"""
import sys
import os
from datetime import datetime, timedelta, date
import pytz

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE    = os.path.join(SCRIPT_DIR, "token.json")
CREDS_FILE    = os.path.join(SCRIPT_DIR, "credentials.json")
CALENDAR_NAME = "부톡 팀 캘린더"
LEAVE_CAL     = "부톡 연차"
KST           = pytz.timezone("Asia/Seoul")
SCOPES        = ["https://www.googleapis.com/auth/calendar"]


def get_service():
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
    return build("calendar", "v3", credentials=creds)


def get_calendar_id(service, name):
    cals = service.calendarList().list().execute().get("items", [])
    for c in cals:
        if c.get("summary") == name:
            return c["id"]
    print(f"❌ '{name}' 캘린더를 찾을 수 없습니다.")
    sys.exit(1)


# ─── agenda: 향후 N일 일정 조회 ──────────────────────────────────────────────
def cmd_agenda(service, days=7):
    cal_id = get_calendar_id(service, CALENDAR_NAME)
    now = datetime.now(KST)
    end = now + timedelta(days=days)

    events = service.events().list(
        calendarId=cal_id,
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute().get("items", [])

    print(f"\n📅 {CALENDAR_NAME} — 향후 {days}일\n")
    if not events:
        print("  (일정 없음)")
        return

    current_date = None
    for e in events:
        start = e["start"].get("dateTime") or e["start"].get("date")
        if "T" in start:
            dt = datetime.fromisoformat(start).astimezone(KST)
            date_str = dt.strftime("%m/%d (%a)")
            time_str = dt.strftime("%H:%M")
        else:
            dt = datetime.strptime(start, "%Y-%m-%d")
            date_str = dt.strftime("%m/%d (%a)")
            time_str = "종일"
        if date_str != current_date:
            print(f"  {date_str}")
            current_date = date_str
        print(f"    {time_str}  {e.get('summary', '(제목 없음)')}")
    print()


# ─── add: 이벤트 추가 ─────────────────────────────────────────────────────────
def cmd_add(service, title, start_str, duration_min=60, allday=False):
    cal_id = get_calendar_id(service, CALENDAR_NAME)

    if allday:
        try:
            datetime.strptime(start_str.strip(), "%Y-%m-%d")
        except ValueError:
            print("❌ 날짜 형식: YYYY-MM-DD")
            sys.exit(1)
        body = {
            "summary": title,
            "start": {"date": start_str.strip()},
            "end":   {"date": start_str.strip()},
        }
    else:
        try:
            dt_start = KST.localize(datetime.strptime(start_str.strip(), "%Y-%m-%d %H:%M"))
        except ValueError:
            print("❌ 날짜/시간 형식: 'YYYY-MM-DD HH:MM'")
            sys.exit(1)
        dt_end = dt_start + timedelta(minutes=int(duration_min))
        body = {
            "summary": title,
            "start": {"dateTime": dt_start.isoformat(), "timeZone": "Asia/Seoul"},
            "end":   {"dateTime": dt_end.isoformat(),   "timeZone": "Asia/Seoul"},
        }

    event = service.events().insert(calendarId=cal_id, body=body).execute()
    print(f"✅ 이벤트 추가: {title}")
    print(f"   시작: {event['start'].get('dateTime') or event['start'].get('date')}")
    print(f"   링크: {event.get('htmlLink', '')}")


# ─── leave: 연차 등록 ─────────────────────────────────────────────────────────
def cmd_leave(service, name, date_str, days=1, half_am=False, half_pm=False):
    cal_id = get_calendar_id(service, LEAVE_CAL)

    try:
        start_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        print("❌ 날짜 형식: YYYY-MM-DD")
        sys.exit(1)

    if half_am:
        # 오전 반차: 09:00~13:00
        label = f"[오전 반차] {name}"
        dt_s = KST.localize(datetime.combine(start_date, datetime.strptime("09:00", "%H:%M").time()))
        dt_e = KST.localize(datetime.combine(start_date, datetime.strptime("13:00", "%H:%M").time()))
        body = {
            "summary": label,
            "start": {"dateTime": dt_s.isoformat(), "timeZone": "Asia/Seoul"},
            "end":   {"dateTime": dt_e.isoformat(), "timeZone": "Asia/Seoul"},
        }
    elif half_pm:
        # 오후 반차: 13:00~18:00
        label = f"[오후 반차] {name}"
        dt_s = KST.localize(datetime.combine(start_date, datetime.strptime("13:00", "%H:%M").time()))
        dt_e = KST.localize(datetime.combine(start_date, datetime.strptime("18:00", "%H:%M").time()))
        body = {
            "summary": label,
            "start": {"dateTime": dt_s.isoformat(), "timeZone": "Asia/Seoul"},
            "end":   {"dateTime": dt_e.isoformat(), "timeZone": "Asia/Seoul"},
        }
    else:
        # 종일 / 연속 연차
        label = f"[연차] {name}" if days == 1 else f"[연차 {days}일] {name}"
        end_date = start_date + timedelta(days=int(days))
        body = {
            "summary": label,
            "start": {"date": start_date.isoformat()},
            "end":   {"date": end_date.isoformat()},
        }

    event = service.events().insert(calendarId=cal_id, body=body).execute()
    date_disp = event["start"].get("dateTime") or event["start"].get("date")
    print(f"✅ 연차 등록: {label}")
    print(f"   날짜: {date_disp}")
    print(f"   링크: {event.get('htmlLink', '')}")


# ─── leaves: 이번 달 연차 현황 조회 ─────────────────────────────────────────
def cmd_leaves(service):
    cal_id = get_calendar_id(service, LEAVE_CAL)
    now = datetime.now(KST)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end   = (month_start + timedelta(days=32)).replace(day=1)

    events = service.events().list(
        calendarId=cal_id,
        timeMin=month_start.isoformat(),
        timeMax=month_end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute().get("items", [])

    print(f"\n🏖️  {now.strftime('%Y년 %m월')} 연차 현황\n")
    if not events:
        print("  (등록된 연차 없음)")
        return
    for e in events:
        start = e["start"].get("date") or e["start"].get("dateTime", "")[:10]
        print(f"  {start}  {e.get('summary', '')}")
    print()


# ─── 진입점 ──────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    service = get_service()

    if cmd == "agenda":
        days = int(args[1]) if len(args) > 1 else 7
        cmd_agenda(service, days)

    elif cmd == "add":
        if len(args) < 3:
            print('사용법: cal.py add "제목" "YYYY-MM-DD HH:MM" [분] [--allday]')
            sys.exit(1)
        title    = args[1]
        start    = args[2]
        allday   = "--allday" in args
        duration = int(args[3]) if len(args) > 3 and not args[3].startswith("--") else 60
        cmd_add(service, title, start, duration, allday)

    elif cmd == "leave":
        if len(args) < 3:
            print('사용법: cal.py leave "이름" "YYYY-MM-DD" [일수|--half-am|--half-pm]')
            sys.exit(1)
        name     = args[1]
        date_str = args[2]
        half_am  = "--half-am" in args
        half_pm  = "--half-pm" in args
        days     = int(args[3]) if len(args) > 3 and not args[3].startswith("--") else 1
        cmd_leave(service, name, date_str, days, half_am, half_pm)

    elif cmd == "leaves":
        cmd_leaves(service)

    else:
        print(f"알 수 없는 명령: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
