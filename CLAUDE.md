# bootalk-openclaw — Claude Code reference

이 저장소는 현재 OpenClaw 런타임이 아니라 Bootalk operations library로 사용됩니다.

## 빠른 참조

| 문서 | 경로 | 내용 |
|---|---|---|
| 팀원·채널 snapshot | `team/channels.md` | Slack ID와 과거 변경 이력. live 검증 필수 |
| 업무 스킬 | `skills/*/SKILL.md` | 재사용 가능한 실행 절차 |
| 캘린더 CLI | `scripts/cal.py` | 팀 일정·연차·HR 메일 |
| 공개 가이드 | `docs/` | 현재 문서와 역사 기록 |
| Codex automation | `/Users/juucheol/.codex/automations/` | 예약 작업의 실제 상태 |

## 현재 실행 구조

```text
Codex automation ── 예약 점검·보고
Slack connector ─── live Slack 조회·명시적 전송
이 repo의 scripts ── 사용자가 요청한 직접 실행형 업무
```

OpenClaw gateway, Socket Mode, `extraDirs`, `18789` 포트와 `launchctl` 재시작 명령은 폐기된 구성입니다. 관련 자료는 `docs-openclaw/`에 보존용으로 남아 있습니다.

## 작업 규칙

- Slack 대상은 `team/channels.md`가 아니라 live connector 결과로 확인합니다.
- side effect가 있는 캘린더·메일·Slack·GitHub 작업은 명시적 요청이 있을 때만 실행합니다.
- 연차 조회는 `leaves`, 등록은 `leave --remaining "..."` 규칙을 지킵니다.
- secret, OAuth 파일, webhook URL, 내부 API key를 출력하거나 커밋하지 않습니다.
- 문서 변경 후 stale OpenClaw 경로와 깨진 링크를 검색하고 관련 테스트를 실행합니다.

자세한 규칙은 [`AGENTS.md`](AGENTS.md)를 기준으로 합니다.
