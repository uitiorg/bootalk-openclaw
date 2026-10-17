# OpenClaw Slack Access Control & Per-Channel Config (retired reference)

> 역사 기록입니다. 현재 Slack live 권한·멘션 상태는 Slack connector로 확인합니다. 아래 OpenClaw config와 pairing 명령은 현재 운영 절차가 아닙니다.

> Source: https://docs.openclaw.ai/channels/slack, /channels/groups, /channels/pairing

---

## DM Policy (`dmPolicy`)

| 값 | 동작 |
|----|------|
| `"pairing"` | 기본값. 미승인 사용자 → 8자 코드 발급, 관리자 승인 필요 |
| `"allowlist"` | `allowFrom` 목록의 사용자만 DM 가능 |
| `"open"` | 누구나 DM 가능 |
| `"disabled"` | DM 완전 차단 |

```json5
// 특정 팀원만 DM 허용
{
  dmPolicy: "allowlist",
  allowFrom: ["U0APRS4J70B", "U0AQ1RUPF4L", "U0AQ1RWGKPW"]
}
```

---

## Channel Policy (`groupPolicy` 역할)

| 값 | 동작 |
|----|------|
| `"open"` | 모든 채널에서 멘션 시 응답 |
| `"allowlist"` | 기본값. `channels` 에 명시된 채널만 |
| `"disabled"` | 채널 메시지 완전 무시 |

---

## 채널별 설정 (핵심!)

`channels.slack.channels.<channelId>` 에 채널별 오버라이드 가능:

```json5
{
  channels: {
    slack: {
      channels: {
        "C0APYE7MLEN": {          // #dev
          allow: true,
          requireMention: true,   // @부톡봇 멘션 필요
          allowBots: false,
          users: ["U0APRS4J70B", "U0AQ1RWGKPW", "U0APRSH0SNP"],
          skills: ["bootalk-calendar"],
          systemPrompt: "You are 부톡봇, assisting the dev team...",
        },
        "C0APYE86NAW": {          // #공지사항
          allow: false,           // 이 채널에서는 응답 안 함
        },
        "#general": {             // 이름으로도 지정 가능
          allow: true,
          requireMention: true,
        }
      }
    }
  }
}
```

### 채널별 필드 전체 목록

| 필드 | 타입 | 설명 |
|------|------|------|
| `allow` | boolean | 이 채널에서 응답 활성화 |
| `requireMention` | boolean | @멘션 없으면 무시 |
| `allowBots` | boolean | 봇 메시지 처리 여부 |
| `users` | string[] | 허용 사용자 ID 목록 |
| `skills` | string[] | 이 채널에서 활성화할 스킬 |
| `systemPrompt` | string | 채널 전용 시스템 프롬프트 |

---

## 멘션 게이팅

채널 메시지는 기본적으로 멘션 필요. 비활성화하려면:
```json5
"C0APYE7MLEN": {
  requireMention: false  // 모든 메시지에 응답
}
```

또는 regex 패턴으로 멘션 인식:
```json5
mentionPattern: "부톡봇|bootalk"
```

스레드 내 봇 메시지에 답글은 암묵적 멘션으로 인식.

---

## Pairing 관리 명령어

```bash
openclaw pairing list slack        # 승인 대기 목록
openclaw pairing approve slack <CODE>  # 승인
```

코드: 8자, 대문자, 모호한 문자(0O1I) 제외, 1시간 만료.
