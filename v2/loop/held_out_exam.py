"""TASK 3 — an exam you can only open once.

The loop improved the agent on the practice claims, so the practice score is a
development score. The exam claims check the result. But if you look at the exam
score, change the agent, and look again, the exam claims have guided your edit:
they are now development evidence too. This is leakage.

Write HeldOutExam so that the exam can be taken ONCE:
  - take(agents) receives a dict {name: Agent}, e.g. {"v0": a0, "v3": a3}, and
    returns {name: list of answers}, one answer per exam claim.
  - A second call to take() raises ExamAlreadyOpened, whatever agents it receives.

Check your work:  python3 -m unittest tests.test_task3_exam
"""


class ExamAlreadyOpened(Exception):
    """Raised when someone tries to use the exam claims a second time."""


class HeldOutExam:
    def __init__(self, claims):
        self.claims = claims
        self.opened = False

    def take(self, agents):
        # TODO: raise ExamAlreadyOpened if the exam was already opened,
        # otherwise mark it opened and return {name: agent.run(self.claims)}.
        raise NotImplementedError("TASK 3: write HeldOutExam.take")
