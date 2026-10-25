"""ClaimSet — all claims, split into practice and exam claims.

Responsibility: read data/claims.json once, and keep the two groups apart.
"""
import json

from claims.claim import Claim


class ClaimSet:
    def __init__(self, claims):
        self.all = claims
        self.practice = [c for c in claims if c.set == "practice"]  # the loop learns from these
        self.exam = [c for c in claims if c.set == "exam"]          # the loop never sees these

    @staticmethod
    def load(path):
        """Read the JSON file. Claim(**record) fills each Claim field from the dict keys."""
        return ClaimSet([Claim(**record) for record in json.loads(path.read_text())])
