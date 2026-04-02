---
name: bootalk_calendar
description: 부톡 팀 구글 캘린더 일정 추가/조회 및 연차 등록. "일정 추가해줘", "연차 등록해줘", "반차야", "이번 달 연차 현황", "오늘 일정 뭐야" 등.
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# 부톡 팀 캘린더 관리

## 캘린더 구조 (반드시 숙지)

| 캘린더 | 용도 | 명령 |
|--------|------|------|
| **부톡 팀 캘린더** | 회의, 데드라인, 팀 이벤트 | `agenda`, `add` |
| **부톡 연차** | 연차·반차 전용. 팀원 전체 편집 가능 | `leave`, `leaves` |

> ⚠️ **`agenda`는 연차 데이터를 포함하지 않는다.**
> 연차·반차·휴가 관련 조회는 반드시 `leaves`만 사용할 것.
> 두 캘린더는 완전히 별개이며, `agenda`로 연차를 찾으려 하면 항상 누락된다.

스크립트: `/Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py`

---

## 명령 라우팅 규칙 (최우선 적용)

```
요청에 연차 / 반차 / 휴가 / 쉬는 날 포함
  → 등록 요청  : leave
  → 조회 요청  : leaves   ← agenda 절대 사용 금지
  → 둘 다 포함 : leave 먼저 실행 후 leaves로 결과 확인

그 외 일정 (회의, 데드라인, 이벤트 등)
  → 조회 : agenda
  → 추가 : add
```

---

## Commands

### 일정 조회 (팀 캘린더)

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py agenda 14
```

### 일정 추가 (팀 캘린더)

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "주간 회의" "2026-04-07 10:00" 60
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py add "배포일" "2026-04-10" --allday
```

### 연차 등록 → 부톡 연차 캘린더

```bash
# 종일 연차
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD"

# 연속 연차 (N일)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" 3

# 오전 반차 (09:00~13:00)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --half-am

# 오후 반차 (13:00~18:00)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --half-pm
```

### 연차 현황 조회 → 반드시 leaves

```bash
# 이번 달 전체 연차 현황 (팀 전체)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leaves
```

---

## 사용자 요청 해석

### 연차 등록
| 요청 | 처리 |
|------|------|
| "나 X일 연차야" / "X일 연차 등록해줘" | `leave 이름 날짜` |
| "X일 반차" (오전/오후 불명확) | 오전/오후 확인 후 등록 |
| "오전 반차" | `leave 이름 날짜 --half-am` |
| "오후 반차" | `leave 이름 날짜 --half-pm` |
| "X일부터 Y일까지 연차" | 일수 계산 후 `leave 이름 시작일 N` |
| "A 오후 반차, B 연차 등록해줘" | leave 두 번 순차 실행 |

### 연차 조회
| 요청 | 처리 |
|------|------|
| "이번 달 연차 현황" | `leaves` |
| "누가 쉬어?" / "연차 있는 사람?" | `leaves` |
| "이번 달 휴가 정리해줘" | `leaves` |

### 이름 매핑 (Slack 발신자 → 실명)
- 주우철 (cdo.bootalk) → "주우철"
- 이훈구 (ceo.uiti) → "이훈구"
- 이현석 (leehs.uiti) → "이현석"
- 배지은 (bje.uiti) → "배지은"
- 정정일 (jji.bootalk) → "정정일"
- 전유진 (cyj.uiti) → "전유진"

날짜 미지정 시 반드시 확인 후 등록.
제3자 연차 등록 시("배지은 연차 등록해줘") 이름을 그대로 사용.

## Response Format

결과를 한국어로:
- 등록 성공: "✅ [연차] 이름 — YYYY-MM-DD 등록 완료"
- 현황 조회: 날짜별 목록 (leaves 결과 그대로)
- 오류 시: 원인과 해결 방법
