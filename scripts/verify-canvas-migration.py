#!/usr/bin/env python3
"""
WORKS → Slack Canvas Migration Verifier
Usage: SLACK_BOT_TOKEN=xoxb-... python3 verify-canvas-migration.py
"""
import subprocess, json, re, os, sys
from datetime import datetime

BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
if not BOT_TOKEN:
    print("❌ SLACK_BOT_TOKEN 환경변수가 필요합니다.")
    print("   export SLACK_BOT_TOKEN=xoxb-...")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Canvas Registry: (channel_id, canvas_id, title_keyword)
# Single source of truth. Update when canvases are added/removed.
# ─────────────────────────────────────────────────────────────────────────────
CANVAS_REGISTRY = [
    # ── 기존 핵심 참조 캔버스 (10개) ──────────────────────────────────────────
    ("C0APW641YA2", "F0APZ1GRWMR", "온보딩 가이드"),       # 부톡-온보딩
    ("C0APYE86NAW", "F0AQZM486L8", "공지사항 필수 정보"),   # 공지사항
    ("C0AQSN8AEGY", "F0AQJA5C0SD", "업무 규칙"),           # 업무규칙
    ("C0AQ226BMSQ", "F0AQ91JMF2Q", "중개사 운영 가이드"),   # brokerage
    ("C0APYE7MLEN", "F0APQ0CF81M", "개발팀 핵심 참조"),     # dev
    ("C0APYE7MLEN", "F0AQZMPL5TJ", "앱 테스트"),           # dev
    ("C0AQSN880NL", "F0AQZMF3VJ4", "핵심 가치"),           # 회사내규
    ("C0APV20P03X", "F0AR0A45X8Q", "단지 링크 공유"),       # marketing
    ("C0APYE7MLEN", "F0AR0A3PBPA", "JIRA"),                # dev
    ("C0AQSN4B680", "F0AQ9KJ64CU", "중임 신청"),           # admin
    # ── WORKS 아카이브 → 캔버스 마이그레이션 (13개) ──────────────────────────
    ("C0APYE86NAW", "F0AQKBL08HF", "네이버"),              # 공지사항 - 부톡 사이트 바로가기
    ("C0AQSN8AEGY", "F0AQ03EUW83", "할 일"),               # 업무규칙 - To Do 사용법
    ("C0AQ226BMSQ", "F0AQKBR6R7T", "중개수수료"),           # brokerage - 중개수수료 규정
    ("C0AQ226BMSQ", "F0AQA3GLZU4", "중개사 계정 등록"),     # brokerage - 계정 등록 프로세스
    ("C0APYE7MLEN", "F0AQ33A5YKX", "매물 추이"),            # dev - 매물 추이 알고리즘
    ("C0APYE7MLEN", "F0AQA3GTM0C", "직거래"),              # dev - 직거래 편향 아이디어
    ("C0APYE7MLEN", "F0AQ33D97N1", "아파트 추가"),          # dev - 신축/100세대 미만 업데이트
    ("C0APYE7MLEN", "F0APR26FUB1", "TTA"),                 # dev - TTA 성능시험성적서
    ("C0APV20P03X", "F0AQ33EGA2H", "네이버 성과형"),        # marketing - 광고 숙지사항
    ("C0APV20P03X", "F0AQKCL5RDX", "수도권 아파트"),        # marketing - 시장규모 재산출
    ("C0APV20P03X", "F0AR0PP8NHE", "부동산 인접"),          # marketing - 인접 서비스 시장 규모
    ("C0APV20P03X", "F0AQKCN9WE5", "마케팅/영업 참조"),     # marketing - 참조 자료 (구글 애즈 포함)
    ("C0AQSN4B680", "F0AQKCR4SHF", "어드민 참조"),          # admin - 참조 자료
]


def curl_get(url):
    r = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {BOT_TOKEN}", url],
        capture_output=True, text=True
    )
    return json.loads(r.stdout)


def download(url):
    r = subprocess.run(
        ["curl", "-s", "-L", "-H", f"Authorization: Bearer {BOT_TOKEN}", url],
        capture_output=True, text=True
    )
    return r.stdout


def html_to_text(html):
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'&amp;', '&', html)
    html = re.sub(r'&nbsp;', ' ', html)
    return re.sub(r'\s+', ' ', html).strip()


def get_channel_name(ch_id):
    d = curl_get(f"https://slack.com/api/conversations.info?channel={ch_id}")
    return d.get("channel", {}).get("name", ch_id)


# ─── Collect all pinned messages ──────────────────────────────────────────────
def get_all_pins():
    result = {}
    d = curl_get("https://slack.com/api/conversations.list?types=public_channel,private_channel&limit=200&exclude_archived=false")
    for ch in d.get("channels", []):
        ch_id = ch["id"]
        pd = curl_get(f"https://slack.com/api/pins.list?channel={ch_id}")
        pins = [i for i in pd.get("items", []) if i.get("type") == "message"]
        if pins:
            result[ch_id] = {"name": ch.get("name", ch_id), "pins": pins}
    return result


