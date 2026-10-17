# Sentry triage ownership migration

> 상태: 완료된 마이그레이션 기록. 마지막 문서 검토: 2026-08-10 KST.

Sentry triage·보고·예약 polling과 GitHub PR review triage는 OpenClaw에서 Codex automation으로 이전되었습니다. 본 Mac에서는 OpenClaw gateway와 그 local ingress runtime을 더 이상 실행하지 않습니다.

## Current ownership

| Area | Owner | Notes |
|---|---|---|
| Sentry triage and reporting | Codex automation + `sentry-cli` skill | 예약 상태는 `~/.codex/automations/`에서 확인 |
| Performance/error morning checks | Codex automation | report-only, Slack은 state-change 또는 material anomaly만 |
| GitHub PR review triage | Codex automation | 현재 automation이 PAUSED인지 live TOML 확인 |
| Slack delivery | Codex Slack connector 또는 명시적 webhook | webhook 답글이 실행 재개를 의미하지 않음 |
| Public Sentry ingress | 현재 활성 runtime 없음 | 과거 OpenClaw compatibility 문서는 보존용 |

## Important boundaries

- Sentry alert firing, webhook ingress, triage 판단, Slack receipt는 서로 다른 증거입니다.
- PR merge나 CI 성공만으로 production 배포를 주장하지 않습니다.
- 반복된 동일 anomaly는 automation memory 기준으로 억제합니다.
- 자동화가 issue·PR·배포·Slack 쓰기를 수행하는지 prompt의 scope와 실제 결과를 분리해 보고합니다.

## Historical material

`docs-openclaw/sentry-pipeline.md`, `sentry/transforms/sentry.js`와 과거 debug journal은 당시 compatibility ingress와 silent transform을 설명합니다. 현재 서비스를 복원하는 설치·재시작 지침으로 사용하지 마세요.
