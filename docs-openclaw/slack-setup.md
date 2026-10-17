# OpenClaw Slack Setup (retired reference)

> 역사 기록입니다. 2026-08-10 현재 OpenClaw gateway와 Socket Mode는 제거되었습니다. 아래 토큰·config·gateway 명령을 실행하지 마세요.

> Source: https://docs.openclaw.ai/channels/slack

---

## Socket Mode (기본값, 권장)

1. Slack App 생성 → Socket Mode 활성화
2. App Token (`xapp-...`) 생성 — `connections:write` scope 필요
3. Bot Token (`xoxb-...`) 생성 — 워크스페이스에 설치
4. `openclaw.json` 에 설정:

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
    }
  }
}
```

또는 환경변수:
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
```

---

## HTTP Events API Mode (대안)

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "...",
      webhookPath: "/slack/events",  // 기본값
    }
  }
}
```

- 같은 경로에서 Event Subscriptions, Interactivity, Slash Commands 처리
- 멀티 계정 HTTP 셋업은 각 계정별 별도 경로 필요

---

## 필수 Bot Scope

| Scope | 용도 |
|-------|------|
| `chat:write` | 메시지 전송 |
| `channels:history` | 채널 히스토리 읽기 |
| `im:history` | DM 히스토리 읽기 |
| `reactions:write` | 리액션 추가 |
| `pins:write` | 핀 관리 |
| `assistant:write` | 타이핑 인디케이터 (스트리밍용) |
| `chat:write.customize` | 커스텀 봇 이름/아이콘으로 전송 |

---

## 필수 Bot Events (Socket Mode)

- `app_mention` — 채널 멘션
- `message.channels` — 공개 채널 메시지
- `message.groups` — 비공개 채널 메시지
- `message.im` — DM 메시지
- `message.mpim` — 그룹 DM 메시지
- `reaction_added`, `reaction_removed`
- `member_joined_channel`, `member_left_channel`
- `channel_rename`
- `pin_added`, `pin_removed`

App Home Messages Tab도 DM 기능에 필요.

---

## User Token (선택)

`userToken: "xoxp-..."` 설정 시 추가 읽기 전용 기능 활성화.
