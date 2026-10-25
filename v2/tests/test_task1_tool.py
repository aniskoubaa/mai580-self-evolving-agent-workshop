import unittest

from tests.helpers import claim
from tools import PoliceReportCheck


class TestTask1PoliceReportCheck(unittest.TestCase):
    tool = PoliceReportCheck()

    def test_theft_with_report(self):
        c = claim("T1", "APPROVE", cause="theft", police_report="yes")
        self.assertEqual(self.tool.run(c), "police_report_check: report present")

    def test_theft_without_report(self):
        c = claim("T2", "DENY", cause="theft", police_report="no")
        self.assertEqual(self.tool.run(c), "police_report_check: report MISSING")

    def test_damage_needs_no_report(self):
        c = claim("T3", "APPROVE", cause="damage")
        self.assertEqual(self.tool.run(c), "police_report_check: not required")
