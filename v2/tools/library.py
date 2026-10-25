"""ToolLibrary — the tools the meta-agent may switch on.

Responsibility: find a tool by its name, and list all tools for the meta-agent.
The order matters: it is the order in the meta-agent's prompt.
"""
from tools.currency_convert import CurrencyConvert
from tools.days_between import DaysBetween


class ToolLibrary:
    def __init__(self, tools=None):
        # PoliceReportCheck (Task 1) is not in the default library: adding it changes the
        # meta-agent's prompt, and the recorded replay only knows the original prompt.
        tools = tools if tools is not None else [DaysBetween(), CurrencyConvert()]
        self.tools = {t.name: t for t in tools}

    def names(self):
        return list(self.tools)

    def get(self, name):
        return self.tools[name]

    def has(self, name):
        return name in self.tools

    def menu(self):
        """The list the meta-agent reads: one line per tool."""
        return "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())
