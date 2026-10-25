"""Claim — one insurance claim, as stored in data/claims.json.

Responsibility: hold the facts of one claim and its correct answer.
"""
import datetime as dt
from dataclasses import dataclass

# The claim fields an agent could be shown. The answer (truth, why) is never shown.
FIELDS = ["description", "cause", "incident_date", "reported_date", "police_report"]


# @dataclass writes __init__ for us: Claim(id="C1", name="Sara", ...) sets every field below.
@dataclass
class Claim:
    id: str
    name: str
    set: str             # "practice" (used by the loop) or "exam" (kept aside)
    description: str
    cause: str
    incident_date: str
    reported_date: str
    police_report: str
    truth: str           # the correct answer: APPROVE or DENY
    why: str             # why that answer is correct, e.g. "ok", "lost", "late"

    def field(self, name):
        """The value of one claim field, e.g. claim.field("cause")."""
        return getattr(self, name)

    def record(self):
        """All five fields as a dict: what a reviewer sees, never the answer."""
        return {f: self.field(f) for f in FIELDS}

    def days_to_report(self):
        """Days from the incident to the report."""
        incident = dt.date.fromisoformat(self.incident_date)
        reported = dt.date.fromisoformat(self.reported_date)
        return (reported - incident).days
