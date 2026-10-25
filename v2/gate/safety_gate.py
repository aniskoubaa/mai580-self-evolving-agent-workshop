"""TASK 2 — a stricter gate.

ScoreGate keeps a candidate whenever its score goes up. But a candidate can fix two
claims and, at the same time, start approving a claim the policy says to DENY. That
is a payout the company should never make.

Write SafetyGate so that it:
  1. REJECTS the candidate if it approves any claim that
       - the current agent did NOT approve, and
       - whose correct answer (claim.truth) is DENY.
     Reason, e.g.: "it newly approves C4, which should be denied"
  2. Otherwise decides exactly like ScoreGate.

Check your work:  python3 -m unittest tests.test_task2_gate
Use it in the loop:  python3 main.py --gate safety

Discuss: which useful changes could this gate reject? Is avoiding invalid payouts
enough, or should wrong denials count too?
"""
from gate.gate import AcceptanceGate, Decision
from gate.score_gate import ScoreGate


class SafetyGate(AcceptanceGate):
    def decide(self, old_answers, new_answers, claims):
        # TODO: find the claims the candidate newly approves although truth is DENY.
        # Hint: loop over zip(claims, old_answers, new_answers).
        raise NotImplementedError("TASK 2: write SafetyGate.decide")
