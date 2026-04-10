# Production Issue Tracking System — Design Spec

**Date:** 2026-04-10
**Channel:** #dev (C0APYE7MLEN)
**Goal:** Production에서 발견된 이슈를 #dev 채널에서 봇을 통해 등록하고, GitHub Issues + Slack Canvas로 추적하는 시스템

---

## 전체 흐름

```
유저: @부톡봇 이슈 등록: 매물 상세 페이지 로딩 안됨

[1] bootalk-issues 스킬 트리거
[2] bootalk-ui lookup.py로 컴포넌트/API/DB 소스 자동 파악
[3] 해당 레포에 GitHub Issue 생성 (label: production-bug)
[4] Weekly Board 캔버스에 이슈 섹션 즉시 업데이트
[5] #dev 채널에 분석 콜백 메시지 응답
```

## 명령어

| 명령어 | 예시 | 동작 |
|--------|------|------|
| `이슈 등록: {설명}` | `이슈 등록: 매물 상세 페이지 로딩 안됨` | 분석 → GitHub Issue 생성 → 캔버스 → 콜백 |
| `이슈 목록` | `이슈 목록` | 열린 production-bug 이슈 요약 |
| `이슈 해결: {번호}` | `이슈 해결: #47` | GitHub Issue close → 캔버스 → 콜백 |

## 레포 자동 배정

1. lookup.py `--search`로 유저 설명 키워드 매칭
2. 매핑 결과의 API 소스 기반 레포 결정:
   - 프론트엔드 UI 렌더링 문제 → `frontend-monorepo`
   - MSA 서비스 (`apart_service`, `real_price_service` 등) → `btalk2.1_backend`
   - Legacy Protocol 관련 → `legacy-service`
   - 인프라/배포 → `bootalk-infra`
3. 판단 불가 시 → `frontend-monorepo` 기본값 + 콜백에 "레포 확인 필요" 표시

## GitHub Issue 템플릿

```markdown
## Production Issue Report

**보고 내용:** {유저 원문}
**보고자:** {Slack 유저 이름}
**보고 채널:** #dev

## 자동 분석
- **관련 컴포넌트:** {bootalk-ui 매핑 결과}
- **데이터 소스:** {API endpoint → service → DB table}

## 상태
- [x] 등록
- [ ] 해결

> 이 이슈는 부톡봇에 의해 자동 생성되었습니다.
```

## Slack 캔버스 현황판

기존 Weekly Board 캔버스에 Production Issues 섹션 추가:

```
# Weekly Board — 4/7 ~ 4/13

## Review 대기
...

## Merged (최근 7일)
...

## Production Issues — Open (2)
- #47 매물 상세 페이지 로딩 안됨 — fe — 미배정 — 4/10
- #45 대출 추천 금리 표시 오류 — be — @정정일 — 4/8

## Production Issues — Resolved This Week (1)
- #44 지도 마커 클릭 안됨 — fe — @주우철 — 해결 4/9
```

### 업데이트 방식 (이중)

- **즉시**: bootalk-issues 스킬이 등록/해결 시 weekly-board.mjs를 직접 실행
- **동기화**: 기존 weekly-board 폴러가 1시간마다 issues 섹션도 함께 갱신

## 콜백 메시지

### 확신도 높음 (매핑 매치)

```
이슈 #47 등록 완료

제목: 매물 상세 페이지 로딩 안됨
레포: uitiorg/frontend-monorepo
관련 컴포넌트: ApartDetailPage → GET /api/v2/apart/{id} → apart_service
링크: https://github.com/uitiorg/frontend-monorepo/issues/47
```

### 확신도 낮음 (매핑 불확실)

```
이슈 #48 등록 완료

제목: 앱 실행 시 흰 화면
레포: uitiorg/frontend-monorepo (레포 확인 필요)
관련 컴포넌트: 특정 불가 — 추가 정보 필요
링크: https://github.com/uitiorg/frontend-monorepo/issues/48

어떤 화면에서 발생하는지 알 수 있을까요?
```

### 이슈 해결

```
이슈 #47 해결 완료

매물 상세 페이지 로딩 안됨 — closed by @주우철
```

## 의존성

- `gh` CLI (GitHub Issue CRUD)
- `python3` + `lookup.py` (bootalk-ui 매핑 조회)
- `SLACK_BOT_TOKEN` (Canvas API)
- 기존 인프라: weekly-board.mjs, LaunchAgent

## 파일 구조

| 작업 | 파일 |
|------|------|
| 생성 | `skills/bootalk-issues/SKILL.md` |
| 수정 | `~/.openclaw/workspace/scripts/weekly-board.mjs` |
