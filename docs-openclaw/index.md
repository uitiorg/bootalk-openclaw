# Retired OpenClaw reference

> 상태: 역사 기록. 2026-08-10 현재 본 Mac에 OpenClaw gateway, Slack Socket Mode, 관련 LaunchAgent는 없습니다.
> 이 디렉터리의 명령은 현재 운영 절차가 아닙니다. 새 작업은 [`../AGENTS.md`](../AGENTS.md)와 Codex automation 상태를 기준으로 하세요.

## 현재 운영 문서

| 목적 | 기준 |
|---|---|
| 예약 작업 | `/Users/juucheol/.codex/automations/` |
| Slack live context | Codex Slack connector / Slack API |
| 업무 스킬·CLI | [`../skills/`](../skills/)와 [`../scripts/`](../scripts/) |
| 운영 규칙 | [`../AGENTS.md`](../AGENTS.md) |
| Sentry triage | [`../sentry/SENTRY_RUNBOOK.md`](../sentry/SENTRY_RUNBOOK.md) |

## 보존된 자료

| 문서 | 과거 용도 |
|---|---|
| `slack-setup.md` | Slack App과 OpenClaw Socket Mode 연결 기록 |
| `slack-access-control.md` | OpenClaw 채널·DM 멘션 게이팅 설정 |
| `slack-config-reference.md` | OpenClaw Slack config 필드 참고 |
| `slack-sessions.md` | OpenClaw Slack 세션·threading 참고 |
| `channel-routing.md` | OpenClaw channel routing 참고 |
| `pairing.md` | OpenClaw DM pairing 참고 |
| `slash-commands.md` | OpenClaw slash command 참고 |
| `sentry-pipeline.md` | 과거 Sentry compatibility ingress 기록 |
| `architecture.md` | 2026-04 시점 Bootalk 서비스 snapshot |

오래된 설정을 다시 활성화하지 말고, 현재 필요한 동작을 Codex task·automation 또는 명시적인 Slack connector 작업으로 새로 정의하세요.
