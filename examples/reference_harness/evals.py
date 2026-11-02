"""Level 17 reference: a tiny benchmark scorer."""


def score(results):
    """Fraction of passing cases; an empty suite scores 0."""
    return sum(1 for r in results if r) / len(results) if results else 0
