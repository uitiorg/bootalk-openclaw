---
name: bootalk_kpt
description: uitiorg GitHub 활동을 수집하여 주간 KPT 회고를 생성하고 team-discussions에 게시합니다.
metadata:
  openclaw:
    requires:
      bins: [gh, jq]
---

# KPT 회고 생성

## When to Use
- 사용자가 KPT, 회고, 주간 보고, 이번 주 한 일을 요청할 때
- "KPT 만들어줘", "회고 생성", "이번 주 정리" 등

## Step 1: 기간 확인

이전 KPT 종료일 ~ 오늘이 이번 회고 기간이다.

```bash
gh api graphql -f query='{ repository(owner: "uitiorg", name: "team-discussions") { discussions(last: 100, categoryId: "DIC_kwDOOXHhes4Cuurh") { nodes { title number createdAt } } } }' | jq '[.data.repository.discussions.nodes[] | select(.number != 40)] | sort_by(.createdAt) | last'
```

## Step 2: 데이터 수집 (병렬)

```bash
# PR 검색
gh search prs --author=juuc --created=">=${START_DATE}" --json repository,title,state,number,createdAt --limit 100

# Issue 검색
gh search issues --author=juuc --created=">=${START_DATE}" --json repository,title,state,number,createdAt --limit 100

# ubuntu-crawler 커밋 (PR 없이 직접 푸시)
gh api repos/uitiorg/ubuntu-crawler/commits --jq '.[] | select(.author.login == "juuc") | select(.commit.author.date > "${START_DATE}") | {sha: .sha[0:7], message: .commit.message | split("\n")[0], date: .commit.author.date}'
```

## Step 3: 분류 기준

uitiorg/ 조직 레포만 포함 (외부 레포 제외).

| state | 섹션 |
|-------|------|
| merged PR | Done |
| closed Issue | Done > Closed Issues |
| open PR | Keep |
| open Issue | Keep |

Done 카테고리: PR 제목 prefix로 분류 (fix, feat, refactor, chore 등). Sentry 관련은 "Sentry 에러 핸들링" 그룹, 릴리즈 관련은 "릴리즈" 그룹으로 묶기.

## Step 4: 양식

- 링크: `uitiorg/repo#번호` (GitHub 파싱용)
- PR 제목이 충분하면 하이픈 뒤 설명 생략
- Problem/Try는 서술형

```markdown
## KPT 회고 ({START_DATE} ~ {END_DATE})

### Done
**카테고리명**
- uitiorg/repo#번호

**Closed Issues**
- uitiorg/repo#번호

---

### Keep
- uitiorg/repo#번호

---

### Problem
- 서술형 문제점 (관련 이슈 링크)

---

### Try
- 서술형 시도할 것 (관련 이슈 링크)
```

## Step 5: 사용자 확인

작성된 회고를 보여주고 수정 요청이 있으면 반영한다.

## Step 6: Discussion 생성 + 코멘트

사용자 승인 후에만 실행한다.

```bash
# Discussion 생성
gh api graphql -f query='mutation { createDiscussion(input: { repositoryId: "R_kgDOOXHheg", categoryId: "DIC_kwDOOXHhes4Cuurh", title: "{TITLE}", body: "{START_DATE}부터 {END_DATE}까지 있었던 일을 공유하고 회고해주시면 감사하겠습니다.\n\nhttps://github.com/uitiorg/team-discussions/discussions/40\n\n회고 방법은 위와 같습니다." }) { discussion { number url id } } }'

# KPT 내용을 코멘트로 작성
gh api graphql -f query='mutation { addDiscussionComment(input: { discussionId: "{DISCUSSION_ID}", body: "{KPT_CONTENT}" }) { comment { url } } }'
```
