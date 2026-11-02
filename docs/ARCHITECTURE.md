# HarnessQuest Architecture Guide

HarnessQuest separates agent reasoning from execution infrastructure into four distinct pillars:
1. **Context Isolation & Compression** (`core/context.py`)
2. **State & Loop Guardrails** (`core/runner.py`)
3. **Execution Sandboxing** (`core/sandbox.py`)
4. **Gamification & Evaluation** (`gamification/xp.py` & `eval/judge.py`)
