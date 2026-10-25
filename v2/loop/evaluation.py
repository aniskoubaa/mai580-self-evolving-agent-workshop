"""Two helper functions: count right answers, and list the claims a change fixed."""


def score(answers, claims):
    """How many answers match the correct answer."""
    return sum(a == c.truth for a, c in zip(answers, claims))


def fixed_ids(claims, before, after):
    """IDs of the claims that were wrong BEFORE and are right AFTER, or "none".
    Swap before and after to get the claims a change broke."""
    ids = [c.id for c, b, a in zip(claims, before, after) if b != c.truth == a]
    return ids or "none"
