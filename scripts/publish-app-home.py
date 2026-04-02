#!/usr/bin/env python3
"""
부톡봇 App Home 발행 스크립트
사용: python3 publish-app-home.py [user_id]
  user_id 생략 시 전 팀원에게 일괄 발행
"""
import sys, os, subprocess, json
from datetime import datetime

TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
if not TOKEN:
    print("❌ SLACK_BOT_TOKEN 환경변수가 필요합니다.")
    print("   export SLACK_BOT_TOKEN=xoxb-...")
    sys.exit(1)

TEAM = {
    "U0AQ1RUPF4L": "이훈구",
    "U0APRS4J70B": "주우철",
    "U0AQ1RWGKPW": "이현석",
    "U0APRSH0SNP": "정정일",
    "U0APW6HMNR4": "배지은",
    "U0APGQN76CF": "전유진",
}


def build_home():
    updated = datetime.now().strftime("%Y년 %m월 %d일")
    return {
        "type": "home",
        "blocks": [

            # ── Hero ─────────────────────────────────────────────
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*안녕하세요, 저는 부톡봇이에요* 👋\n말하듯 요청하면 알아서 처리할게요. 명령어 외울 필요 없어요."
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "사용 가이드 열기 →", "emoji": False},
                    "style": "primary",
                    "url": "https://uitiorg.github.io/bootalk-openclaw/",
                    "action_id": "open_guide"
                }
            },
            {"type": "divider"},

            # ── 캘린더 & 연차 ────────────────────────────────────
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "emoji", "name": "calendar"},
                            {"type": "text", "text": "  캘린더 & 연차", "style": {"bold": True}}
                        ]
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*연차 · 반차 등록*\n`나 내일 연차야`\n`4월 20일 오전 반차`\n`28~30일 연차`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*연차 현황 조회*\n`이번 달 누가 쉬어?`\n`이번 달 연차 현황 알려줘`"
                    },
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*팀 일정 추가*\n`오늘 3시 스프린트 회의 잡아줘`\n`4월 10일 배포일 등록해줘`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*일정 조회*\n`이번 주 일정 보여줘`\n`오늘 뭐 있어?`"
                    },
                ]
            },
            {"type": "divider"},

            # ── Slack 관리 ───────────────────────────────────────
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "emoji", "name": "speech_balloon"},
                            {"type": "text", "text": "  Slack 관리", "style": {"bold": True}}
                        ]
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*채널 캔버스*\n`#dev 캔버스 내용 보여줘`\n`업무규칙 캔버스에 추가해줘`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*멤버 관리*\n`#dev에 홍길동 초대해줘`\n`누가 어느 채널에 있어?`"
                    },
                ]
            },
            {"type": "divider"},

            # ── 준비중 ───────────────────────────────────────────
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "emoji", "name": "construction"},
                            {"type": "text", "text": "  곧 추가될 기능", "style": {"bold": True}}
                        ]
                    }
                ]
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "emoji", "name": "warning"},
                                    {"type": "text", "text": " 할 일 관리 · 주간 KPT · 주간 보고서"},
                                    {"type": "text", "text": "  — 구현 완료, 검증 중", "style": {"italic": True}}
                                ]
                            },
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "emoji", "name": "hammer_and_wrench"},
                                    {"type": "text", "text": " 회원·중개사 조회 · 매물 통계"},
                                    {"type": "text", "text": "  — API 연동 필요", "style": {"italic": True}}
                                ]
                            }
                        ]
                    }
                ]
            },

            # ── Footer ───────────────────────────────────────────
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"채널에서 `@부톡봇` 멘션하거나 여기서 DM으로 사용하세요   •   업데이트: {updated}"}
                ]
            }
        ]
    }


def publish(user_id):
    home = build_home()
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", f"Authorization: Bearer {TOKEN}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"user_id": user_id, "view": home}),
         "https://slack.com/api/views.publish"],
        capture_output=True, text=True
    )
    result = json.loads(r.stdout)
    return result.get("ok"), result.get("error", "")


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(TEAM.keys())
    for uid in targets:
        name = TEAM.get(uid, uid)
        ok, err = publish(uid)
        status = "✅" if ok else f"❌ {err}"
        print(f"  {name} ({uid})  {status}")
