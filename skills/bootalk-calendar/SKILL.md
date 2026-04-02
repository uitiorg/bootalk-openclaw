---
name: bootalk_calendar
description: 부톡 팀 구글 캘린더 일정 추가/조회 및 연차 등록. "일정 추가해줘", "연차 등록해줘", "반차야", "이번 달 연차 현황", "오늘 일정 뭐야" 등.
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# 부톡 팀 캘린더 관리

캘린더 구성:
- **부톡 팀 캘린더** — 회의, 일정, 이벤트
- **부톡 연차** — 연차/반차 전용 (팀원 전체 편집 가능)

스크립트: `/Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py`

## 권한 안내

`token.json` / `credentials.json`이 스크립트와 같은 폴더에 로컬 저장됨 (git 제외).
봇이 실행되는 머신에 존재하며, refresh_token으로 자동 갱신.

---

## Commands

### 일정 조회

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda 14
```

### 일정 추가

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "주간 회의" "2026-04-07 10:00" 60
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "배포일" "2026-04-10" --allday
```

### 연차 등록 (부톡 연차 캘린더)

```bash
# 연차 (종일)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD"

# 연속 연차 (N일)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" 3

# 오전 반차 (09:00~13:00)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --half-am

# 오후 반차 (13:00~18:00)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --half-pm
```

### 이번 달 연차 현황

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leaves
```

---

## 사용자 요청 해석

### 연차 관련
| 요청 | 처리 방식 |
|------|-----------|
| "나 X일 연차야" / "X일 연차 등록해줘" | leave 명령, 이름은 Slack 발신자 |
| "X일 반차야" (시간 불명확) | 오전/오후 확인 후 등록 |
| "오전 반차" / "오후 반차" | --half-am / --half-pm |
| "X일부터 Y일까지 연차" | 일수 계산 후 N일 연차 |
| "이번 달 연차 현황" | leaves 명령 |

### 이름 매핑 (Slack 발신자 → 실명)
- 주우철 (cdo.bootalk) → "주우철"
- 이훈구 (ceo.uiti) → "이훈구"
- 이현석 (leehs.uiti) → "이현석"
- 배지은 (bje.uiti) → "배지은"
- 정정일 (jji.bootalk) → "정정일"
- 전유진 (cyj.uiti) → "전유진"

날짜 미지정 시 반드시 확인 후 등록. 이름은 Slack 발신자 기준으로 자동 적용.

## Response Format

결과를 한국어로:
- 연차 등록 성공: "✅ [연차] 이름 — YYYY-MM-DD 등록 완료"
- 현황 조회: 날짜별 목록
- 오류 시: 원인과 해결 방법
