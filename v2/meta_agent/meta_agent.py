"""MetaAgent — the bigger model that diagnoses mistakes and proposes ONE change.

Responsibility: write the meta-agent's prompt, ask the bigger model, and check its reply.

You only need to READ propose(). build_prompt() is one long text, and
parse_reply() checks that the reply is valid JSON naming a real part.
"""
import json

from claims import FIELDS
from meta_agent.proposal import PART_FOR, Proposal

META_MODEL = "gemini-2.5-flash"   # the bigger model: diagnoses and proposes


class MetaAgent:
    def __init__(self, llm, harness, policy, tool_library):
        self.llm = llm
        self.harness = harness
        self.policy = policy
        self.tool_library = tool_library

    def propose(self, config, claims, answers, undone):
        """Look at the mistakes on these claims and propose one change."""
        text = self.build_prompt(config, claims, answers, undone)
        reply = self.llm.ask(META_MODEL, text, temperature=0.3)
        return self.parse_reply(reply, config)

    def build_prompt(self, config, claims, answers, undone):
        mistakes = "\n".join(
            f"- {json.dumps(c.record())}\n"
            f"  agent said {a}, correct is {c.truth} ({c.why})"
            for c, a in zip(claims, answers) if a != c.truth)
        example = self.harness.build_request(config, claims[0])
        return f"""You improve a small AI agent that approves or denies phone insurance claims.
Company policy:
{self.policy.text()}
The agent has three parts you may change:
- "prompt": the instruction lines the agent reads.
- "harness": {{"send_fields": [...]}} which claim fields the harness sends to the agent.
  Possible fields: {FIELDS}. The agent sees nothing else.
- "tools": tools the harness runs and whose results it shows to the agent. Library:
{self.tool_library.menu()}
Current agent:
{json.dumps(config.to_dict())}
The agent receives this text for a claim (example):
---
{example}
---
Its mistakes on the practice claims (full records, the agent saw only the fields above):
{mistakes}
Changes already tried and undone (do not repeat): {undone or 'none'}

Diagnose the main cause of the mistakes as ONE kind, and fix the part that kind names:
- knowledge: the prompt does not state a rule the agent needs     -> change the "prompt"
- information: a claim field the agent needs is not sent to it    -> change the "harness"
- skill: the agent has every field it needs but counts or calculates wrongly -> change the "tools"
Change exactly ONE part. Keep the prompt at most 6 short lines. Never name a claim in the prompt.
Reply with JSON only:
{{"diagnosis": "<two short, plain sentences>", "kind": "knowledge|information|skill",
  "new_value": <the new value of that part only>}}"""

    def parse_reply(self, reply, config):
        """Turn the model's JSON into a Proposal. Raise an error if it is invalid."""
        d = json.loads(reply[reply.find("{"): reply.rfind("}") + 1])
        part, new = PART_FOR[d["kind"]], d["new_value"]
        if part == "prompt":
            assert isinstance(new, list) and all(isinstance(s, str) for s in new)
        elif part == "harness":
            new = new if isinstance(new, dict) else {"send_fields": new}
            assert all(f in FIELDS for f in new["send_fields"])
            new = {"send_fields": [f for f in FIELDS if f in new["send_fields"]]}
        else:
            new = new if isinstance(new, list) else [new]
            new = [t["name"] if isinstance(t, dict) else t for t in new]
            assert all(self.tool_library.has(t) for t in new)
        return Proposal(d["diagnosis"], d["kind"], part, config.with_part(part, new))
