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

# 오전 반차 (09:30~13:30)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --half-am

# 오후 반차 (13:30~18:30)
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --half-pm
```

### 자동 이메일 알림

연차/반차 등록 시 자동으로 `holiday.uiti@gmail.com`에 알림 메일 1통이 발송된다.

- 발신: `<신청자 이름> <cdo.bootalk@gmail.com>` (display name = 신청자 본인)
- 제목: `[오전반차] 26.05.01 주우철` 형식
- 본문: 신청자, 일자, 종류, 신청일시, 신청 경로 5줄
- Reply-To: 신청자 본인 이메일 (HR이 답장 시 신청자에게 직접 도달)

이메일 발송 실패는 stderr 경고만 출력하고 캘린더 등록은 유지된다 — 사용자에게 발송 실패 안내 후 수동 재시도 가능.

이메일 발송을 끄려면 `--no-email` 플래그 추가 (테스트/디버그 용도):

```bash
python3 /Users/juucheol/Bootalk/bootalk-openclaw/scripts/cal.py leave "이름" "YYYY-MM-DD" --no-email
```

제3자가 다른 사람의 연차를 등록할 때(예: "정정일 5월 5일 오후 반차 등록해줘")는 발화자가 아니라 **신청 대상자(정정일)** 기준으로 메일 발송.

---

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

> 전체 팀원 ID 및 채널 목록: `/Users/juucheol/Bootalk/bootalk-openclaw/team/channels.md`

| Slack 계정 | 실명 | Slack ID |
|------------|------|----------|
| cdo.bootalk | 주우철 | U0APRS4J70B |
| ceo.uiti | 이훈구 | U0AQ1RUPF4L |
| leehs.uiti | 이현석 | U0AQ1RWGKPW |
| bje.uiti | 배지은 | U0APW6HMNR4 |
| jji.bootalk | 정정일 | U0APRSH0SNP |
| cyj.uiti | 전유진 | U0APGQN76CF |

날짜 미지정 시 반드시 확인 후 등록.
제3자 연차 등록 시("배지은 연차 등록해줘") 이름을 그대로 사용.

## Response Format

결과를 한국어로.

### 🚨 leave 명령 응답 (CRITICAL — 절대 paraphrase 금지)

`cal.py leave` 명령은 항상 다음 두 가지 부수 효과를 일으킨다:
1. "부톡 연차" 캘린더에 이벤트 생성
2. `holiday.uiti@gmail.com`에 알림 메일 발송

따라서 응답은 **반드시 두 사실 모두를 신청자에게 보고**해야 한다. 캘린더 등록만 보고하고 이메일 발송을 누락하는 것은 명백한 결함.

#### cal.py stdout 예시 (실제 출력)

```
✅ 연차 등록: [오전반차] 주우철
   날짜: 2026-05-13T09:30:00+09:00
   링크: https://www.google.com/calendar/event?eid=...
📧 이메일 발송 완료: holiday.uiti@gmail.com
```

#### Slack 응답으로 변환할 때 — 다음 두 줄을 반드시 모두 포함:

```
✅ [오전반차] 주우철 — 5월 13일 등록 완료 (<URL|캘린더>)
📧 holiday.uiti@gmail.com 알림 완료
```

(첫 줄은 표현 자유. 둘째 줄 `📧 ...` 는 거의 그대로 유지.)

#### ❌ 잘못된 응답 (이메일 라인 누락)

```
5월 13일 주우철님의 오전 반차를 부톡 연차 캘린더에 등록했어요.
캘린더에서 보기
```

위 응답은 등록만 보고하고 메일 발송 사실을 숨겼으므로 잘못됨. 신청자가 HR에 메일 도달 여부를 확인할 수 없게 됨.

#### 이메일 발송 실패 시

cal.py stderr에 `⚠️ 이메일 발송 실패 (캘린더는 등록됨): ...` 라인이 있으면, 응답에 명시:

```
✅ [연차] 주우철 — 5월 14일 등록 완료
⚠️ 이메일 발송 실패 — 사유: <에러 요약>. 수동 재시도 필요.
```

### 기타 명령 응답

- `agenda` 조회: 날짜별 목록 (cal.py 출력 그대로 정리)
- `leaves` 조회: 날짜별 목록 (cal.py 출력 그대로)
- `add` 등록: "✅ <제목> — <시간> 등록 완료" + 캘린더 링크
- 오류 시: 원인과 해결 방법
