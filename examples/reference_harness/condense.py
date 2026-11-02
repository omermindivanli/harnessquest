"""Level 15 reference: condense old turns, keep the goal and the latest failures."""


def condense(messages, keep_last=2):
    if len(messages) <= keep_last + 2:
        return list(messages)
    head, tail = messages[0], messages[-keep_last:]
    middle = messages[1:-keep_last]
    summary = {"role": "system", "content": f"[summary of {len(middle)} earlier turns omitted]"}
    return [head, summary] + tail
