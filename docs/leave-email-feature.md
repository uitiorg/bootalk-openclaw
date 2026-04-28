# 연차 신청 시 자동 이메일 알림

> 부톡봇으로 연차/반차를 등록하면 캘린더 등록과 동시에 HR 메일함으로 알림 메일 1통이 자동 발송됩니다.

**시작일:** 2026-04-28 · **상태:** 운영 중 · **수신자:** `holiday.uiti@gmail.com`

---

## 한 줄 요약

부톡봇 DM/채널에 `"내일 오전 반차"` 한 줄만 입력하면, 캘린더 등록 + HR 메일 발송이 자동으로 동시에 처리됩니다.

## 사용법 (Slack에서)

부톡봇과의 DM 또는 #dev / #공지사항 등 봇이 들어와 있는 채널에서 자연어로:

| 요청 | 등록되는 내용 |
|---|---|
| `내일 오전 반차` | 다음날 09:30~13:30 반차 |
| `5월 13일 오후 반차` | 5/13 13:30~18:30 반차 |
| `5월 14일 연차` | 5/14 종일 연차 |
| `5월 15일부터 3일 연차` | 5/15~5/17 종일 연차 (3일) |
| `정정일 5월 18일 오전 반차 등록해줘` | 정정일 명의로 5/18 오전 반차 (제3자 대리 등록) |

봇 응답 예시 (반드시 두 줄):

```
✅ [오전반차] 주우철 — 5월 13일 등록 완료 (캘린더에서 보기)
📧 holiday.uiti@gmail.com 알림 완료
```

## HR이 받게 되는 메일

```
보낸사람: 주우철 <cdo.bootalk@gmail.com>
받는사람: holiday.uiti@gmail.com
회신:    cdo.bootalk@gmail.com   (← 신청자 본인 이메일로 자동 매핑)
제목:    [오전반차] 26.05.13 주우철

신청자: 주우철
일자: 2026-05-13 (수)
종류: 오전반차 (09:30–13:30)
신청일시: 2026-05-12 14:32 KST
신청 경로: 부톡봇 (Slack)
```

### 보낸사람 표시의 의미

기술적 발신 계정은 `cdo.bootalk@gmail.com` 단일 계정이지만, **From 헤더의 표시 이름(display name)이 신청자 본인의 한국어 이름**이라 HR 받은편지함 리스트에는 "주우철"·"정정일" 같이 신청자 이름이 그대로 보입니다. HR이 "회신" 버튼을 누르면 `Reply-To`에 매핑된 본인 이메일로 자동 채워져서 신청자에게 바로 도달합니다.

이 방식의 트레이드오프는 [설계 문서 §"3가지 발송 방식 비교"](superpowers/specs/2026-04-27-leave-email-notification-design.md)에 정리되어 있습니다.

### 신청자 이름 ↔ 본인 이메일 매핑

| 한국어 이름 | Reply-To |
|---|---|
| 주우철 | `cdo.bootalk@gmail.com` |
| 이훈구 | `ceo.uiti@gmail.com` |
| 이현석 | `leehs.uiti@gmail.com` |
| 정정일 | `jji.bootalk@gmail.com` |
| 배지은 | `bje.uiti@gmail.com` |
| 전유진 | `cyj.uiti@gmail.com` |

매핑은 `scripts/cal.py`의 `TEAM_EMAILS` dict에 코드로 관리됩니다 (보안상 docs에는 미수록 — 위 표는 README/docs용 예시). 신규 입사자는 dict에 한 줄 추가하는 것으로 등록.

매핑에 없는 이름은 메일은 정상 발송되지만 `Reply-To` 헤더가 생략되며, 터미널 로그에 매핑 누락 경고가 출력됩니다.

## 제3자 대리 등록 동작

전유진이 부톡봇에게 "정정일 5월 18일 오후 반차 등록해줘"라고 입력해도:

- 메일 발신자 표시 이름: **정정일** (= 신청 대상자)
- Reply-To: 정정일 본인 이메일 (`jji.bootalk@gmail.com`)
- 본문 `신청자` 필드: **정정일**
- HR 입장에서 추적 주체는 일관되게 "정정일이 신청한 것"

발화자(전유진)는 별도로 표기되지 않습니다. HR 입장에서 누가 신청한 연차인지가 핵심 추적 정보이기 때문입니다.

## 안전장치

- **이메일 발송 실패 시 캘린더는 그대로 유지** — 메일 API 오류, 네트워크 문제 등이 발생해도 캘린더 등록은 롤백되지 않습니다. 봇 응답에 `⚠️ 이메일 발송 실패` 라인이 명시되며, 신청자가 수동 재시도하거나 HR에게 직접 통지하면 됩니다.
- **테스트용 이메일 끄기** — 디버그/테스트가 필요한 경우 CLI 직접 실행 시 `--no-email` 플래그로 메일 발송만 스킵 가능:
  ```bash
  python3 scripts/cal.py leave "주우철" "2026-05-13" --half-am --no-email
  ```
- **OAuth 토큰 만료** — 토큰이 만료되면 부톡봇 응답에 인증 에러가 표시됩니다. `scripts/token.json` 삭제 후 `cal.py agenda 1` 한 번 실행해서 브라우저 동의 갱신.

## 봇이 어떤 명령을 실행하는지

부톡봇은 자연어 요청을 받아 내부적으로 다음 CLI를 호출합니다:

```bash
python3 scripts/cal.py leave "<이름>" "<YYYY-MM-DD>" [일수|--half-am|--half-pm]
```

매뉴얼하게 같은 동작을 트리거하고 싶으면 위 명령을 직접 실행해도 됩니다.

## FAQ

**Q. HR로 가는 메일을 끄고 싶다.**
`scripts/cal.py`의 `RECIPIENT_EMAIL` 상수를 다른 주소로 바꾸거나 `--no-email` 플래그로 개별 호출에서 스킵.

**Q. 메일 발신 계정이 다른 사람의 Gmail로 보이는 게 부담스럽다.**
모든 메일은 기술적으로 `cdo.bootalk@gmail.com`이라는 단일 계정에서 발송됩니다. 표시 이름만 신청자별로 다르게 설정될 뿐, 다른 팀원의 메일함에 침입하지 않습니다.

**Q. Gmail이 "via cdo.bootalk@gmail.com" 같은 경고를 표시한다.**
Gmail 안티-피싱 기능 때문에 가끔 표시될 수 있으나 기능 동작에 영향 없음. SPF/DKIM 검증은 `cdo.bootalk@gmail.com`에 대해 정상 통과합니다.

**Q. 다른 회사 도메인 메일 (예: `@uiti.com`)로 발송하고 싶다.**
Google Workspace 도메인 마이그레이션 후 service account + domain-wide delegation 설정으로 가능. 현재는 모든 팀원이 개인 Gmail 계정을 쓰므로 미적용.

## 관련 문서

- 봇 스킬 정의: [`skills/bootalk-calendar/SKILL.md`](../skills/bootalk-calendar/SKILL.md)
- CLI 스크립트: [`scripts/cal.py`](../scripts/cal.py) (`notify_email`, `cmd_leave` 함수)
- 설계 문서: [`docs/superpowers/specs/2026-04-27-leave-email-notification-design.md`](superpowers/specs/2026-04-27-leave-email-notification-design.md)
- 구현 계획: [`docs/superpowers/plans/2026-04-27-leave-email-notification.md`](superpowers/plans/2026-04-27-leave-email-notification.md)
