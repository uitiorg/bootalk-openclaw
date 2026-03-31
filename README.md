# bootalk-openclaw

OpenClaw skills, Sentry triage config, and Slack integration for the Bootalk team.

**No separate server required.** OpenClaw Gateway runs locally and connects to Slack via Socket Mode. Skills are markdown files — no code, no deployment.

## Architecture

```
Slack Workspace
    │ Socket Mode (WebSocket)
    ▼
OpenClaw Gateway (local Mac, port 18789)
    │
    ├── Skills (this repo)
    │   ├── 매물 조회     → curl → btalk2.1_backend API
    │   ├── KPT 회고      → gh CLI → GitHub API
    │   ├── TODO 관리     → gog CLI → Google Docs
    │   ├── 배포 상태     → vercel CLI
    │   ├── 회원 조회     → curl → btalk2.1_backend API
    │   └── 주간 보고     → gh CLI → GitHub API
    │
    ├── Sentry Triage Bot (separate gateway, port 19789)
    │   └── CF Tunnel → webhook transform → triage → Slack/Telegram
    │
    └── Google Drive    → Slack native integration (별도 설치)
```

## Integration Progress

| Item | Status | Notes |
|------|--------|-------|
| **OpenClaw Gateway** | ✅ Running | `launchd` daemon on port 18789 |
| **Telegram channel** | ✅ Connected | Main + gamedev + career agents |
| **Sentry triage bot** | ✅ Running | Separate gateway on port 19789, CF Tunnel, delivers to Telegram |
| **Skills (this repo)** | ✅ Ready | 6 skills written, descriptions optimized for AI matching |
| **Slack workspace** | ⬜ Not started | Create workspace → create app → get tokens |
| **Slack App (tokens)** | ⬜ Not started | Need `xapp-` (App Token) + `xoxb-` (Bot Token) |
| **OpenClaw ↔ Slack** | ⬜ Not started | Add `channels.slack` to `openclaw.json` |
| **Backend auth endpoint** | ⬜ Not started | `InternalAuthController.kt` — 1 file to add to btalk2.1_backend |
| **Sentry → Slack delivery** | ⬜ Not started | Set `SENTRY_DELIVERY_CHANNEL=slack` env var |
| **Google Drive ↔ Slack** | ⬜ Not started | Install Google Drive app in Slack workspace |
| **Slack channels setup** | ⬜ Not started | `#sentry-alerts`, `#dev`, `#공지사항` etc. |

## Setup

### Prerequisites

- OpenClaw installed and gateway running (`openclaw gateway`)
- `gh` CLI authenticated (`gh auth login`)
- `gog` CLI authenticated (`gog auth`, account: `cdo.bootalk@gmail.com`)
- `vercel` CLI linked (for deploy skill)

### 1. Clone and link skills

```bash
git clone git@github.com:uitiorg/bootalk-openclaw.git ~/Bootalk/bootalk-openclaw

# Option A: extraDirs (recommended)
# Add to ~/.openclaw/openclaw.json:
#   "skills": { "load": { "extraDirs": ["~/Bootalk/bootalk-openclaw/skills"] } }

# Option B: symlink
ln -s ~/Bootalk/bootalk-openclaw/skills/* ~/.openclaw/skills/
```

### 2. Add Slack channel to OpenClaw

See [docs/slack-setup.md](docs/slack-setup.md) for step-by-step Slack App creation.

Add to `~/.openclaw/openclaw.json`:

```json5
{
  "channels": {
    // ... existing telegram config ...
    "slack": {
      "enabled": true,
      "mode": "socket",
      "appToken": "xapp-YOUR_APP_TOKEN",
      "botToken": "xoxb-YOUR_BOT_TOKEN"
    }
  }
}
```

### 3. Add backend auth endpoint

One file to add to `btalk2.1_backend` — see [docs/api-auth.md](docs/api-auth.md).

This enables skills to call existing backend APIs with `UserRole.SERVICE` authentication.

### 4. Configure skill environment variables

```json5
// ~/.openclaw/openclaw.json
{
  "skills": {
    "entries": {
      "bootalk-properties": {
        "env": {
          "BOOTALK_API_URL": "https://api.bootalk.com",
          "BOOTALK_API_KEY": "your-internal-api-key"
        }
      }
    }
  }
}
```

### 5. Restart gateway and verify

```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
openclaw channels status --probe
```

Test in Slack: `@Bootalk AI 안녕`

## Structure

```
skills/                          # OpenClaw skills (SKILL.md)
├── bootalk-properties/          # 매물 현황, 시세, 거래량 조회
├── bootalk-kpt/                 # 주간 KPT 회고 생성
├── bootalk-todo/                # Google Docs TODO 관리
├── bootalk-deploy/              # Vercel 배포 상태/로그/롤백
├── bootalk-members/             # 회원/중개사 검색
└── bootalk-weekly-report/       # 경영진 주간 보고 (비개발자 언어)
sentry/                          # Sentry triage bot
├── transforms/sentry.js         # Webhook transform (env-based delivery target)
└── SENTRY_RUNBOOK.md            # Triage 정책 (분류/대응/기록)
docs/
├── slack-setup.md               # Slack App 생성 가이드
├── skill-guide.md               # Skill 작성 방법
├── api-auth.md                  # Backend 서비스 토큰 인증
└── sentry-triage-migration.md   # Sentry Telegram → Slack 마이그레이션
config/
└── openclaw.example.json5       # 설정 템플릿 (토큰 제외)
```

## Adding a new skill

`skills/<name>/SKILL.md` 파일을 추가하면 됩니다. 코드 작성 불필요, 배포 불필요.

작성 가이드: [docs/skill-guide.md](docs/skill-guide.md)

Key points:
- `description` 필드에 사용자가 실제로 말할 **트리거 키워드**를 넣을 것
- `When to Use` 섹션이 AI의 스킬 선택을 결정함
- `Commands`는 구체적인 bash 명령어로 작성

## Docs

| Document | Purpose |
|----------|---------|
| [Slack Setup](docs/slack-setup.md) | Slack App 생성 + OpenClaw 연결 |
| [Skill Guide](docs/skill-guide.md) | 새 스킬 작성 방법 |
| [API Auth](docs/api-auth.md) | btalk2.1_backend 서비스 토큰 인증 |
| [Sentry Migration](docs/sentry-triage-migration.md) | Sentry triage Telegram → Slack 전환 |
