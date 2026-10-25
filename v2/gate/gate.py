"""AcceptanceGate — the parent class of every gate. Decision — what a gate returns.

Responsibility: compare the current agent's answers with the candidate's answers
on the same claims, and decide: keep the candidate, or undo the change.
"""
from dataclasses import dataclass


@dataclass
class Decision:
    keep: bool      # True: the candidate replaces the current agent
    reason: str     # one short sentence the console prints


class AcceptanceGate:
    def decide(self, old_answers, new_answers, claims):
        """Compare the current agent's answers with the candidate's on the same claims."""
        raise NotImplementedError("Each gate must define decide().")
