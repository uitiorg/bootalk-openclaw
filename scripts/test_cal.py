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


if __name__ == "__main__":
    unittest.main()
