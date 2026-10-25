"""TASK 1 — write your first tool.

Rule 2 says a theft claim needs a police report. Write a tool that states,
in one line, whether this claim still needs a police report.

    theft claim, police_report "yes"  -> "police_report_check: report present"
    theft claim, police_report "no"   -> "police_report_check: report MISSING"
    any other cause                   -> "police_report_check: not required"

Check your work:  python3 -m unittest tests.test_task1_tool
"""
from tools.tool import Tool


class PoliceReportCheck(Tool):
    name = "police_report_check"
    description = "says whether a theft claim has the police report it needs"

    def run(self, claim):
        # TODO: use claim.cause and claim.police_report
        raise NotImplementedError("TASK 1: write PoliceReportCheck.run")
