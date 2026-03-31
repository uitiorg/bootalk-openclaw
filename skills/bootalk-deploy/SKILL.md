---
name: bootalk_deploy
description: Vercel 배포 상태를 확인하고 관리합니다.
metadata:
  openclaw:
    requires:
      bins: [vercel]
---

# 배포 상태 확인

## When to Use
- 사용자가 배포 상태, 디플로이, 최근 배포를 묻을 때
- "배포 상태 알려줘", "최근 배포", "롤백해줘" 등

## Commands

### 최근 배포 목록
```bash
vercel ls --limit 5
```

### 배포 상세 정보
```bash
vercel inspect {deployment-url}
```

### 배포 로그 확인
```bash
vercel logs {deployment-url}
```

## Response Format
- 배포 상태를 표로 정리 (URL, 상태, 시간, 커밋)
- 에러 시 로그 핵심 부분 발췌
