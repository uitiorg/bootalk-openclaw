# 연차 신청 시 holiday.uiti@gmail.com 이메일 발송

> 상태: `scripts/cal.py`의 직접 실행형 기능. 상주 Slack 봇이 자동으로 연차를 등록하는 현재 runtime은 없습니다.
> 마지막 문서 검토: 2026-08-10 KST.

## 동작 범위

`cal.py leave`가 정상적으로 Calendar 이벤트를 만든 뒤, 인증이 준비되어 있고 `--no-email`이 없으면 HR 주소로 Gmail 알림을 보냅니다. Calendar와 Gmail credential이 없거나 만료된 환경에서는 실행 전 준비가 필요합니다.

현재 실행 주체는 다음 중 하나입니다.

- 사용자가 Codex task에서 명시적으로 요청한 직접 실행
- 운영자가 검토한 local CLI 실행
- 별도로 승인·구현된 Codex automation

Slack에 메시지가 들어왔다는 사실만으로 이 명령이 실행되지는 않습니다.

## CLI 사용법

```bash
python3 scripts/cal.py leave "주우철" "YYYY-MM-DD" --remaining "사용 후 잔여일"
python3 scripts/cal.py leave "주우철" "YYYY-MM-DD" --half-am --remaining "사용 후 잔여일"
python3 scripts/cal.py leave "주우철" "YYYY-MM-DD" --half-pm --remaining "사용 후 잔여일"
python3 scripts/cal.py leave "주우철" "YYYY-MM-DD" --no-email --remaining "사용 후 잔여일"
```

반차 시간은 오전 09:30~13:30, 오후 13:30~18:30입니다. 실행 전 대상자, 날짜, 기간, 잔여 연차를 확인합니다.

## 성공과 부분 성공

정상적인 보고에는 아래 사실을 분리해 포함합니다.

```text
Calendar: 등록 완료 (event link)
Gmail: holiday.uiti@gmail.com 발송 완료
잔여 연차: 사용 후 값
```

Calendar 등록이 실패하면 Gmail을 보내지 않습니다. Calendar 등록 후 Gmail만 실패할 수 있으므로 두 결과를 하나로 뭉뚱그리지 않습니다.

## 테스트와 인증

- 메일 side effect가 필요 없는 테스트에는 `--no-email`을 사용합니다.
- `scripts/token.json`과 `scripts/credentials.json`의 내용을 출력하거나 커밋하지 않습니다.
- OAuth 만료 시 인증 파일을 임의로 삭제하기 전에 백업·재인증 절차와 대상 계정을 확인합니다.
- 실제 Gmail 발송을 테스트할 때는 수신자, 제목, 발신자 표시, 중복 발송 여부를 확인합니다.

## 관련 파일

- 스킬 지침: [`skills/bootalk-calendar/SKILL.md`](../skills/bootalk-calendar/SKILL.md)
- CLI: [`scripts/cal.py`](../scripts/cal.py)
- 과거 설계: [`docs/superpowers/specs/2026-04-27-leave-email-notification-design.md`](superpowers/specs/2026-04-27-leave-email-notification-design.md)
- 과거 구현 계획: [`docs/superpowers/plans/2026-04-27-leave-email-notification.md`](superpowers/plans/2026-04-27-leave-email-notification.md)
