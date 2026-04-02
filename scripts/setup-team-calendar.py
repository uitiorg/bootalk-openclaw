#!/usr/bin/env python3
"""
부톡 팀 공유 캘린더 생성 & 초대 스크립트

사전 준비:
  Google Cloud Console → APIs & Services → Credentials
  → Create Credentials → OAuth client ID → Desktop app → Download JSON
  → 파일을 scripts/credentials.json 으로 저장

실행:
  python3 setup-team-calendar.py
  (브라우저가 열리면 cdo.bootalk@gmail.com으로 로그인 → 허용)
"""
import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ─── 설정 ───────────────────────────────────────────────────────────────────
CALENDAR_NAME = "부톡 팀 캘린더"
CALENDAR_TIMEZONE = "Asia/Seoul"

TEAM_MEMBERS = [
    {"email": "cdo.bootalk@gmail.com",  "name": "주우철"},
    {"email": "ceo.uiti@gmail.com",     "name": "이훈구"},
    {"email": "leehs.uiti@gmail.com",   "name": "이현석"},
    {"email": "bje.uiti@gmail.com",     "name": "배지은"},
    {"email": "jji.bootalk@gmail.com",  "name": "정정일"},
    {"email": "cyj.uiti@gmail.com",     "name": "전유진"},
]

SCOPES      = ["https://www.googleapis.com/auth/calendar"]
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE  = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_FILE  = os.path.join(SCRIPT_DIR, "token.json")

# ─── OAuth ───────────────────────────────────────────────────────────────────
def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                print("❌ credentials.json 파일이 없습니다.")
                print(f"   위치: {CREDS_FILE}")
                print()
                print("   Google Cloud Console → APIs & Services → Credentials")
                print("   → Create Credentials → OAuth client ID → Desktop app")
                print("   → Download JSON → credentials.json으로 저장")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


# ─── 캘린더 생성 ──────────────────────────────────────────────────────────────
def create_or_find_calendar(service):
    calendars = service.calendarList().list().execute().get("items", [])
    for cal in calendars:
        if cal.get("summary") == CALENDAR_NAME:
            print(f"📅 기존 캘린더 발견: {CALENDAR_NAME} (ID: {cal['id']})")
            return cal["id"]
    cal = service.calendars().insert(body={
        "summary": CALENDAR_NAME,
        "timeZone": CALENDAR_TIMEZONE,
    }).execute()
    print(f"✅ 캘린더 생성: {CALENDAR_NAME} (ID: {cal['id']})")
    return cal["id"]


# ─── 팀원 초대 (편집 권한) ────────────────────────────────────────────────────
def share_with_team(service, calendar_id):
    existing_acl = service.acl().list(calendarId=calendar_id).execute().get("items", [])
    existing_emails = {r.get("scope", {}).get("value", "") for r in existing_acl}

    for member in TEAM_MEMBERS:
        email, name = member["email"], member["name"]
        if email in existing_emails:
            print(f"  ⏭️  {name} ({email}) — 이미 공유됨")
            continue
        try:
            service.acl().insert(calendarId=calendar_id, body={
                "role": "writer",
                "scope": {"type": "user", "value": email},
            }).execute()
            print(f"  ✅ {name} ({email}) — 편집 권한 부여")
        except HttpError as e:
            print(f"  ❌ {name} ({email}) — 오류: {e}")


# ─── 메인 ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("부톡 팀 공유 캘린더 설정")
    print("=" * 55)

    service = get_service()
    calendar_id = create_or_find_calendar(service)

    print("\n👥 팀원 초대 중...")
    share_with_team(service, calendar_id)

    encoded = calendar_id.replace("@", "%40")
    print(f"\n📎 캘린더 링크:")
    print(f"   https://calendar.google.com/calendar/r?cid={encoded}")
    print("\n🎉 완료! 팀원들에게 초대 이메일이 발송됩니다.")


if __name__ == "__main__":
    main()
