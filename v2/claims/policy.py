"""Policy — the three company rules.

Responsibility: hold the rules. The meta-agent reads them; the agent knows only its own prompt.
"""


class Policy:
    RULES = [
        "Rule 1: covered causes are damage and theft. A lost phone is not covered.",
        "Rule 2: a theft claim needs a police report.",
        "Rule 3: the claim must be reported at most 30 days after the incident.",
    ]

    def text(self):
        return "\n".join(self.RULES)
