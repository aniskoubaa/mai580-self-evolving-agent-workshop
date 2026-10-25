import unittest

from loop.held_out_exam import ExamAlreadyOpened, HeldOutExam
from tests.helpers import claim


class AlwaysApprove:
    """A fake agent: no model needed for this test."""
    def run(self, claims):
        return ["APPROVE"] * len(claims)


class TestTask3HeldOutExam(unittest.TestCase):
    def test_first_opening_returns_answers(self):
        exam = HeldOutExam([claim("E1", "APPROVE"), claim("E2", "DENY")])
        results = exam.take({"v0": AlwaysApprove(), "v3": AlwaysApprove()})
        self.assertEqual(results, {"v0": ["APPROVE", "APPROVE"], "v3": ["APPROVE", "APPROVE"]})

    def test_second_opening_is_refused(self):
        exam = HeldOutExam([claim("E1", "APPROVE")])
        exam.take({"v3": AlwaysApprove()})
        with self.assertRaises(ExamAlreadyOpened):
            exam.take({"v4": AlwaysApprove()})
