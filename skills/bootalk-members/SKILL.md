---
name: bootalk_members
description: 회원 검색, 중개사 조회, 가입자 수, 사용자 정보 조회. btalk2.1_backend API 사용.
metadata:
  openclaw:
    primaryEnv: BOOTALK_API_KEY
    requires:
      env: [BOOTALK_API_KEY, BOOTALK_API_URL]
      bins: [curl, jq]
---

# 회원/중개사 조회

## When to Use
- 사용자가 회원, 중개사, 가입자 정보를 묻을 때
- "중개사 조회", "회원 검색", "오늘 가입자 수" 등

## Authentication

bootalk-properties 스킬과 동일한 서비스 토큰 발급 방식 사용:

```bash
SERVICE_TOKEN=$(curl -s -X POST "$BOOTALK_API_URL/internal/auth/service-token" \
  -H "X-Internal-Api-Key: $BOOTALK_API_KEY" \
  -H "Content-Type: application/json" | jq -r '.data.accessToken')
```

## Commands

### 회원 검색
```bash
curl -s "$BOOTALK_API_URL/api/members?keyword={검색어}" \
  -H "Authorization: Bearer $SERVICE_TOKEN" | jq
```

### 중개사 조회
```bash
curl -s "$BOOTALK_API_URL/api/agents?keyword={검색어}" \
  -H "Authorization: Bearer $SERVICE_TOKEN" | jq
```

## Response Format
- 개인정보는 마스킹 처리 (이름 가운데 글자 *, 전화번호 중간 4자리 ****)
- 결과를 한국어 표 형태로 정리
