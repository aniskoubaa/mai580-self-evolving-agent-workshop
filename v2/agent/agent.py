"""Agent — a small model plus its configuration and its harness.

Responsibility: answer APPROVE or DENY for each claim.
"""

AGENT_MODEL = "gemini-2.5-flash-lite"   # the small model being improved


class Agent:
    def __init__(self, config, harness, llm):
        self.config = config
        self.harness = harness
        self.llm = llm

    def decide(self, claim):
        """APPROVE or DENY one claim."""
        text = self.harness.build_request(self.config, claim)
        return self.harness.parse_answer(self.llm.ask(AGENT_MODEL, text))

    def run(self, claims):
        """One answer per claim, in the same order."""
        return [self.decide(c) for c in claims]
