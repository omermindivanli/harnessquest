"""HarnessQuest: a gamified way to learn harness engineering for AI agents."""

__version__ = "1.1.0"

__all__ = ["HarnessRunner", "get_provider", "ExecutionSandbox", "ContextEngine", "__version__"]


def __getattr__(name):
    # Lazy imports keep `import harnessquest` fast and free of heavy dependencies (litellm).
    if name in ("HarnessRunner", "get_provider", "ExecutionSandbox", "ContextEngine"):
        from harnessquest import core

        return getattr(core, name)
    raise AttributeError(f"module 'harnessquest' has no attribute {name!r}")
