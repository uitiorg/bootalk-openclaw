# Bootalk operations Agent Guide

이 저장소는 Bootalk 팀의 업무 스킬, CLI, Slack 참고자료와 운영 기록을 관리합니다. 현재 상주 OpenClaw gateway를 제공하지 않으며, 저장소의 문서나 스크립트가 자동으로 실행된다고 가정하지 않습니다.

## Runtime model

| Layer | Use it for | Do not rely on it for |
|---|---|---|
| Slack connector / Slack API | 현재 채널·멤버·메시지 조회, 명시적으로 요청된 Slack 전송 | Bootalk 업무 규칙, 캘린더·메일 side effect |
| Codex automation | 예약된 에러·성능·배포·문서 점검과 보고 | 이 repo의 파일을 자동으로 최신화한다는 보장 |
| `skills/*/SKILL.md` | 재사용 가능한 업무 절차와 판단 기준 | 자동 로딩이나 상주 봇 실행 |
| `scripts/*` | 사용자가 요청한 직접 실행형 업무 로직 | 승인 없는 반복 실행 |

OpenClaw gateway, Slack Socket Mode, `18789`/`19789` 포트와 `launchctl` 재시작 절차는 현재 운영 경로가 아닙니다. 관련 문서는 `docs-openclaw/`에 역사 기록으로 보존되어 있습니다.

## Repository map

| Path | Purpose |
|---|---|
| `skills/*/SKILL.md` | Codex 또는 수동 작업에 사용할 업무 지침 |
| `scripts/cal.py` | 팀 캘린더·연차·HR 메일 CLI |
| `scripts/verify-canvas-migration.py` | Slack Canvas 검증 도구 |
| `team/channels.md` | Slack 채널·사용자 ID 참고 snapshot |
| `sentry/SENTRY_RUNBOOK.md` | Codex Sentry triage 정책 |
| `docs/` | 공개 문서. 내부 secret 금지 |
| `docs-openclaw/` | 폐기된 OpenClaw 참고자료 |
| `config/openclaw.example.json5` | 폐기된 설정의 보존 기록 |

## Effective workflow

1. 요청을 Slack 조회/전송, Bootalk 업무 실행, 또는 읽기 전용 분석으로 분류합니다.
2. Slack 대상은 작업 직전에 connector로 사용자·채널·권한을 확인합니다. `team/channels.md`는 live source가 아닙니다.
3. 캘린더, 연차, Gmail, GitHub issue/PR, Canvas처럼 side effect가 있는 작업은 사용자의 명시적 의도와 필수 입력을 확인합니다.
4. 예약 automation의 현재 상태는 `/Users/juucheol/.codex/automations/`에서 확인합니다. 이 repo를 수정해 automation이 자동으로 배포된다고 가정하지 않습니다.
5. 실행 결과에는 명령, 대상, 링크/ID, side effect와 확인 제한을 남깁니다.
6. 문서나 스킬을 수정한 뒤 stale 경로·깨진 링크·문법 오류를 검색하고 관련 테스트를 실행합니다.

## Calendar rules

- 팀 회의·이벤트 조회와 추가는 `agenda`와 `add`를 사용합니다.
- 연차·반차 조회는 반드시 `leaves`를 사용합니다.
- 연차 등록은 반드시 `--remaining "..."`을 포함합니다.
- 잔여 연차가 없으면 등록하지 않고 전유진님 또는 HR에 확인하도록 합니다.
- 등록 후 캘린더와 HR 메일의 성공 여부를 각각 보고합니다.
- 테스트나 재현에서는 `--no-email`로 메일 side effect를 끕니다.

## Slack rules

- 채널·멤버·메시지의 현재 상태는 connector 결과를 우선합니다.
- 공개 채널에 쓰기 전 대상 채널과 요청 범위를 다시 확인합니다.
- 사용자 요청이 없는 자동 Slack 메시지, reaction, pin, Canvas 수정은 실행하지 않습니다.
- Slack webhook은 일방향 알림일 수 있으므로, 그 메시지에 답글을 달면 원래 automation이 재개된다고 설명하지 않습니다.

## Secrets and public docs

- Slack token, Google credential, OAuth token, webhook URL, 내부 API key, `.env`는 출력·커밋·문서화하지 않습니다.
- `scripts/credentials.json`, `scripts/token.json`은 로컬 인증 파일이며 내용을 읽거나 복사하지 않습니다.
- `docs/`는 GitHub Pages 공개 영역입니다. 내부 운영 경로와 개인 데이터를 넣지 않습니다.

## Verification

- 문서/스킬 변경: diff, 링크, stale 검색, 관련 테스트를 확인합니다.
- 캘린더 작업: 명령 결과와 Calendar 링크를 확인합니다.
- Slack 작업: channel/user ID와 Slack 링크를 확인합니다.
- GitHub 작업: issue/PR URL과 실제 상태를 확인합니다.
- 자동화 상태: TOML의 `status`, `rrule`, `cwds`와 automation memory를 함께 확인합니다.

## Historical OpenClaw material

`docs-openclaw/`, `.debug-journal.md`, 과거 `docs/superpowers/` 설계 문서는 삭제하지 않은 역사 기록입니다. 현재 실행 절차처럼 복사하거나 재활성화하지 말고, 현재 문서의 사실과 충돌하면 현재 Codex automation 상태를 우선합니다.
