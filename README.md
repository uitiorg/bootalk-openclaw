# bootalk-openclaw

OpenClaw skills, Sentry triage config, and Slack integration for the Bootalk team.

**No separate server required.** OpenClaw Gateway runs locally and connects to Slack via Socket Mode. Skills are markdown files — no code, no deployment.

## 🆕 Recently Added (2026-04-28)

**연차 등록 시 자동 이메일 알림** — 부톡봇으로 연차/반차를 등록하면 "부톡 연차" 캘린더 등록과 동시에 `holiday.uiti@gmail.com` (HR)로 알림 메일 1통이 자동 발송됩니다.

- 메일 제목: `[오전반차] 26.05.13 주우철` 형식
- From: `<신청자 이름> <cdo.bootalk@gmail.com>` — 시각적으로 신청자 본인이 보낸 것처럼 표시
- Reply-To: 신청자 본인 이메일 (HR이 답장 시 신청자에게 직접 도달)
- 반차 시간: 오전 09:30~13:30 / 오후 13:30~18:30
- 자세한 동작·구성·예시: [`docs/leave-email-feature.md`](docs/leave-email-feature.md)

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
| **Skills (this repo)** | ✅ Loaded | 6 skills, `extraDirs` 연결 완료, git hook으로 자동 동기화 |
| **Slack workspace** | ✅ Done | WORKS 게시판 57개 포스트 마이그레이션 완료 |
| **Slack App (tokens)** | ✅ Done | `xapp-` + `xoxb-` 발급 및 연결 완료 |
| **OpenClaw ↔ Slack** | ✅ Connected | Socket Mode, `channels.slack` 설정 완료 |
| **Google Drive ↔ Slack** | ✅ Done | Google Drive 앱 설치, 도메인 인증 활성화 |
| **Slack channels setup** | ✅ Done | 11개 채널, WORKS 아카이브 핀 메시지 세팅 완료 |
| **Backend auth endpoint** | ⬜ Not started | `InternalAuthController.kt` — 1 file to add to btalk2.1_backend |
| **Sentry → Slack delivery** | ⬜ Not started | Set `SENTRY_DELIVERY_CHANNEL=slack` env var |

## Setup

### Prerequisites

- OpenClaw installed and gateway running (`openclaw gateway`)
- `gh` CLI authenticated (`gh auth login`)
- `gog` CLI authenticated (`gog auth`, account: `cdo.bootalk@gmail.com`)
- `vercel` CLI linked (for deploy skill)

### 1. Clone and link skills

```bash
git clone git@github.com:uitiorg/bootalk-openclaw.git ~/Bootalk/bootalk-openclaw
```

`~/.openclaw/openclaw.json`의 `skills` 섹션에 아래를 추가:

```json5
{
  "skills": {
    "load": {
      "extraDirs": ["/Users/juucheol/Bootalk/bootalk-openclaw/skills"]
    }
  }
}
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

## 로컬 OpenClaw와 동기화 방법

### 동작 원리

이 레포의 `skills/` 폴더는 `~/.openclaw/openclaw.json`의 `extraDirs`를 통해 OpenClaw Gateway에 직접 연결되어 있습니다. Gateway는 실행 시 해당 폴더를 읽어 스킬을 로드합니다.

```
이 레포 (skills/)
    ↓  extraDirs로 직접 참조 (복사 없음)
~/.openclaw/openclaw.json
    ↓
OpenClaw Gateway (port 18789)
    ↓  Socket Mode
Slack / Telegram
```

### SKILL.md를 수정하면?

Gateway를 재시작해야 변경사항이 반영됩니다:

```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
```

### git pull 시 자동 재시작

`.git/hooks/post-merge` 훅이 설정되어 있어 `git pull` 후 Gateway가 자동으로 재시작됩니다:

```bash
# .git/hooks/post-merge (이미 설정됨)
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
```

즉, **`git pull`만 하면 봇에 바로 반영**됩니다. 별도 배포나 서버 재시작 없음.

### 새 팀원이 이 레포를 클론할 때

```bash
git clone git@github.com:uitiorg/bootalk-openclaw.git ~/Bootalk/bootalk-openclaw

# openclaw.json에 extraDirs 추가 (위 Setup 섹션 참고)

# post-merge 훅은 git hook이라 클론 시 자동으로 따라오지 않음 — 수동 설정 필요:
echo 'launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway' \
  > ~/Bootalk/bootalk-openclaw/.git/hooks/post-merge
chmod +x ~/Bootalk/bootalk-openclaw/.git/hooks/post-merge
```

---

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
