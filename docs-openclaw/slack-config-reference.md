# OpenClaw Slack Config — Full Reference (retired reference)

> 역사 기록입니다. `openclaw.json`을 만들거나 토큰을 입력하는 현재 설정 가이드가 아닙니다. 현재 예약 작업은 Codex automation이 소유합니다.

> Source: https://docs.openclaw.ai/gateway/configuration-reference

---

## 전체 필드 테이블

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `enabled` | boolean | false | Slack 연동 활성화 |
| `botToken` | string | — | 필수. 환경변수: `SLACK_BOT_TOKEN` |
| `appToken` | string | — | Socket Mode 필수. 환경변수: `SLACK_APP_TOKEN` |
| `signingSecret` | string | — | HTTP mode 필수 |
| `mode` | enum | `"socket"` | `"socket"` \| `"http"` |
| `dmPolicy` | enum | `"pairing"` | `"pairing"` \| `"allowlist"` \| `"open"` \| `"disabled"` |
| `allowFrom` | string[] | `[]` | allowlist 모드 시 허용 사용자 ID |
| `historyLimit` | number | 50 | 컨텍스트 히스토리 메시지 수 |
| `allowBots` | boolean | false | 봇 메시지 처리 여부 (글로벌) |
| `reactionNotifications` | enum | `"own"` | `"off"` \| `"own"` \| `"all"` \| `"allowlist"` |
| `reactionAllowlist` | string[] | `[]` | allowlist 시 리액션 알림 받을 사용자 |
| `replyToMode` | enum | `"first"` | `"off"` \| `"first"` \| `"all"` |
| `streaming` | enum | `"partial"` | `"off"` \| `"partial"` \| `"block"` \| `"progress"` |
| `nativeStreaming` | boolean | true | Slack 네이티브 스트리밍 사용 (`assistant:write` 필요) |
| `textChunkLimit` | number | 4000 | 메시지당 최대 글자 수 |
| `chunkMode` | enum | `"length"` | `"length"` \| `"paragraph"` |
| `mediaMaxMb` | number | 20 | 첨부 파일 최대 크기 (MB) |
| `typingReaction` | string | `"hourglass_flowing_sand"` | 처리 중 임시 리액션 이모지 |

---

## 완성된 JSON5 예시 (부톡봇용)

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: process.env.SLACK_BOT_TOKEN,
      appToken: process.env.SLACK_APP_TOKEN,

      // DM: 팀원 전용
      dmPolicy: "allowlist",
      allowFrom: [
        "U0AQ1RUPF4L",  // 이훈구
        "U0APRS4J70B",  // 주우철
        "U0AQ1RWGKPW",  // 이현석
        "U0APRSH0SNP",  // 정정일
        "U0APW6HMNR4",  // 배지은
        "U0APGQN76CF",  // 전유진
      ],

      // 채널별 설정
      channels: {
        "C0APYE7MLEN": {            // #dev
          allow: true,
          requireMention: true,
          users: ["U0APRS4J70B", "U0AQ1RWGKPW", "U0APRSH0SNP"],
          skills: ["bootalk-calendar"],
          systemPrompt: "You are 부톡봇 assisting the dev team. Be concise.",
        },
        "C0APWC7RSSJ": {            // #cs
          allow: true,
          requireMention: true,
        },
        "C0APYE86NAW": {            // #공지사항 (읽기 전용)
          allow: false,
        },
      },

      // 스레딩
      replyToMode: "first",
      thread: {
        historyScope: "thread",
        inheritParent: false,
      },

      // 스트리밍
      streaming: "partial",
      nativeStreaming: true,

      // 액션
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },

      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      mediaMaxMb: 20,
    },
  },
}
```

---

## dm 세부 설정

```json5
dm: {
  enabled: true,
  groupEnabled: false,       // 그룹 DM 활성화 여부 (기본: false)
  groupChannels: ["G123"],   // groupEnabled 시 허용 그룹 ID
}
```

---

## actions 세부 설정

```json5
actions: {
  reactions: true,     // 리액션 추가/제거 이벤트
  messages: true,      // 메시지 수정/삭제 이벤트
  pins: true,          // 핀 추가/제거 이벤트
  memberInfo: true,    // 멤버 정보 조회
  emojiList: true,     // 이모지 목록 조회
}
```

---

## 인터랙티브 답글 (Block Kit)

`[[slack_buttons]]`, `[[slack_select]]` 디렉티브로 Block Kit 버튼/셀렉트 생성 가능.
단, OpenClaw가 `block_actions` 이벤트를 처리해야 동작.

> ⚠️ 현재 부톡봇은 block_actions 미지원 — 버튼 클릭 무반응.
> App Home 버튼도 이 이유로 제거됨 (2026-04-02).
