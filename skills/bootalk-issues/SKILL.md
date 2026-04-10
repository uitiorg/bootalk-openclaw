---
name: bootalk_issues
description: Production 이슈 등록·조회·해결. "이슈 등록: 매물 상세 로딩 안됨", "이슈 목록", "이슈 해결: #47", "프로덕션 버그", "production bug" 등.
metadata:
  openclaw:
    requires:
      env: [SLACK_BOT_TOKEN]
      bins: [gh, python3]
---

# Production Issue Tracker

production에서 발견된 이슈를 GitHub Issues로 관리하고 Weekly Board 캔버스에 표시.

## When to Use

- "이슈 등록: [설명]" / "프로덕션 버그: [설명]" / "production bug: [설명]"
- "이슈 목록" / "열린 이슈" / "production issues"
- "이슈 해결: #번호" / "이슈 닫아줘: #번호"

## 팀원 매핑

| 이름 | GitHub ID | Slack ID |
|------|-----------|----------|
| 주우철 | juuc | U0APRS4J70B |
| 정정일 | 12OneTwo12 | U0APRSH0SNP |
| 이현석 | hslee-uiti | U0AQ1RWGKPW |

## 레포 매핑

| 별칭 | 레포 | 약어 |
|------|------|------|
| frontend, fe, 프론트 | frontend-monorepo | fe |
| backend, be, 백엔드 | btalk2.1_backend | be |
| legacy | legacy-service | legacy |
| infra, ops | bootalk-infra | infra |
| crawler, db | ubuntu-crawler | crawler |

기본 org: `uitiorg`

---

## Commands

### 이슈 등록

유저가 "이슈 등록: {설명}" 형태로 요청하면 아래 순서대로 실행:

**Step 1 — bootalk-ui 매핑 분석**

```bash
LOOKUP=~/.claude/skills/bootalk-ui/scripts/lookup.py

# 유저 설명에서 키워드 추출 후 검색
python3 $LOOKUP --search "{키워드}"

# 결과가 없으면 개념 검색 시도
python3 $LOOKUP --concept "{키워드}"
```

검색 결과에서 추출할 정보:
- 관련 섹션 (§0-1 ~ §6)
- API 엔드포인트 or Legacy Protocol 번호
- DB 테이블명

**Step 2 — 레포 결정**

검색 결과 기반으로 레포 판단:
- MSA 엔드포인트 (`/aparts/`, `/real-price/` 등) → `btalk2.1_backend`
- Legacy Protocol (10238, 539, 10259 등) → `legacy-service`
- UI 렌더링/프론트엔드 컴포넌트 문제 → `frontend-monorepo`
- 크롤러/DB 데이터 문제 → `ubuntu-crawler`
- 판단 불가 시 → `frontend-monorepo` (기본값)

**Step 3 — GitHub Issue 생성**

```bash
REPO="frontend-monorepo"  # Step 2에서 결정된 레포
TITLE="이슈 제목 (유저 설명 요약)"

gh issue create \
  --repo uitiorg/$REPO \
  --title "$TITLE" \
  --label "production-bug" \
  --body "$(cat <<'ISSUE_EOF'
## Production Issue Report

**보고 내용:** {유저 원문 그대로}
**보고자:** {Slack 메시지 보낸 사람 이름}
**보고 채널:** #dev

## 자동 분석
- **관련 컴포넌트:** {lookup.py 결과 — 섹션, 라벨, API}
- **데이터 소스:** {API endpoint → service → DB table}

## 상태
- [x] 등록
- [ ] 해결

> 이 이슈는 부톡봇에 의해 자동 생성되었습니다.
ISSUE_EOF
)"
```

생성된 이슈 URL을 파싱하여 저장.

**Step 4 — Weekly Board 캔버스 즉시 업데이트**

```bash
node ~/.openclaw/workspace/scripts/weekly-board.mjs
```

**Step 5 — 콜백 메시지 작성**

매핑 결과 확신도에 따라:

확신도 높음 (검색 결과 있음):
```
이슈 #{번호} 등록 완료

제목: {제목}
레포: uitiorg/{레포}
관련 컴포넌트: {섹션 라벨} → {API 엔드포인트} → {DB 테이블}
링크: {GitHub URL}
```

확신도 낮음 (검색 결과 없음 또는 모호):
```
이슈 #{번호} 등록 완료

제목: {제목}
레포: uitiorg/{레포} (레포 확인 필요)
관련 컴포넌트: 특정 불가 — 추가 정보 필요
링크: {GitHub URL}

어떤 화면에서 발생하는지 알 수 있을까요?
```

### 이슈 목록

```bash
# 전체 레포 open production-bug 이슈 조회
for repo in frontend-monorepo btalk2.1_backend legacy-service bootalk-infra ubuntu-crawler; do
  gh issue list --repo uitiorg/$repo --label production-bug --state open \
    --json number,title,assignees,createdAt,url 2>/dev/null
done
```

응답 형식:
```
Production Issues — Open ({N}건)

• #{번호} {제목} — {레포약어} — {담당자 또는 미배정} — {등록일}
• #{번호} {제목} — {레포약어} — {담당자 또는 미배정} — {등록일}
```

### 이슈 해결

유저가 "이슈 해결: #{번호}" 요청 시:

```bash
# 번호로 이슈 찾기 (어느 레포인지 탐색)
for repo in frontend-monorepo btalk2.1_backend legacy-service bootalk-infra ubuntu-crawler; do
  gh issue view {번호} --repo uitiorg/$repo --json state,title,url 2>/dev/null && break
done

# 이슈 닫기
gh issue close {번호} --repo uitiorg/{찾은레포}
```

캔버스 업데이트:
```bash
node ~/.openclaw/workspace/scripts/weekly-board.mjs
```

콜백:
```
이슈 #{번호} 해결 완료

{제목} — closed
```

---

## Response Format

- 등록/해결 결과는 위 콜백 형식에 맞춰 응답
- 목록은 bullet 형식으로 정리
- GitHub URL 포함 (Slack에서 미리보기 표시)
- 한국어로 답변
