# Skill 작성 가이드

## Skill이란?

AI에게 "이럴 때 이 도구를 써라"라고 알려주는 **마크다운 파일**입니다.
코드가 아니므로 배포 없이 파일 수정만으로 즉시 반영됩니다.

## 기본 구조

```
skills/
└── my-skill/
    └── SKILL.md
```

## SKILL.md 템플릿

```markdown
---
name: skill_name
description: 한 줄 설명 (AI가 이 설명을 보고 사용 여부를 판단)
metadata:
  openclaw:
    primaryEnv: MAIN_API_KEY
    requires:
      env: [MAIN_API_KEY]      # 필요한 환경변수
      bins: [curl, jq]         # 필요한 CLI 도구
---

# 스킬 제목

## When to Use
- 어떤 상황에서 이 스킬을 사용하는지 (자연어)
- 트리거 키워드 나열

## Authentication (필요시)
인증 방법 설명 + 명령어

## Commands
실제 실행할 명령어들 (bash 코드블록)

## Response Format
응답 형식 가이드라인
```

## 핵심 원칙

1. **코드가 아니라 지침서** — AI가 읽고 판단해서 실행
2. **`When to Use`가 가장 중요** — AI가 이 섹션으로 스킬 사용 여부를 판단
3. **Commands는 구체적으로** — curl 명령어, jq 파이프라인 등을 정확히 작성
4. **환경변수로 비밀값 관리** — SKILL.md에 토큰을 하드코딩하지 말 것

## 새 스킬 추가 후

```bash
# 이 레포를 pull 하거나 파일을 추가하면 자동 반영
# hot reload가 안 되면 gateway 재시작
openclaw gateway
```
