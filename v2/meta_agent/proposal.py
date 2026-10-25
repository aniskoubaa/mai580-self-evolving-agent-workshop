"""Proposal — what the meta-agent suggests.

Responsibility: carry the diagnosis, the kind of problem, the part to change,
and the candidate agent with that one part changed.
"""
from dataclasses import dataclass

from agent import AgentConfig

# Each kind of problem names the one part that fixes it.
PART_FOR = {"knowledge": "prompt",       # a rule is missing from the prompt
            "information": "harness",    # a field the agent needs is not sent
            "skill": "tools"}            # the agent calculates wrongly


@dataclass
class Proposal:
    diagnosis: str
    kind: str
    part: str
    candidate: AgentConfig
