from tools.tool import Tool


class DaysBetween(Tool):
    """Exact date arithmetic, which a small model often gets wrong."""
    name = "days_between"
    description = "exact number of days from the incident to the report"

    def run(self, claim):
        return f"days_between(incident_date, reported_date) = {claim.days_to_report()}"
