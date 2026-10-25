"""Tool — the parent class of every tool.

Responsibility: define what every tool must have: a name, a description, and run(claim).
A new tool inherits from Tool and writes its own run().
"""


class Tool:
    name = "tool"                 # the name the agent configuration uses
    description = "what it does"  # what the meta-agent reads when it chooses tools

    def run(self, claim):
        """Return one line of text that the harness adds to the model's input."""
        raise NotImplementedError("Each tool must define run(claim).")
