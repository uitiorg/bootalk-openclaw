# Slack App 설정 기록

> 상태: 역사 기록. 2026-08-10 현재 본 Mac의 OpenClaw gateway와 Socket Mode는 제거되었습니다.

이 문서는 과거 Bootalk Slack App을 OpenClaw에 연결할 때 사용했던 설정 기록입니다. 현재 Slack live context와 메시지 작업은 Codex Slack connector 또는 명시적인 Slack API 호출을 사용합니다.

현재 작업에서 이 문서의 `xapp-`, `xoxb-`, `openclaw.json`, Socket Mode, `openclaw gateway` 명령을 실행하지 마세요. 토큰을 재발급하거나 Slack App을 변경해야 하는 경우에는 Slack connector와 공식 Slack App 설정을 기준으로 별도 검토합니다.

과거 설정의 목적은 다음과 같았습니다.

- Slack App에 필요한 Bot Scope와 Event Subscription을 기록
- App Home과 DM 사용 설정을 기록
- Socket Mode 연결 확인 명령을 기록

현재 repo 운영 기준은 [`AGENTS.md`](../AGENTS.md)와 [`README.md`](../README.md)입니다.
