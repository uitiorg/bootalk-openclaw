# Bootalk operations library

Bootalk 팀의 업무 스킬, CLI 스크립트, Slack 운영 참고자료와 마이그레이션 기록을 관리하는 저장소입니다.

현재 이 저장소는 상주 봇이나 로컬 서버가 아닙니다. 실행 주체는 다음과 같이 분리되어 있습니다.

| 실행 주체 | 역할 |
|---|---|
| Codex automation | 예약된 에러·성능·배포·문서 점검과 보고 |
| Slack connector / Slack API | 실시간 채널·사용자 조회와 명시적으로 요청된 Slack 작업 |
| 이 repo의 스크립트 | 캘린더, 연차, Slack Canvas 검증 등 직접 실행 가능한 업무 로직 |
| 이 repo의 문서 | 업무 규칙, 권한 경계, 과거 마이그레이션의 버전 관리 |

## Current status

2026-08-10 KST 기준 확인된 상태입니다. 자동화 목록과 실행 결과는 `/Users/juucheol/.codex/automations/`가 source of truth입니다.

- 본 Mac의 OpenClaw 명령, gateway, Socket Mode 런타임은 제거되었습니다.
- Codex automation은 11개가 등록되어 있고 8개가 활성, 3개가 일시정지 상태입니다.
- 에러·성능 autopilot은 Codex automation이 소유합니다. 이 repo는 해당 작업의 실행 엔진이 아닙니다.
- Sentry public ingress와 PR polling의 OpenClaw 중복 경로는 사용하지 않습니다.
- Slack 채널·멤버 표는 참고용 snapshot일 뿐이며, 새 작업 전 Slack connector로 다시 확인해야 합니다.

## Use this repository

| Path | Purpose |
|---|---|
| `skills/*/SKILL.md` | Codex 또는 수동 작업에서 재사용할 Bootalk 업무 지침 |
| `scripts/cal.py` | Google Calendar/Gmail 기반 일정·연차 CLI |
| `scripts/verify-canvas-migration.py` | Slack Canvas 마이그레이션 검증 |
| `team/channels.md` | Slack ID와 채널의 참고 snapshot |
| `sentry/SENTRY_RUNBOOK.md` | Sentry triage 판단 정책 |
| `docs/` | 공개 문서와 업무 기능 설명 |
| `docs-openclaw/` | 더 이상 실행하지 않는 OpenClaw 참고 문서 |
| `config/openclaw.example.json5` | 폐기된 설정의 호환성 기록 |

## Safe workflow

1. Slack의 현재 채널·멤버·메시지는 connector에서 조회합니다. `team/channels.md`의 ID를 최신 사실로 가정하지 않습니다.
2. 예약 작업의 상태·스케줄·최근 실행은 `/Users/juucheol/.codex/automations/*/automation.toml`과 각 `memory.md`에서 확인합니다.
3. 캘린더·연차·메일처럼 side effect가 있는 CLI는 사용자의 명시적 요청과 필요한 값이 모두 있을 때만 실행합니다.
4. Slack 메시지나 webhook을 받았다는 사실만으로 GitHub·캘린더·메일 작업을 자동 승인하지 않습니다.
5. 토큰, OAuth 파일, webhook URL, 내부 API key는 출력하거나 커밋하지 않습니다.

## Calendar and leave CLI

```bash
python3 scripts/cal.py agenda
python3 scripts/cal.py leaves
python3 scripts/cal.py add "주간 회의" "2026-04-07 10:00" 60
python3 scripts/cal.py leave "이름" "YYYY-MM-DD" --remaining "사용 후 잔여일"
```

연차 등록은 `--remaining` 값을 반드시 받아야 합니다. Gmail 알림까지 보내지 않는 테스트는 `--no-email`을 사용합니다. 실제 Calendar/Gmail side effect 전에는 대상자, 날짜, 반차 여부, 잔여 연차를 다시 확인합니다.

## Service API authentication

`BOOTALK_API_URL`과 `BOOTALK_API_KEY`가 필요한 스킬은 서비스 토큰을 발급한 뒤 API를 호출합니다. 자세한 내용은 [`docs/api-auth.md`](docs/api-auth.md)를 참고하세요. 토큰 값 자체는 문서와 로그에 남기지 않습니다.

## Retired OpenClaw material

`docs-openclaw/`, `docs/slack-setup.md`, `config/openclaw.example.json5`와 일부 설계 문서는 과거 OpenClaw/Slack Socket Mode 구성의 보존 기록입니다. 현재 gateway를 설치하거나 되살리는 절차로 사용하지 마세요. 현재 운영 경계는 [`AGENTS.md`](AGENTS.md)와 Codex automation 설정입니다.

## Contributing

- 업무 규칙이나 실행 명령을 바꿀 때 source 문서와 관련 스킬을 함께 갱신합니다.
- 채널 ID·멤버·권한은 Slack live state로 재검증한 날짜와 범위를 기록합니다.
- 공개 `docs/`에는 secret, 개인 OAuth 파일, 내부 endpoint 세부값을 넣지 않습니다.
- 문서 변경 후 stale한 OpenClaw 실행 경로, 오래된 날짜, 깨진 링크를 검색하고 관련 CLI 테스트를 실행합니다.
