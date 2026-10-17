# OpenClaw Channel Routing (retired reference)

> 역사 기록입니다. 현재 OpenClaw channel routing이나 세션 저장 경로는 실행되지 않습니다. 현재 Slack 대상은 Codex Slack connector에서 live state를 조회하세요.

> Source: https://docs.openclaw.ai/channels/channel-routing

---

## 라우팅 우선순위 (8단계)

1. Exact peer match via bindings
2. Parent peer/thread inheritance
3. Discord guild + roles matching
4. Guild-only matching
5. **Slack team matching** ← 부톡봇 해당
6. Account-specific routing
7. Channel-wide routing (any account)
8. Default agent fallback

바인딩에 여러 매칭 필드가 있으면 **모든 필드가 일치해야** 적용.

---

## 세션 키 패턴

| 타입 | 키 형식 |
|------|---------|
| DM | `agent:<agentId>:main` |
| 채널 | `agent:<agentId>:slack:channel:<channelId>` |
| 스레드 | `agent:<agentId>:slack:channel:<channelId>:thread:<threadId>` |
| 그룹 | `agent:<agentId>:<channel>:group:<id>` |

---

## 멀티 계정 설정

여러 Slack 계정이 있을 경우 기본 계정 명시:
```json5
{
  channels: {
    slack: {
      defaultAccount: "bootalk-workspace"
    }
  }
}
```

---

## 세션 저장 경로

```
~/.openclaw/agents/<agentId>/sessions/sessions.json
~/.openclaw/agents/<agentId>/sessions/<sessionKey>.jsonl
```

커스텀 경로 설정 시 `{agentId}` 템플릿 사용 가능.

---

## Broadcast Groups

여러 에이전트가 같은 채널/피어에 동시 응답:
```json5
{
  broadcastGroups: {
    "team-channel": {
      strategy: "parallel",
      agents: ["agent1", "agent2"]
    }
  }
}
```
