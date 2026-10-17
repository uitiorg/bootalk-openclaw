# Sentry public ingress (retired OpenClaw record)

> 상태: 역사 기록. 2026-08-10 현재 OpenClaw gateway, Sentry compatibility gateway, 관련 LaunchAgent와 local ports는 실행되지 않습니다.

## Current ownership

- Sentry triage와 예약 보고: Codex automation 및 `sentry-cli` skill
- 성능·에러 morning check: Codex automation
- GitHub PR review triage: Codex automation의 prompt와 status에 따름
- Slack 전달: Codex Slack connector 또는 명시적으로 요청된 webhook
- 이 문서의 OpenClaw ingress: 복원 대상이 아닌 보존 기록

## Historical topology

과거에는 Cloudflare tunnel, URL-token compatibility proxy, 별도 Sentry gateway와 transform을 통해 Sentry webhook을 처리했습니다. 당시에도 중복 polling과 Telegram/Slack delivery는 제거하는 방향이었고, transform은 `NO_REPLY`와 `deliver: false`를 사용했습니다.

이 구조를 현재 실행 경로로 간주하거나 `18790`, `19789` 포트를 다시 열지 마세요. 현재 live 상태와 automation 결과를 확인하려면 [`../docs/sentry-triage-migration.md`](../docs/sentry-triage-migration.md)를 참고하세요.

## Preserved files

| Path | Status |
|---|---|
| `sentry/transforms/sentry.js` | 과거 transform source. 현재 runtime 없음 |
| `sentry/SENTRY_RUNBOOK.md` | 현재 Codex triage 정책으로 정리된 기준 |
| `docs/sentry-triage-migration.md` | ownership migration 기록 |
