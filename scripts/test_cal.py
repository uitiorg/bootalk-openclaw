"""scripts/cal.py 의 순수 함수 unit test."""
import unittest
from cal import leave_type_label


class TestLeaveTypeLabel(unittest.TestCase):
    def test_full_day_single(self):
        self.assertEqual(leave_type_label(days=1, half_am=False, half_pm=False), "연차")

    def test_full_day_multi(self):
        self.assertEqual(leave_type_label(days=3, half_am=False, half_pm=False), "연차 3일")

    def test_half_am(self):
        self.assertEqual(leave_type_label(days=1, half_am=True, half_pm=False), "오전반차")

    def test_half_pm(self):
        self.assertEqual(leave_type_label(days=1, half_am=False, half_pm=True), "오후반차")


from datetime import date as _date
from cal import format_email_subject


class TestFormatEmailSubject(unittest.TestCase):
    def test_half_am(self):
        result = format_email_subject("주우철", "오전반차", _date(2026, 5, 1))
        self.assertEqual(result, "[오전반차] 26.05.01 주우철")

    def test_half_pm(self):
        result = format_email_subject("정정일", "오후반차", _date(2026, 4, 28))
        self.assertEqual(result, "[오후반차] 26.04.28 정정일")

    def test_full_day_single(self):
        result = format_email_subject("이현석", "연차", _date(2026, 6, 15))
        self.assertEqual(result, "[연차] 26.06.15 이현석")

    def test_full_day_multi(self):
        result = format_email_subject("배지은", "연차 3일", _date(2026, 7, 1))
        self.assertEqual(result, "[연차 3일] 26.07.01 배지은")


from datetime import datetime as _datetime
from cal import format_email_body, KST


class TestFormatEmailBody(unittest.TestCase):
    def setUp(self):
        # 신청일시를 결정적으로 만들기 위해 고정값 주입
        self.now = KST.localize(_datetime(2026, 4, 27, 14, 32))

    def test_half_am(self):
        body = format_email_body(
            name="주우철",
            leave_type="오전반차",
            start_date=_date(2026, 5, 1),
            days=1,
            time_range="09:30–13:30",
            now=self.now,
        )
        self.assertIn("신청자: 주우철", body)
        self.assertIn("일자: 2026-05-01", body)
        self.assertIn("종류: 오전반차 (09:30–13:30)", body)
        self.assertIn("신청일시: 2026-04-27 14:32 KST", body)
        self.assertIn("신청 경로: 부톡봇 (Slack)", body)
        self.assertNotIn("CDO", body)  # 직책 표기 금지

    def test_full_day_multi_includes_end_date(self):
        body = format_email_body(
            name="정정일",
            leave_type="연차 3일",
            start_date=_date(2026, 5, 1),
            days=3,
            time_range="종일",
            now=self.now,
        )
        # 다중일은 "일자: 시작 ~ 종료" 형식
        self.assertIn("2026-05-01", body)
        self.assertIn("2026-05-03", body)
        self.assertIn("~", body)

    def test_full_day_single_no_range(self):
        body = format_email_body(
            name="이현석",
            leave_type="연차",
            start_date=_date(2026, 6, 1),
            days=1,
            time_range="종일",
            now=self.now,
        )
        # 1일은 ~ 표기 없음
        self.assertNotIn("~", body)


from cal import resolve_reply_to


class TestResolveReplyTo(unittest.TestCase):
    def test_known_name(self):
        # 매핑이 있으면 본인 이메일 반환
        self.assertEqual(resolve_reply_to("주우철"), "cdo.bootalk@gmail.com")
        self.assertEqual(resolve_reply_to("이훈구"), "ceo.uiti@gmail.com")
        self.assertEqual(resolve_reply_to("이현석"), "leehs.uiti@gmail.com")
        self.assertEqual(resolve_reply_to("정정일"), "jji.bootalk@gmail.com")
        self.assertEqual(resolve_reply_to("배지은"), "bje.uiti@gmail.com")
        self.assertEqual(resolve_reply_to("전유진"), "cyj.uiti@gmail.com")

    def test_unknown_name_returns_none(self):
        # 매핑에 없으면 None — Reply-To 헤더 자체를 생략하기 위함
        self.assertIsNone(resolve_reply_to("홍길동"))
        self.assertIsNone(resolve_reply_to(""))


if __name__ == "__main__":
    unittest.main()
