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


if __name__ == "__main__":
    unittest.main()
