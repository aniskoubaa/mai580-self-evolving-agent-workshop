"""Small claims built by hand, so each test shows exactly what it checks."""
from claims import Claim


def claim(id, truth, cause="damage", police_report="not needed"):
    return Claim(id=id, name="Test", set="practice", description="-", cause=cause,
                 incident_date="2026-09-01", reported_date="2026-09-03",
                 police_report=police_report, truth=truth,
                 why="ok" if truth == "APPROVE" else "test")
