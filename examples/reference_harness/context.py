"""Level 4 reference: keep conversation history inside a token budget."""


def _tokens(message):
    return len(str(message.get("content", ""))) // 4 + 1  # rough: ~4 chars per token


def trim_history(messages, max_tokens):
    """Drop the oldest messages until the history fits; always keep the newest one."""
    if sum(_tokens(m) for m in messages) <= max_tokens:
        return list(messages)
    out = list(messages)
    while len(out) > 1 and sum(_tokens(m) for m in out) > max_tokens:
        out.pop(0)
    return out
