---
name: bootalk_weekly_report
description: 주간 보고, 업무 요약, 이번 주 뭐했어, 대표님 보고용 경영진 리포트 생성. 비개발자 언어로 번역.
metadata:
  openclaw:
    requires:
      bins: [gh, jq]
---

# 주간 보고 생성

## When to Use
- 사용자가 주간 보고, 이번 주 요약, 업무 보고를 요청할 때
- "이번 주 뭐했어?", "주간 보고 만들어줘", "대표님한테 보고할 거 정리해줘" 등

## Data Collection

지난 7일간의 GitHub 활동을 수집한다:

```bash
# 전체 팀원 merged PR
gh search prs --org=uitiorg --merged --created=">=$(date -v-7d +%Y-%m-%d)" --json repository,title,state,number,author --limit 200

# 전체 팀원 closed issues
gh search issues --org=uitiorg --state=closed --created=">=$(date -v-7d +%Y-%m-%d)" --json repository,title,number,author --limit 200
```

## Report Format

비개발자(대표)가 읽을 수 있도록 기술 용어를 최소화한다:

```
이번 주 개발팀 업무 요약 ({START} ~ {END})

완료: N건
  - 기능 개선: N건
  - 버그 수정: N건
  - 인프라/보안: N건

주요 성과:
  - {가장 임팩트 있는 작업 1~3개, 비개발자 언어로}

진행 중:
  - {open PR/Issue 중 중요한 것}

다음 주 예정:
  - {Keep 섹션 기반 추정}
```

## Guidelines
- PR 제목의 기술 용어를 비개발자 언어로 번역
- 예: "fix: apt_supply_pyeong INNER JOIN → LEFT JOIN" → "아파트 면적 데이터 조회 오류 수정"
- 숫자로 임팩트 표현 (수정된 건수, 영향받는 단지 수 등)
