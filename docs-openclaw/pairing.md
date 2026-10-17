# OpenClaw Pairing (retired reference)

> 역사 기록입니다. 현재 Mac에는 OpenClaw pairing store와 gateway가 없습니다. 아래 명령을 실행하지 마세요.

> Source: https://docs.openclaw.ai/channels/pairing

---

## DM Pairing이란?

`dmPolicy: "pairing"` (기본값) 설정 시, 미승인 사용자가 DM을 보내면:
1. 사용자에게 8자 코드 전송 (대문자, 모호한 문자 0O1I 제외)
2. 코드 1시간 내 만료
3. 관리자가 CLI로 승인해야 DM 처리 시작

---

## 관리 명령어

```bash
# 승인 대기 목록 보기
openclaw pairing list slack

# 승인
openclaw pairing approve slack <CODE>
```

---

## Pairing 파일 위치

```
~/.openclaw/credentials/slack-pending.json    ← 대기 요청
~/.openclaw/credentials/slack-allowlist.json  ← 승인된 목록
```

---

## 부톡봇 권장 설정

6명 소규모 팀이므로 pairing 불필요. `allowlist` 사용 권장:

```json5
{
  dmPolicy: "allowlist",
  allowFrom: [
    "U0AQ1RUPF4L",  // 이훈구
    "U0APRS4J70B",  // 주우철
    "U0AQ1RWGKPW",  // 이현석
    "U0APRSH0SNP",  // 정정일
    "U0APW6HMNR4",  // 배지은
    "U0APGQN76CF",  // 전유진
  ]
}
```
