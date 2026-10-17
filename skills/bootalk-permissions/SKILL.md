---
name: bootalk_permissions
description: 채널 멤버 관리, 그룹 권한 조회, 채널 초대/제거, 팀 그룹 구성 확인. "누가 어느 채널에 있어?", "XX 채널에 YY 초대해줘", "권한 설정 보여줘" 등.
metadata:
  codex:
    requires:
      env: [SLACK_BOT_TOKEN]
      bins: [curl, python3]
---

# 채널 권한 관리 (Permission Manager)

## When to Use
- "누가 dev 채널 있어?"
- "YY를 admin 채널에 추가해줘"
- "권한 그룹 보여줘"
- "채널 멤버 목록"
- 팀 구성원 채널 접근 권한 변경

---

## 그룹 정의 (Group Definitions)

```
개발팀:     주우철 (U0APRS4J70B), 정정일 (U0APRSH0SNP), 이현석 (U0AQ1RWGKPW)
마케팅/디자인: 배지은 (U0APW6HMNR4), 이훈구 (U0AQ1RUPF4L)
전체:       전원 (위 6명 전체)
admin:      이현석 (U0AQ1RWGKPW), 전유진 (U0APGQN76CF), 이훈구 (U0AQ1RUPF4L)
```

## 채널 접근 정책 (Channel Access Policy)

```
채널              접근 그룹
─────────────────────────────────────────
dev              개발팀
marketing        마케팅/디자인
design           마케팅/디자인
admin            admin 그룹
brokerage        전체
온보딩           전체
공지사항         전체
cs               전체
회사내규         전체
업무규칙         전체
```

## 채널 ID 매핑

```
dev          C0APYE7MLEN
marketing    C0APV20P03X
design       C0APT0W6B43
admin        C0AQSN4B680
brokerage    C0AQ226BMSQ
온보딩       C0AQBB8JTSM
공지사항     C0APYE86NAW
cs           C0APWC7RSSJ
회사내규     C0AQSN880NL
업무규칙     C0AQSN8AEGY
```

---

## Commands

### 채널 멤버 조회

```bash
CHANNEL_ID="C0APYE7MLEN"  # dev 예시
curl -s -X GET \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.members?channel=$CHANNEL_ID" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('members', d.get('error')))"
```

### 채널에 멤버 초대

```bash
CHANNEL_ID="C0APYE7MLEN"
USER_IDS="U0APRS4J70B,U0APRSH0SNP"  # 콤마로 구분, 최대 1000명
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  "https://slack.com/api/conversations.invite" \
  -d "{\"channel\":\"$CHANNEL_ID\",\"users\":\"$USER_IDS\"}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if d.get('ok') else d.get('error'))"
```

### 채널에서 멤버 제거

```bash
CHANNEL_ID="C0APYE7MLEN"
USER_ID="U0APRSH0SNP"
curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  "https://slack.com/api/conversations.kick" \
  -d "{\"channel\":\"$CHANNEL_ID\",\"user\":\"$USER_ID\"}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if d.get('ok') else d.get('error'))"
```

### 전체 멤버 목록 조회

```bash
curl -s -X GET \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/users.list" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
for u in d.get('members', []):
    if u.get('is_bot') or u.get('deleted') or u.get('id') == 'USLACKBOT':
        continue
    print(u['id'], u.get('real_name',''))
"
```

### 현재 권한 정책 전체 적용 (초기 세팅용)

모든 채널에 정책대로 멤버를 초대합니다. 이미 채널에 있는 멤버는 `already_in_channel` 에러가 나지만 무시해도 됩니다.

```bash
BOT_TOKEN="$SLACK_BOT_TOKEN"

invite() {
  local channel=$1; local users=$2
  curl -s -X POST \
    -H "Authorization: Bearer $BOT_TOKEN" \
    -H "Content-Type: application/json" \
    "https://slack.com/api/conversations.invite" \
    -d "{\"channel\":\"$channel\",\"users\":\"$users\"}" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print('$channel OK' if d.get('ok') else '$channel ' + d.get('error',''))"
}

DEV_TEAM="U0APRS4J70B,U0APRSH0SNP,U0AQ1RWGKPW"
MARKETING="U0APW6HMNR4,U0AQ1RUPF4L"
ALL="U0APRS4J70B,U0APRSH0SNP,U0AQ1RWGKPW,U0APW6HMNR4,U0AQ1RUPF4L,U0APGQN76CF"
ADMIN_GROUP="U0AQ1RWGKPW,U0APGQN76CF,U0AQ1RUPF4L"

invite C0APYE7MLEN "$DEV_TEAM"
invite C0APV20P03X "$MARKETING"
invite C0APT0W6B43 "$MARKETING"
invite C0AQSN4B680 "$ADMIN_GROUP"
invite C0AQ226BMSQ "$ALL"
invite C0AQBB8JTSM "$ALL"
invite C0APYE86NAW "$ALL"
invite C0APWC7RSSJ "$ALL"
invite C0AQSN880NL "$ALL"
invite C0AQSN8AEGY "$ALL"
```

## Response Format

결과를 한국어로 표 형태로 정리:
- 채널명과 현재 멤버 목록
- 변경 성공/실패 여부
- 그룹 정책과의 차이점 (있을 경우)
