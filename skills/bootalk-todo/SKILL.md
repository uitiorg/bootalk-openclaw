---
name: bootalk_todo
description: Google Docs TODO 시트에 할일을 추가/조회합니다.
metadata:
  openclaw:
    requires:
      bins: [gog]
---

# 부톡 TODO 관리

## When to Use
- 사용자가 할일 추가, 태스크, TODO, 업무 등록을 요청할 때
- "할일 추가해줘", "TODO에 넣어줘", "업무 등록" 등

## Context
- TODO 문서: "주우철, 정정일 TO DO (2026)"
- gog alias: `todo`
- 4-column table: 시작미팅 / 관계자 / 내용 / 예정완료일자
- 계정: cdo.bootalk@gmail.com

## Commands

### TODO 목록 조회
```bash
gog docs read todo
```

### TODO 추가
Google Docs API로 테이블 row 삽입 (insertTableRow, row 1 아래):

```bash
# gog를 통한 토큰으로 Google Docs API 직접 호출
# 새 행 추가 후 셀 내용 채우기
gog docs write todo --content "{내용}"
```

## Response Format
- 추가 완료 시: 추가된 내용과 예정완료일자를 확인 메시지로 응답
- 조회 시: 표 형태로 현재 TODO 목록 정리
