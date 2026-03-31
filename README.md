# bootalk-openclaw

OpenClaw skills and configuration for the Bootalk team.

## Structure

```
skills/                          # OpenClaw skills (SKILL.md)
├── bootalk-properties/          # 매물/아파트 데이터 조회
├── bootalk-kpt/                 # 주간 KPT 회고 생성
├── bootalk-todo/                # Google Docs TODO 관리
├── bootalk-deploy/              # 배포 상태 확인
├── bootalk-members/             # 회원/중개사 조회
└── bootalk-weekly-report/       # 주간 보고 생성
sentry/                          # Sentry triage bot
├── transforms/sentry.js         # Webhook transform (payload → triage prompt)
└── SENTRY_RUNBOOK.md            # Triage 정책 (분류/대응/기록)
docs/                            # 설정 가이드
config/                          # 설정 템플릿
```

## Setup

### 1. Link skills to OpenClaw

```bash
# Option A: extraDirs 설정 (권장)
# ~/.openclaw/openclaw.json 에 추가:
# { "skills": { "load": { "extraDirs": ["/path/to/bootalk-openclaw/skills"] } } }

# Option B: 심링크
ln -s $(pwd)/skills/* ~/.openclaw/skills/
```

### 2. Configure environment variables

```bash
cp config/openclaw.example.json5 ~/.openclaw/openclaw.json
# 토큰 값 채우기 (SLACK_APP_TOKEN, SLACK_BOT_TOKEN, BOOTALK_API_KEY 등)
```

### 3. Start gateway

```bash
openclaw gateway
openclaw channels status --probe
```

## Adding a new skill

`skills/<name>/SKILL.md` 파일을 추가하면 됩니다. 코드 작성 불필요, 배포 불필요.

작성 가이드: [docs/skill-guide.md](docs/skill-guide.md)

## Sentry Triage Bot

현재 Telegram으로 전달 중인 Sentry triage bot의 설정과 정책이 `sentry/` 디렉토리에 있습니다.
Slack 마이그레이션 가이드: [docs/sentry-triage-migration.md](docs/sentry-triage-migration.md)
