import unittest

from gate import SafetyGate
from tests.helpers import claim

A, D = "APPROVE", "DENY"


class TestTask2SafetyGate(unittest.TestCase):
    gate = SafetyGate()
    claims = [claim("C1", A), claim("C2", A), claim("C3", D)]

    def test_rejects_new_invalid_payout_even_if_score_rises(self):
        # score rises from 1/3 to 2/3, but C3 (truth DENY) is newly approved
        decision = self.gate.decide([D, D, D], [A, A, A], self.claims)
        self.assertFalse(decision.keep)
        self.assertIn("C3", decision.reason)

    def test_keeps_a_safe_improvement(self):
        decision = self.gate.decide([A, D, D], [A, A, D], self.claims)
        self.assertTrue(decision.keep)

    def test_rejects_when_score_does_not_rise(self):
        decision = self.gate.decide([A, A, D], [A, D, D], self.claims)
        self.assertFalse(decision.keep)

    def test_an_old_invalid_approval_is_not_new(self):
        # C3 was already approved before, so it is not NEW: decide on the score (1/3 -> 2/3)
        decision = self.gate.decide([D, A, A], [A, A, A], self.claims)
        self.assertTrue(decision.keep)
