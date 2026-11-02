"""Level 7 reference: a verification gate between "the model says done" and "done"."""


def verify(output):
    return bool(output and output.strip()) and "[TASK_COMPLETE]" in output
