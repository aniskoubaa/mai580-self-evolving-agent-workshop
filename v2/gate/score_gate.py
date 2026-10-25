"""ScoreGate — the gate used in class: keep the candidate if MORE claims are right."""
from gate.gate import AcceptanceGate, Decision
from loop.evaluation import score


class ScoreGate(AcceptanceGate):
    """It does not look at WHICH claims changed, so it can accept a dangerous trade."""

    def decide(self, old_answers, new_answers, claims):
        old, new, n = score(old_answers, claims), score(new_answers, claims), len(claims)
        if new > old:
            return Decision(True, f"{new}/{n} is better than {old}/{n}")
        return Decision(False, f"{new}/{n} is not better than {old}/{n}")
