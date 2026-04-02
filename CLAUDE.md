# bootalk-openclaw — Claude Code 참조

## 빠른 참조

| 문서 | 경로 | 내용 |
|------|------|------|
| **팀원 & 채널** | `team/channels.md` | Slack 채널 목록, 팀원 ID, 변경 이력 |
| **봇 스킬** | `skills/*/SKILL.md` | 봇 명령어 라우팅 및 스크립트 경로 |
| **캘린더 스크립트** | `scripts/cal.py` | 팀 캘린더 & 연차 CLI |
| **사용자 가이드** | `docs/index.html` | GitHub Pages 공개 문서 |
| **마이그레이션 현황** | `docs/works-migration.html` | WORKS → Slack 이전 기록 |

## 봇 동기화 구조

```
skills/ (이 레포)
    ↓ extraDirs — 직접 참조
OpenClaw Gateway (port 18789, launchd)
    ↓ Socket Mode
Slack
```

- **스킬 수정 반영**: `git pull` → post-merge hook이 gateway 자동 재시작
- **즉시 반영 필요 시**: `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway`

## 팀 구성

> 상세 내용은 `team/channels.md` 참조

| 이름 | Slack ID | 직책 |
|------|----------|------|
| 이훈구 | U0AQ1RUPF4L | CEO |
| 주우철 | U0APRS4J70B | CDO |
| 이현석 | U0AQ1RWGKPW | Dev |
| 정정일 | U0APRSH0SNP | Dev |
| 배지은 | U0APW6HMNR4 | Design / Marketing |
| 전유진 | U0APGQN76CF | Admin / Ops |
| 부톡봇 | U0APV0B0GKX | Bot |

## 채널 요약

| 채널 | 대상 |
|------|------|
| #공지사항 #업무규칙 #회사내규 #부톡-온보딩 #cs #brokerage | 전원 |
| #dev #sentry-alerts | 개발팀 (주우철, 이현석, 정정일) |
| #marketing | 이훈구, 배지은 |
| #design | 이훈구, 배지은, 주우철 |
| #admin 🔒 | 이훈구, 이현석, 전유진, 주우철 |

## 주요 규칙

- `docs/` 폴더만 GitHub Pages에 노출됨 — 민감 정보는 `docs/` 외부에 둘 것
- 봇 토큰/크리덴셜은 절대 커밋하지 말 것 (`.gitignore` 참조)
- 스킬에서 연차/휴가 조회 시 반드시 `leaves` 명령 사용 (`agenda` 사용 금지)
