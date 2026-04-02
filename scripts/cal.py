#!/usr/bin/env python3
"""
부톡 팀 캘린더 CLI

사용법:
  python3 cal.py agenda              # 향후 7일 일정
  python3 cal.py agenda 14           # 향후 14일 일정
  python3 cal.py add "회의" "2026-04-03 14:00" 60    # 1시간짜리 이벤트
  python3 cal.py add "데드라인" "2026-04-05" --allday  # 종일 이벤트
  python3 cal.py quick "내일 오후 2시 주간회의"        # 자연어 입력
"""
import sys
import os
from datetime import datetime, timedelta, timezone
import pytz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE  = os.path.join(SCRIPT_DIR, "token.json")
CREDS_FILE  = os.path.join(SCRIPT_DIR, "credentials.json")
CALENDAR_NAME = "부톡 팀 캘린더"
KST = pytz.timezone("Asia/Seoul")

SCOPES = ["https://www.googleapis.com/auth/calendar"]


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


def get_calendar_id(service):
    cals = service.calendarList().list().execute().get("items", [])
    for c in cals:
        if c.get("summary") == CALENDAR_NAME:
            return c["id"]
    print(f"❌ '{CALENDAR_NAME}' 캘린더를 찾을 수 없습니다.")
    print("   setup-team-calendar.py를 먼저 실행하세요.")
    sys.exit(1)


# ─── agenda: 향후 N일 일정 조회 ──────────────────────────────────────────────
def cmd_agenda(service, days=7):
    cal_id = get_calendar_id(service)
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

        title = e.get("summary", "(제목 없음)")
        print(f"    {time_str}  {title}")
    print()


# ─── add: 이벤트 추가 ─────────────────────────────────────────────────────────
def cmd_add(service, title, start_str, duration_min=60, allday=False):
    cal_id = get_calendar_id(service)

    if allday:
        # 종일 이벤트
        date_str = start_str.strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("❌ 종일 이벤트 날짜 형식: YYYY-MM-DD")
            sys.exit(1)
        body = {
            "summary": title,
            "start": {"date": date_str},
            "end":   {"date": date_str},
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
    link = event.get("htmlLink", "")
    start_disp = event["start"].get("dateTime") or event["start"].get("date")
    print(f"✅ 이벤트 추가: {title}")
    print(f"   시작: {start_disp}")
    print(f"   링크: {link}")


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
            print("사용법: cal.py add \"제목\" \"YYYY-MM-DD HH:MM\" [분] [--allday]")
            sys.exit(1)
        title    = args[1]
        start    = args[2]
        allday   = "--allday" in args
        duration = int(args[3]) if len(args) > 3 and not args[3].startswith("--") else 60
        cmd_add(service, title, start, duration, allday)

    else:
        print(f"알 수 없는 명령: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
