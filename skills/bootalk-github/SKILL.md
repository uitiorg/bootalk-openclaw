---
name: bootalk_github
description: GitHub 이슈·PR 조회, 팀원 작업 현황, 레포 탐색. "이슈 목록", "PR 현황", "juuc 최근 작업", "frontend 오픈 PR", "이슈 만들어줘" 등.
metadata:
  codex:
    requires:
      bins: [gh]
---

# GitHub 팀 작업 관리

기본 org: `uitiorg` — 모든 `gh` 명령에 적용.

## When to Use

- "이슈 목록 보여줘" / "오픈 PR 어떤 거 있어?"
- "주우철 / 정정일 / 이현석 요즘 뭐 해?"
- "backend 이번 주 머지된 PR"
- "frontend open 이슈 몇 개야?"
- "이슈 만들어줘 — [제목] [내용]"
- "PR #123 뭔 내용이야?"
- "uitiorg 전체 레포 open 이슈 요약"

## 팀원 GitHub ID 매핑

| 이름 | GitHub ID |
|------|-----------|
| 주우철 (CDO) | `juuc` |
| 정정일 (Dev) | `12OneTwo12` |
| 이현석 (Dev) | `hslee-uiti` ← 확인 필요 (활동 없음) |

## 핵심 레포 (uitiorg)

| 레포 | 별칭 | 언어 | 활성 |
|------|------|------|------|
| `frontend-monorepo` | frontend, fe, 프론트 | TS/Next.js/Expo | ✅ |
| `btalk2.1_backend` | backend, be, 백엔드 | Kotlin/Spring | ✅ |
| `legacy-service` | legacy | Java Servlet | ✅ |
| `bootalk-amplify` | amplify | AWS | ✅ |
| `manifest-ops` | infra, ops | K8s YAML | ✅ |
| `bootalk-infra` | infra | IaC | ✅ |
| `ubuntu-crawler` | crawler, db | SQL/Python | ✅ |
| `semugpt-2026` | semugpt | TS/Python | 별도 프로젝트 |

---

## Commands

### 이슈 목록 조회

```bash
# 특정 레포 open 이슈
gh issue list --repo uitiorg/frontend-monorepo --limit 20 --state open

# 레포 이슈를 JSON으로 (레이블·담당자 포함)
gh issue list --repo uitiorg/btalk2.1_backend --limit 20 --state open \
  --json number,title,labels,assignees,createdAt,url

# org 전체에서 특정 키워드 이슈 검색
gh search issues --owner uitiorg --limit 20 "MSA 전환" \
  --json number,title,repository,state,createdAt,url

# 특정 사용자가 연 이슈
gh search issues --author juuc --owner uitiorg --limit 15 \
  --json title,repository,state,createdAt,url
```

### PR 조회

```bash
# 특정 레포 open PR
gh pr list --repo uitiorg/frontend-monorepo --limit 20 \
  --json number,title,author,state,createdAt,url

# 특정 사용자 최근 PR (org 전체)
gh search prs --author 12OneTwo12 --owner uitiorg --limit 15 \
  --json title,repository,state,createdAt,url

# 머지된 PR (최근)
gh search prs --author juuc --owner uitiorg --state closed --limit 10 \
  --json title,repository,state,createdAt,url

# PR 상세 조회
gh pr view 553 --repo uitiorg/btalk2.1_backend --json title,body,author,state,files
```

### 팀원 작업 현황 (activity)

팀원별 최근 PR + 열린 이슈를 함께 조회:

```bash
USER="juuc"  # 또는 12OneTwo12
# 최근 PR
gh search prs --author "$USER" --owner uitiorg --limit 10 \
  --json title,repository,state,createdAt,url
# 최근 open 이슈
gh search issues --author "$USER" --owner uitiorg --limit 5 \
  --json title,repository,state,createdAt,url
```

### 전체 org 현황 요약

```bash
# 여러 핵심 레포의 open 이슈 수
for repo in frontend-monorepo btalk2.1_backend legacy-service manifest-ops ubuntu-crawler; do
  count=$(gh issue list --repo uitiorg/$repo --state open --json number 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
  echo "$repo: $count open"
done

# 여러 레포 오픈 PR 수
for repo in frontend-monorepo btalk2.1_backend; do
  count=$(gh pr list --repo uitiorg/$repo --state open --json number 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
  echo "$repo PR: $count open"
done
```

### 이슈 생성

```bash
gh issue create \
  --repo uitiorg/frontend-monorepo \
  --title "이슈 제목" \
  --body "이슈 내용" \
  --label "bug"
```

### 레포 목록

```bash
gh repo list uitiorg --limit 50 --json name,description,isPrivate,updatedAt \
  | python3 -c "
import sys, json
repos = json.load(sys.stdin)
for r in sorted(repos, key=lambda x: x['updatedAt'], reverse=True):
    vis = '🔒' if r['isPrivate'] else '🌐'
    print(f\"{vis} {r['name']}: {r.get('description','')[:50]}\")
"
```

---

## Response Format

- 이슈/PR 목록: `#번호 제목 (레포, 날짜)` 형식으로 Slack 친화적 출력
- 팀원 현황: "최근 PR N개 / 오픈 이슈 N개" 요약 후 핵심 항목 나열
- 에러 시: `gh auth status` 확인 후 재시도
- 링크 포함 시: GitHub URL 그대로 첨부 (Slack이 미리보기 표시)
- 한국어로 답변
