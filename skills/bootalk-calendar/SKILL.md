---
name: bootalk_calendar
description: 부톡 팀 구글 캘린더 일정 추가/조회. "일정 추가해줘", "캘린더에 올려줘", "오늘 일정 뭐야", "X시에 Y 잡아줘" 등.
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# 부톡 팀 캘린더 관리

캘린더: **부톡 팀 캘린더** (Google Calendar 공유 캘린더, 팀원 6명 편집 가능)

스크립트 위치: `/Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py`

## 권한 안내

- `token.json` / `credentials.json`은 `scripts/` 폴더에 로컬 저장 (git 제외)
- 봇이 실행되는 머신에 이미 존재 → 추가 설정 불필요
- refresh_token 포함이라 만료 없이 자동 갱신됨

## Commands

### 일정 조회

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda
```

향후 N일:
```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda 14
```

### 일정 추가

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "제목" "YYYY-MM-DD HH:MM" [분]
```

예시:
```bash
# 오늘 15시, 1시간
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "주간 회의" "2026-04-02 15:00" 60

# 종일 이벤트
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "배포일" "2026-04-10" --allday
```

## 사용자 요청 해석

- "오늘 3시에 X" → 오늘 날짜 + 15:00, 기본 60분
- "내일 오전 10시에 Y 30분" → 내일 날짜 + 10:00, 30분
- "X 잡아줘" / "캘린더에 X 추가해줘" → add 명령
- "오늘/이번 주 일정" → agenda 명령

날짜를 명시하지 않으면 오늘 날짜로, 시간을 명시하지 않으면 사용자에게 확인 후 추가.

## Response Format

결과를 한국어로:
- 추가 성공 시: 제목, 시작 시간, 캘린더 링크
- 조회 시: 날짜별 일정 목록
- 오류 시: 원인과 해결 방법
