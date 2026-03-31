---
name: bootalk_properties
description: 매물 현황, 아파트 시세, 매매가, 전세가, 거래량, 부동산 통계, 지역별 매물 수를 조회합니다.
metadata:
  openclaw:
    primaryEnv: BOOTALK_API_KEY
    requires:
      env: [BOOTALK_API_KEY, BOOTALK_API_URL]
      bins: [curl, jq]
---

# 부톡 매물 조회

## When to Use
- 사용자가 매물, 아파트, 부동산, 시세, 거래량을 질문할 때
- 특정 지역(구, 동)의 매물 현황을 묻을 때
- 중개사 매물 정보를 조회할 때

## Authentication

모든 API 호출 전에 서비스 토큰을 먼저 발급받는다:

```bash
SERVICE_TOKEN=$(curl -s -X POST "$BOOTALK_API_URL/internal/auth/service-token" \
  -H "X-Internal-Api-Key: $BOOTALK_API_KEY" \
  -H "Content-Type: application/json" | jq -r '.data.accessToken')
```

이후 모든 요청에 이 토큰을 사용한다:

```bash
curl -s "$BOOTALK_API_URL/{endpoint}" \
  -H "Authorization: Bearer $SERVICE_TOKEN" | jq
```

## Commands

### 매물 통계 조회
```bash
curl -s "$BOOTALK_API_URL/api/properties/stats?gu={지역명}" \
  -H "Authorization: Bearer $SERVICE_TOKEN" | jq
```

### 아파트 상세 조회
```bash
curl -s "$BOOTALK_API_URL/api/apt/{apt_id}" \
  -H "Authorization: Bearer $SERVICE_TOKEN" | jq
```

### 중개사 매물 목록
```bash
curl -s "$BOOTALK_API_URL/api/agent/properties?agentId={agent_id}" \
  -H "Authorization: Bearer $SERVICE_TOKEN" | jq
```

## Response Format
- 결과를 한국어로 정리하여 표 형태로 응답한다
- 숫자는 천 단위 구분자를 사용한다 (예: 1,243건)
- 가격은 억/만 단위로 표시한다 (예: 18.2억)
