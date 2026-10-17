# Bootalk Slack 채널 & 멤버 현황

> 마지막 업데이트: 2026-05-04
> GitHub Pages에 노출되지 않음 (docs/ 외부)

---

## 팀원 ID 매핑

| 이름 | Slack ID | 계정명 | 직책 |
|------|----------|--------|------|
| 이훈구 | U0AQ1RUPF4L | ceo.uiti | CEO |
| 주우철 | U0APRS4J70B | cdo.bootalk | CDO |
| 이현석 | U0AQ1RWGKPW | leehs.uiti | Dev |
| 정정일 | U0APRSH0SNP | jji.bootalk | Dev |
| 배지은 | U0APW6HMNR4 | bje.uiti | Design / Marketing |
| 전유진 | U0APGQN76CF | cyj.uiti | Admin / Ops |
| 유상근 | U0B28B4CSRE | ysg.uiti | — |
| 안기웅 | U0B1SV1UQDP | agu.uiti | — |
| 부톡봇 | U0APV0B0GKX | bootalk-bot | Bot |

---

## 채널 목록

### 전사 채널 — 전원 참여

| 채널 | Channel ID | 멤버 | 비고 |
|------|------------|------|------|
| #전체메세지 | C0B1T0GSP89 | 전원 | 전사 공지·메세지 (구 #공지사항 후속) |
| #부톡-온보딩 | C0APW641YA2 | 전원 | 신규 입사자 가이드 + 사내 정책 캔버스 (구 #회사내규/#업무규칙 통합) |
| #cs | C0APWC7RSSJ | 전원 | |
| #중개팀 | C0AQ226BMSQ | 전원 + 외부 공인중개사 | 부톡 서비스에서 고객을 응대하는 공인중개사들이 멤버로 참여 (구 #brokerage) |
| #zerro제로 | C0B1B3YNSGM | — + 봇 | 신규 서비스 **웨이블(Wayble)** 개발 채널 (배출자/수집운반자/처리자 3-role 폐기물 관리 서비스 — 부톡 본 서비스와 분리) |

### 직군별 채널

| 채널 | Channel ID | 멤버 | 비고 |
|------|------------|------|------|
| #bootalk-products | C0APYE7MLEN | 주우철, 이현석, 정정일, 이훈구, 배지은, 안기웅 + 봇 | 개발/제품 (구 #dev) |
| #dev-private 🔒 | C0APWC6KXQE | 주우철, 이현석, 정정일 + 봇 | 시크릿 + Sentry 알림 (구 #sentry-alerts, private 전환) |
| #mktg-sales | C0APV20P03X | 이훈구, 배지은 + 봇 | (구 #marketing) |
| #design | C0APT0W6B43 | 이훈구, 배지은, 주우철 + 봇 | |
| #admin 🔒 | C0AQSN4B680 | 이훈구, 이현석, 전유진, 주우철 + 봇 | PRIVATE |

### 아카이브된 채널

| 채널 | Channel ID | 아카이브 일자 | 사유 |
|------|------------|--------------|------|
| #회사내규 | C0AQSN880NL | 2026-05-04 | 캔버스 #부톡-온보딩 으로 통합 |
| #업무규칙 | C0AQSN8AEGY | 2026-05-04 | 캔버스 #부톡-온보딩 으로 통합 |
| #공지사항 | C0APYE86NAW | 2026-05-04 | 캔버스 #전체메세지 로 이전 |
| #developers | C0AQSUFK5Q9 | 2026-04-28 | #dev-private 으로 통합 |

---

## 변경 이력

| 날짜 | 채널 | 변경 |
|------|------|------|
| 2026-05-06 | #zerro제로 | 봇 join (캔버스 없음) |
| 2026-05-04 | #회사내규/#업무규칙/#공지사항 | 캔버스 이전 후 아카이브 |
| 2026-05-04 | #sentry-alerts → #dev-private | private 전환 + 이름 변경 |
| 2026-04-02 | #sentry-alerts | 이훈구, 배지은, 전유진 제거 → 개발팀만 유지 |
| 2026-04-02 | #admin | 주우철 추가 |
| 2026-04-02 | #design | 주우철 추가 |

---

## 봇 정보

| 항목 | 값 |
|------|----|
| Bot ID | B0AQSLK8AF2 |
| Bot User ID | U0APV0B0GKX |
| Token | `SLACK_BOT_TOKEN` 환경변수 참고 |
| Missing scopes | channels:join, bookmarks:write, usergroups:read, users.profile:read |
