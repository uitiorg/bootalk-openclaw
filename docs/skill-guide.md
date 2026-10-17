# Skill 작성 가이드

이 repo의 skill은 AI가 업무 절차와 판단 기준을 재사용할 수 있도록 작성한 Markdown 문서입니다. 현재 저장소가 스킬을 자동 로딩하거나 상주 봇에 배포하지는 않습니다. Codex에 실제로 사용할 스킬은 Codex skill 디렉터리에 설치되어 있어야 하며, 이 repo의 파일은 versioned source와 검토용 기준으로 취급합니다.

## 기본 구조

```text
skills/
└── my-skill/
    └── SKILL.md
```

```markdown
---
name: skill_name
description: 한 줄 설명. AI가 사용 여부를 판단할 수 있는 트리거를 포함
metadata:
  codex:
    requires:
      env: [MAIN_API_KEY]
      bins: [curl, jq]
---

# 스킬 제목

## When to Use
- 어떤 요청에 사용하는지
- 실제 사용자가 말할 트리거 키워드

## Authentication
필요한 인증과 secret 주입 위치를 설명합니다. 값 자체는 넣지 않습니다.

## Commands
실행할 명령과 예상 결과를 작성합니다.

## Safety
쓰기 작업, 승인, dry-run, 확인해야 할 대상을 명시합니다.

## Response Format
결과·링크·확인 제한을 어떻게 보고할지 작성합니다.
```

## 핵심 원칙

1. `When to Use`는 모호한 키워드보다 실제 요청 예시를 사용합니다.
2. 읽기와 쓰기 명령을 구분하고, 쓰기에는 필요한 승인과 확인값을 적습니다.
3. 채널·사용자·레포 ID는 snapshot일 수 있으므로 live 조회를 요구합니다.
4. 환경변수와 secret 경로만 문서화하고 token 값은 절대 넣지 않습니다.
5. 명령은 현재 작업 디렉터리와 필요한 도구를 명확히 지정합니다.
6. 자동화가 실패했을 때 재시도·중복 전송·부분 성공을 어떻게 처리할지 적습니다.

## 새 스킬 추가 후

- Codex에서 실제 사용할 경우 설치된 skill 경로에도 반영합니다.
- 예약 automation이 사용하는 스킬이면 해당 automation prompt와 memory 경로를 함께 확인합니다.
- `git diff`, Markdown 링크, 명령의 존재 여부를 확인합니다.
- OpenClaw gateway 재시작이나 Socket Mode 연결을 수행할 필요는 없습니다.