# ─── Main verification ────────────────────────────────────────────────────────
def run():
    print("=" * 65)
    print("WORKS → Canvas Migration Verification Report")
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    all_pins = get_all_pins()
    total_pins = sum(len(v["pins"]) for v in all_pins.values())
    print(f"\n📌 총 핀 메시지: {total_pins}개 (채널 {len(all_pins)}개)")
    print(f"📋 캔버스 레지스트리: {len(CANVAS_REGISTRY)}개\n")

    # ── 1. Verify each registered canvas ──────────────────────────────────────
    print("─" * 65)
    print("1. 캔버스 존재 여부 + 내용 검증")
    print("─" * 65)

    results = []
    for ch_id, canvas_id, title_keyword in CANVAS_REGISTRY:
        ch_name = all_pins.get(ch_id, {}).get("name") or get_channel_name(ch_id)

        fd = curl_get(f"https://slack.com/api/files.info?file={canvas_id}")
        if not fd.get("ok"):
            results.append({
                "canvas_id": canvas_id, "ch": ch_name,
                "title": title_keyword, "status": "FAIL",
                "reason": f"files.info 에러: {fd.get('error')}"
            })
            continue

        canvas_title = fd["file"].get("title", "")
        dl_url = fd["file"].get("url_private_download", "")
        canvas_text = html_to_text(download(dl_url))

        if len(canvas_text) < 50:
            results.append({
                "canvas_id": canvas_id, "ch": ch_name, "title": canvas_title,
                "status": "FAIL", "reason": f"내용 너무 짧음 ({len(canvas_text)}자)"
            })
        elif title_keyword.lower() not in canvas_text.lower() and \
             title_keyword.lower() not in canvas_title.lower():
            results.append({
                "canvas_id": canvas_id, "ch": ch_name, "title": canvas_title,
                "status": "WARN", "reason": f"키워드 '{title_keyword}' 미발견"
            })
        else:
            results.append({
                "canvas_id": canvas_id, "ch": ch_name, "title": canvas_title,
                "status": "PASS", "reason": f"{len(canvas_text)}자"
            })

    for r in results:
        icon = "✅" if r["status"] == "PASS" else ("⚠️" if r["status"] == "WARN" else "❌")
        print(f"{icon} [{r['ch']:12}] {r['canvas_id']}  {r['title'][:35]:<35} {r['reason']}")

    # ── 2. Check orphan pins (pins without any registered canvas) ─────────────
    print("\n" + "─" * 65)
    print("2. 핀 메시지 ↔ 캔버스 매핑 검증")
    print("─" * 65)

    registered_channels = {}
    for ch_id, canvas_id, _ in CANVAS_REGISTRY:
        registered_channels.setdefault(ch_id, []).append(canvas_id)

    orphan_count = 0
    for ch_id, info in sorted(all_pins.items(), key=lambda x: x[1]["name"]):
        ch_name = info["name"]
        canvas_ids = registered_channels.get(ch_id, [])
        for pin in info["pins"]:
            msg_snippet = pin.get("message", {}).get("text", "")[:60].replace("\n", " ")
            if canvas_ids:
                print(f"✅ [{ch_name:12}] {msg_snippet[:55]}")
            else:
                print(f"❌ [{ch_name:12}] {msg_snippet[:55]}  ← 캔버스 없음")
                orphan_count += 1

    # ── 3. Check for canvases not pinned in channel ───────────────────────────
    print("\n" + "─" * 65)
    print("3. 캔버스 ↔ 핀 채널 일치 검증")
    print("─" * 65)

    mismatch_count = 0
    for ch_id, canvas_id, _ in CANVAS_REGISTRY:
        fd = curl_get(f"https://slack.com/api/files.info?file={canvas_id}")
        if not fd.get("ok"):
            continue
        canvas_channels = fd["file"].get("channels", []) + fd["file"].get("groups", [])
        if ch_id not in canvas_channels:
            ch_name = get_channel_name(ch_id)
            print(f"⚠️  {canvas_id} — 채널 {ch_name}에 없음 (actual: {canvas_channels})")
            mismatch_count += 1
        else:
            ch_name = all_pins.get(ch_id, {}).get("name") or get_channel_name(ch_id)
            print(f"✅ {canvas_id} → #{ch_name}")

    # ── Summary ───────────────────────────────────────────────────────────────
    passed  = sum(1 for r in results if r["status"] == "PASS")
    warned  = sum(1 for r in results if r["status"] == "WARN")
    failed  = sum(1 for r in results if r["status"] == "FAIL")

    print("\n" + "=" * 65)
    print(f"  캔버스 내용 검증  PASS {passed} / WARN {warned} / FAIL {failed}  (total {len(CANVAS_REGISTRY)})")
    print(f"  고아 핀 메시지     {orphan_count}개")
    print(f"  채널 불일치        {mismatch_count}개")
    print("=" * 65)

    all_ok = (passed == len(CANVAS_REGISTRY) and orphan_count == 0 and mismatch_count == 0)
    if all_ok:
        print("🎉 100% 마이그레이션 완료 — 모든 검증 통과")
        return 0
    else:
        print("⚠️  미완료 항목 있음")
        return 1


if __name__ == "__main__":
    sys.exit(run())
