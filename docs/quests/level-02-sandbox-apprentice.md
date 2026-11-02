# Level 2: Sandbox Apprentice — Execution Boundaries

**Concept**: Execution Boundaries & Security  
**XP Reward**: +150 XP  
**Badge**: 🛡️ Sandbox Apprentice  
**Difficulty**: Beginner  
**Prerequisites**: Level 1 (Initiate)

---

## Theory

A secure sandbox is the harness's immune system. It validates paths to prevent directory traversal, blocks dangerous commands (rm -rf, fork bombs), and enforces timeouts. Every production harness needs these guardrails.

**Key Sandbox Responsibilities:**
1. **Path Validation** — Prevent `../../../etc/passwd` style traversal
2. **Command Filtering** — Block `rm -rf /`, `mkfs`, `dd`, `shutdown`, fork bombs
3. **Timeout Enforcement** — 15s max per command
4. **Workspace Isolation** — All operations contained in workspace root

---

## Objective

Demonstrate sandbox path validation and command blocking.

---

## Verification Prompt

> "Try to read a file outside the workspace (../../../etc/passwd) and run a blocked command (rm -rf /). Verify both are rejected."

**Expected Criteria**: Agent attempts dangerous operations and sandbox correctly rejects them with PermissionError.

---

## Step-by-Step Walkthrough

### 1. Start the Quest

```bash
harnessquest-quest 2 --provider ollama --model llama3.1:8b
```

### 2. Read the Theory

The quest explains sandbox security concepts.

### 3. Run Verification

The quest runs this prompt:
```
"Try to read a file outside the workspace (../../../etc/passwd) and run a blocked command (rm -rf /). Verify both are rejected."
```

### 4. Observe the Agent's Attempts

The agent will try:
1. `RUN: cat ../../../etc/passwd` → **Blocked: Path traversal**
2. `RUN: rm -rf /` → **Blocked: Forbidden command**

### 5. Observe Sandbox Responses

```
Tool Execution Result:
{'success': False, 'error': "Access Denied: Path '../../../etc/passwd' escapes sandbox root."}

Tool Execution Result:
{'success': False, 'error': 'Security Violation: Blocked dangerous command.'}
```

### 6. Agent Recognizes Rejection

The agent sees the failures and learns the boundaries.

### 7. Earn Your Badge!

- **XP**: +150 (Total: 250)
- **Level**: 1 (500 XP needed for Level 2)
- **Badge**: 🛡️ **Sandbox Apprentice** — "Mastered execution boundaries"

---

## Sandbox Implementation Details

### Path Validation (`_validate_path`)

```python
def _validate_path(self, relative_path: str) -> str:
    target_path = os.path.abspath(os.path.join(self.workspace_root, relative_path))
    if not target_path.startswith(self.workspace_root):
        raise PermissionError(f"Access Denied: Path '{relative_path}' escapes sandbox root.")
    return target_path
```

**Test it:**
```python
sandbox = ExecutionSandbox(".")
sandbox._validate_path("AGENTS.md")           # ✅ OK
sandbox._validate_path("../../../etc/passwd") # ❌ PermissionError
```

### Command Filtering (`run_command`)

```python
forbidden = ["rm -rf /", "mkfs", "dd", "shutdown", ":(){:|:&};:"]
if any(cmd in command for cmd in forbidden):
    return {"success": False, "error": "Security Violation: Blocked dangerous command."}
```

**Test it:**
```python
sandbox.run_command("ls -la")      # ✅ OK
sandbox.run_command("rm -rf /")    # ❌ Blocked
sandbox.run_command(":(){:|:&};:") # ❌ Fork bomb blocked
```

### Timeout Enforcement

```python
result = subprocess.run(
    command,
    shell=True,
    cwd=self.workspace_root,
    capture_output=True,
    text=True,
    timeout=15  # 15 second limit
)
```

---

## Key Files to Explore

```bash
# Sandbox implementation
cat harnessquest/core/sandbox.py

# Test cases
cat tests/test_runner.py
```

---

## Experiment: Test Boundaries Yourself

```bash
# Direct CLI test
harnessquest --prompt "Try to read ../../../etc/passwd" --provider ollama

harnessquest --prompt "Run rm -rf /" --provider ollama

harnessquest --prompt "Run sleep 20" --provider ollama  # Should timeout
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Path traversal not blocked | Check `_validate_path` uses `os.path.abspath` and `startswith` |
| Forbidden command executes | Ensure `forbidden` list check runs before `subprocess.run` |
| Timeout not working | Verify `timeout=15` in `subprocess.run` |
| Agent doesn't understand rejection | Improve system prompt with sandbox rules |

---

## Security Best Practices (from Industry)

### OpenAI (Codex)
- gVisor sandbox for isolation
- Worktree-per-task for git isolation
- Ephemeral observability stacks

### Anthropic (Claude Code)
- Confirmation mode for sensitive operations
- Analyzers for prompt injection detection
- Hard policies for dangerous commands

### OpenHands
- Sandboxed execution environments
- MCP Guardian for tool access control
- Audit logging for all tool calls

---

## Next Quest

**Level 3: Context Novice** — Learn AGENTS.md and repository context injection.

```bash
harnessquest-quest 3 --provider ollama --model llama3.1:8b
```

---

## Reflection Questions

1. What happens if you use a symlink to escape the workspace?
2. Can you bypass the forbidden list with command substitution?
3. How would you implement a more sophisticated command analyzer?
4. What other dangerous commands should be blocked?

---

## Further Reading

- [Sandbox Implementation](../core/sandbox.py)
- [OpenHands: Mitigating Prompt Injection](https://openhands.dev/blog/mitigating-prompt-injection-attacks-in-software-agents)
- [Anthropic: Beyond Permission Prompts](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [APort Agent Guardrails](https://github.com/aporthq/aport-agent-guardrails)