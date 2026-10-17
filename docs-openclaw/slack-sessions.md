# OpenClaw Slack Sessions & Threading (retired reference)

> 역사 기록입니다. 현재 OpenClaw session store나 Slack Socket Mode session은 실행되지 않습니다.

> Source: https://docs.openclaw.ai/channels/slack, /channels/channel-routing

---

## 세션 키 패턴

| 컨텍스트 | 세션 키 형식 |
|----------|-------------|
| DM | `agent:<agentId>:main` (기본값: dmScope=main으로 collapse) |
| 채널 | `agent:<agentId>:slack:channel:<channelId>` |
| 스레드 | `agent:<agentId>:slack:channel:<channelId>:thread:<threadId>` |
| 그룹 DM | `agent:<agentId>:group:<groupId>` |

---

## Thread History Scope

```json5
{
  channels: {
    slack: {
      thread: {
        historyScope: "thread",   // "thread" | "channel" | "none"
        inheritParent: false,     // 부모 채널 히스토리 포함 여부
      }
    }
  }
}
```

- `"thread"` (기본값): 해당 스레드 대화만 컨텍스트로 사용
- `"channel"`: 채널 전체 히스토리 포함
- `"none"`: 히스토리 없이 새 컨텍스트

---

## Reply Threading Mode

```json5
replyToMode: "off"   // "off" | "first" | "all"
```

| 값 | 동작 |
|----|------|
| `"off"` | 모든 Slack 스레드 답글 비활성화 (explicit [[reply_to_*]] 태그도 무시) |
| `"first"` | 첫 메시지에만 스레드 |
| `"all"` | 모든 메시지에 스레드 |

> ⚠️ `replyToMode: "off"` 는 explicit `[[reply_to_*]]` 태그도 비활성화함.

수동 태그 예: `[[reply_to_thread]]`, `[[reply_to_channel]]`

---

## DM 세션 범위

```json5
session: {
  dmScope: "main"   // DM 대화를 main 세션으로 collapse (기본값)
}
```

`dmScope: "user"` 로 변경하면 사용자별 별도 세션 유지.

---

## 히스토리 컨텍스트 크기

```json5
historyLimit: 50   // 컨텍스트에 포함할 메시지 수 (기본값: 50)
```

---

## 세션 저장 위치

```
~/.openclaw/agents/<agentId>/sessions/sessions.json
~/.openclaw/agents/<agentId>/sessions/<sessionKey>.jsonl  ← 대화 트랜스크립트
```
