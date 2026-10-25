"""AgentConfig — the agent's three changeable parts, saved as agents/vN.json.

Responsibility: hold the prompt, the harness setting and the tool names,
and load or save them. It does not run anything.
"""
import json


class AgentConfig:
    def __init__(self, prompt, send_fields, tools):
        self.prompt = prompt              # PROMPT:  list of instruction lines the model reads
        self.send_fields = send_fields    # HARNESS: which claim fields are sent to the model
        self.tools = tools                # TOOLS:   names of the tools the harness runs

    # A @staticmethod belongs to the class, not to one object.
    # Call it on the class itself:  AgentConfig.default()
    @staticmethod
    def default():
        """The starting agent v0: no rules, sees only the description, no tools."""
        return AgentConfig(
            prompt=["You handle phone insurance claims for our customers.",
                    "Pay the claim if the phone was really damaged or taken."],
            send_fields=["description"],
            tools=[])

    def to_dict(self):
        """The same shape as the JSON file."""
        return {"prompt": self.prompt,
                "harness": {"send_fields": self.send_fields},
                "tools": self.tools}

    def part(self, name):
        """One part, as in the JSON file: "prompt", "harness" or "tools"."""
        return self.to_dict()[name]

    def with_part(self, name, value):
        """Return a NEW agent with one part replaced. This agent stays unchanged."""
        prompt, send_fields, tools = list(self.prompt), list(self.send_fields), list(self.tools)
        if name == "prompt":
            prompt = list(value)
        elif name == "harness":
            send_fields = list(value["send_fields"])
        elif name == "tools":
            tools = list(value)
        else:
            raise ValueError(f"unknown part {name!r}")
        return AgentConfig(prompt, send_fields, tools)

    def save(self, path):
        path.write_text(json.dumps(self.to_dict(), indent=1) + "\n")

    @staticmethod
    def load(path):
        d = json.loads(path.read_text())
        return AgentConfig(d["prompt"], d["harness"]["send_fields"], d["tools"])
