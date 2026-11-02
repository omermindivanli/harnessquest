"""Level 16 reference: detect prompt injection in untrusted text (tool output, files, web pages)."""

import re

PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) instructions",
    r"disregard (the )?(system|previous) (prompt|instructions)",
    r"reveal (the |your )?system prompt",
    r"you are now (in )?(developer|dan) mode",
]


def scan(text):
    """Return the list of injection patterns found (empty list means clean)."""
    return [p for p in PATTERNS if re.search(p, text, re.IGNORECASE)]
