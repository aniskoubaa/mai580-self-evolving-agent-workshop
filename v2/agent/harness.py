"""Harness — the code around the model.

Responsibility: build the text the model reads for one claim, and turn the
model's reply into one answer. It never decides anything itself.
"""
from claims import FIELDS


class Harness:
    def __init__(self, tool_library):
        self.tool_library = tool_library

    def build_request(self, config, claim):
        """The exact text the model receives for this claim."""
        lines = list(config.prompt) + ["", "Claim:"]
        lines += [f"{f}: {claim.field(f)}" for f in FIELDS if f in config.send_fields]
        if config.tools:
            lines += ["", "Tool results:"]
            lines += [self.tool_library.get(name).run(claim) for name in config.tools]
        return "\n".join(lines + ["", "Answer with one word: APPROVE or DENY."])

    def parse_answer(self, reply):
        """APPROVE or DENY, whichever the model wrote last. "?" if neither."""
        reply = reply.upper()
        approve, deny = reply.rfind("APPROVE"), reply.rfind("DENY")
        if approve == deny == -1:
            return "?"
        return "APPROVE" if approve > deny else "DENY"
