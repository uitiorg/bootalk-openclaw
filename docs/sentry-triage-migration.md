# Sentry Triage Bot — Slack 마이그레이션 가이드

## 현재 구조

```
Sentry.io (webhook)
    │ POST https://sentry-hook.bootalk.co.kr/hooks/sentry?token=...
    ▼
Cloudflare Tunnel (sentry-hook)       ← launchd: com.cloudflare.sentry-hook
    │ sentry-hook.bootalk.co.kr → localhost:19789
    ▼
OpenClaw Sentry Gateway (port 19789) ← launchd: ai.openclaw.sentry
    │ Profile: sentry
    │ Config: ~/.openclaw-sentry/openclaw.json
    │ Model: gpt-5.3-codex (fallback: claude-opus-4-5)
    │
    ├── hooks/transforms/sentry.js   ← webhook payload → triage prompt
    ├── SENTRY_RUNBOOK.md            ← 분류/대응 정책
    │
    └── Delivery: openclaw --profile main message send
        → Telegram 그룹 (-5152975056)
```

## 마이그레이션 목표

```
변경 전: triage 결과 → Telegram 그룹
변경 후: triage 결과 → Slack #sentry-alerts 채널
```

바꿔야 할 것:
1. `sentry.js`의 delivery 목적지
2. `~/.openclaw-sentry/openclaw.json`에 Slack 채널 추가
3. 메인 프로필 (`~/.openclaw/openclaw.json`)에도 Slack 설정 필요 (delivery가 main profile 경유)

바꾸지 않는 것:
- Cloudflare Tunnel 설정 (그대로)
- launchd 데몬들 (그대로)
- SENTRY_RUNBOOK.md 정책 (그대로)
- triage 분석 로직 (그대로)

## 사전 준비

### 1. Slack App 생성

[slack-setup.md](slack-setup.md) 참고. 동일한 Slack App으로 메인 Gateway + Sentry Gateway 모두 사용 가능.

### 2. Slack에 #sentry-alerts 채널 생성

```
Slack Workspace → 채널 만들기 → #sentry-alerts
→ 봇을 채널에 초대: /invite @Bootalk AI
```

## 마이그레이션 절차

### Step 1: 메인 프로필에 Slack 추가

`~/.openclaw/openclaw.json`의 `channels`에 Slack 추가:

```json5
{
  "channels": {
    "telegram": { /* 기존 설정 유지 */ },
    "slack": {
      "enabled": true,
      "mode": "socket",
      "appToken": "xapp-YOUR_APP_TOKEN",
      "botToken": "xoxb-YOUR_BOT_TOKEN"
    }
  }
}
```

### Step 2: sentry.js의 delivery 목적지 변경

이 레포의 `sentry/transforms/sentry.js`는 이미 환경변수 기반으로 변경 가능하게 되어 있음.

`~/.openclaw-sentry/openclaw.json`에서 환경변수 설정:

```json5
{
  // 기존 설정...
  "env": {
    "SENTRY_DELIVERY_CHANNEL": "slack",
    "SENTRY_DELIVERY_TARGET": "slack:#sentry-alerts"
  }
}
```

또는 launchd plist (`ai.openclaw.sentry.plist`)의 EnvironmentVariables에 추가:

```xml
<key>SENTRY_DELIVERY_CHANNEL</key>
<string>slack</string>
<key>SENTRY_DELIVERY_TARGET</key>
<string>slack:#sentry-alerts</string>
```

### Step 3: transform 파일 교체

```bash
# 이 레포의 transform으로 교체
cp sentry/transforms/sentry.js ~/.openclaw-sentry/hooks/transforms/sentry.js
```

### Step 4: SENTRY_RUNBOOK.md 심링크 (선택)

레포의 runbook을 원본으로 사용하려면:

```bash
ln -sf /path/to/bootalk-openclaw/sentry/SENTRY_RUNBOOK.md \
  ~/.openclaw/workspace/SENTRY_RUNBOOK.md
```

### Step 5: Gateway 재시작 + 테스트

```bash
# 메인 Gateway 재시작
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway

# Sentry Gateway 재시작
launchctl kickstart -k gui/$(id -u)/ai.openclaw.sentry

# Sentry test webhook으로 확인
# Sentry > Settings > Integrations > Internal Integration > Send Test
```

## 롤백 (문제 발생 시)

```bash
# 환경변수만 텔레그램으로 되돌리면 됨
# SENTRY_DELIVERY_CHANNEL=telegram
# SENTRY_DELIVERY_TARGET=telegram:-5152975056

# 또는 원본 transform 복원
cp ~/.openclaw-sentry/hooks/transforms/sentry.js.bak \
   ~/.openclaw-sentry/hooks/transforms/sentry.js

launchctl kickstart -k gui/$(id -u)/ai.openclaw.sentry
```

## 듀얼 채널 테스트 (권장)

한번에 전환하지 말고, 양쪽 다 보내서 비교할 수도 있음:

```javascript
// sentry.js에서 양쪽 다 전송하는 임시 코드
const deliveryInstructions = `
Delivery (MANDATORY):
1) /tmp/sentry_summary.txt 저장
2) Telegram 전송: openclaw --profile main message send --channel telegram --target telegram:-5152975056 ...
3) Slack 전송: openclaw --profile main message send --channel slack --target slack:#sentry-alerts ...
`;
```

2주간 양쪽 비교 후 Telegram 제거.

## FAQ

**Q: Slack CLI를 설치해야 하나?**
A: 아니오. OpenClaw이 `@slack/bolt` SDK를 내장하고 있어서, `appToken` + `botToken`만 설정하면 Socket Mode로 자동 연결됩니다.

**Q: 기존 Cloudflare Tunnel을 바꿔야 하나?**
A: 아니오. Sentry webhook → CF Tunnel → OpenClaw Gateway 경로는 동일합니다. 바뀌는 것은 triage 후 결과를 어디로 보내느냐(Telegram vs Slack)만입니다.

**Q: Sentry Gateway와 메인 Gateway를 합칠 수 있나?**
A: 가능하지만 비추천. 격리해둔 이유가 있음 (모델/리소스 충돌 방지, Sentry triage가 메인 대화에 영향 안 줌). 현재 구조 유지 권장.
