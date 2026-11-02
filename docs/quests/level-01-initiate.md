# Level 1: Initiate — Hello Harness

**Concept**: Agent Loop Fundamentals  
**XP Reward**: +100 XP  
**Badge**: 🌱 Initiate  
**Difficulty**: Beginner  
**Prerequisites**: None

---

## Theory

Every AI agent harness runs a loop: **observe → reason → act → repeat**. The harness provides the scaffolding: context injection, tool execution, turn limits, and completion detection. Understanding this loop is the foundation of all harness engineering.

```
while turn < max_turns:
    turn += 1
    messages = assemble_context(system_prompt, user_prompt, history)
    response = await llm.complete(messages)
    if "[TASK_COMPLETE]" in response:
        return success
    if "RUN: cmd" in response:
        result = sandbox.run_command(cmd)
    else:
        prompt_continue()
```

---

## Objective

Run your first agent task and observe the complete loop execution.

---

## Verification Prompt

> "List the files in the current directory and output [TASK_COMPLETE]"

**Expected Criteria**: Agent successfully lists files and includes `[TASK_COMPLETE]` marker.

---

## Step-by-Step Walkthrough

### 1. Start the Quest

```bash
harnessquest-quest 1 --provider ollama --model llama3.1:8b
```

### 2. Read the Theory

The quest will display the theory about agent loops. Read it carefully.

### 3. Run Verification

The quest automatically runs the verification prompt:
```
"List the files in the current directory and output [TASK_COMPLETE]"
```

### 4. Observe the Output

You'll see something like:
```
╭───────────────────────────────────────────────╮
│ HARNESSQUEST v1.1.0 - Gamified Harness Engine │
╰───────────────────────────────────────────────╯

🎯 Running verification...
Prompt: List the files in the current directory and output [TASK_COMPLETE]

✅ Task completed successfully!

🛡️ Quest Completion Stats & Rewards
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Metric         ┃ Value           ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Player Level   │ Level 1         │
│ XP Earned      │ +100 XP (100)   │
│ Execution Time │ 2.34s           │
│ Turns Used     │ 1               │
│ Total Tokens   │ 342             │
│ Provider       │ ollama          │
│ Model          │ llama3.1:8b     │
│ Active Badges  │ 🌱 Initiate     │
└────────────────┴─────────────────┘

Agent Output Summary:
Files in current directory:
- AGENTS.md
- README.md
- pyproject.toml
- harnessquest/
- tests/
- docs/
[TASK_COMPLETE]
```

### 5. Earn Your Badge!

- **XP**: +100 (Total: 100)
- **Level**: 1
- **Badge**: 🌱 **Initiate** — "Completed first agent run"

---

## What Just Happened?

1. **Initialization**: `HarnessRunner` created with Ollama provider
2. **Context Loading**: `ContextEngine` read `AGENTS.md` (or generated tree)
3. **Loop Turn 1**: 
   - Assembled messages with system prompt + repo context + user prompt
   - Sent to `llama3.1:8b` via Ollama
   - Model responded with `RUN: ls -la`
4. **Tool Execution**: Sandbox ran `ls -la`, captured output
5. **Loop Turn 2**:
   - Agent received tool result
   - Model responded with file list + `[TASK_COMPLETE]`
6. **Completion**: Gamification evaluated run (1 turn, 342 tokens, 0 faults)
7. **Rewards**: +100 XP, 🌱 Initiate badge unlocked

---

## Key Files to Explore

```bash
# Core loop implementation
cat harnessquest/core/runner.py

# Context engineering
cat harnessquest/core/context.py

# Sandbox security
cat harnessquest/core/sandbox.py

# Gamification
cat harnessquest/gamification/xp.py
```

---

## Experiment: Try Different Providers

```bash
# OpenAI
harnessquest-quest 1 --provider openai --model gpt-4o-mini

# Anthropic
harnessquest-quest 1 --provider anthropic --model claude-3-5-haiku-20241022

# NVIDIA NIM
harnessquest-quest 1 --provider nim --model meta/llama-3.1-70b-instruct

# Compare: turns, tokens, latency, cost
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "Provider configuration error" | Check `.env` has correct API key |
| "Ollama server not responding" | Run `ollama serve` in another terminal |
| "Max turns exceeded" | Increase `max_turns` or simplify prompt |
| No `[TASK_COMPLETE]` | Model didn't understand — try clearer prompt |

---

## Next Quest

**Level 2: Sandbox Apprentice** — Learn execution boundaries and security.

```bash
harnessquest-quest 2 --provider ollama --model llama3.1:8b
```

---

## Reflection Questions

1. What happens if you remove `[TASK_COMPLETE]` from the verification prompt?
2. How many turns does it take with different models?
3. What's the token count difference between providers?
4. What happens if you ask for a file outside the workspace?

---

## Further Reading

- [Tutorial: Understanding the Loop](../tutorials/02-understanding-the-loop.md)
- [Architecture: Agent Loop Flow](../architecture/agent-loop-flow.svg)
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)