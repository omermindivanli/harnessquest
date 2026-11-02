# Context Engineering Tutorial

> **"Give the agent a map, not a 1,000-page instruction manual."** — OpenAI Codex Team

## The Context Problem

Context is the agent's working memory. Three failure modes:

1. **Context Overflow** — Too much context crowds out task, code, relevant docs
2. **Non-Guidance** — When everything is "important," nothing is. Agents pattern-match locally.
3. **Staleness** — Monolithic manuals rot instantly. Agents can't tell what's still true.

## HarnessQuest's Solution: Progressive Disclosure

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROGRESSIVE DISCLOSURE                        │
├─────────────────────────────────────────────────────────────────┤
│  Level 1: AGENTS.md (map only, ~100 lines)                      │
│         └── "Here's the repo structure, here are the rules"     │
│                                                                   │
│  Level 2: Repo Tree (on demand)                                 │
│         └── "Here are the files and directories"                │
│                                                                   │
│  Level 3: Deep Docs (when agent asks)                           │
│         └── "Here's docs/architecture.md"                       │
│                                                                   │
│  Level 4: Specs (feature_list.json)                             │
│         └── "Here's what to build, feature by feature"          │
│                                                                   │
│  Level 5: Surgical File Reads (when needed)                     │
│         └── "Here's the exact file content you need"            │
└─────────────────────────────────────────────────────────────────┘
```

## AGENTS.md: The Map

**Location**: Repository root (auto-loaded by ContextEngine)

**Purpose**: Table of contents for the agent, not encyclopedia

**Template**:
```markdown
# Repository Architecture Map (AGENTS.md)

## Directory Structure
- `src/`: Main source code
- `tests/`: Test suites
- `docs/`: Documentation
- `scripts/`: Utility scripts

## Key Files
- `src/main.py`: Entry point
- `src/config.py`: Configuration
- `tests/test_core.py`: Core tests

## Rules
1. Operate strictly within sandbox boundaries
2. Signal completion with '[TASK_COMPLETE]'
3. Use tools for file operations, not direct writes
```

## ContextEngine Implementation

```python
class ContextEngine:
    def load_repo_map(self) -> str:
        """Load AGENTS.md or generate minimalist fallback."""
        agents_map = self.root_dir / "AGENTS.md"
        if agents_map.exists():
            return agents_map.read_text()
        
        # Fallback: generate tree map
        tree = []
        for path in sorted(self.root_dir.rglob("*")):
            if any(part.startswith(".") for part in path.parts):
                continue
            depth = len(path.relative_to(self.root_dir).parts)
            tree.append("  " * (depth - 1) + f"├── {path.name}")
        return "Repository Tree Map:\n" + "\n".join(tree[:50])
    
    def assemble_context(self, system_prompt, user_prompt, history):
        repo_map = self.load_repo_map()
        combined_system = f"""
{system_prompt}

=== REPOSITORY HARNESS CONTEXT ===
{repo_map}
===================================

Rules:
1. You must operate strictly within the provided harness boundary.
2. Signal completion by including '[TASK_COMPLETE]' in your message.
"""
        messages = [{"role": "system", "content": combined_system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})
        return messages
```

## Token Budget Management

### The MINIMALIST Badge Target: < 1,200 tokens

```python
# In GamificationEngine
token_bonus = max(0, int((2000 - total_tokens) * 0.1)) if total_tokens < 2000 else 0
# Under 1200 tokens → MINIMALIST badge (+50 XP)
```

### Strategies for Token Efficiency

| Strategy | Description | Token Savings |
|----------|-------------|---------------|
| **Summarize History** | Keep last 5 turns full, summarize older | 50-70% |
| **Tool Masking** | Only show relevant tools per phase | 20-30% |
| **Progressive Disclosure** | Load deep docs only when asked | 40-60% |
| **Surgical Reads** | Read specific files, not entire dirs | 30-50% |
| **KV-Cache Optimization** | Preserve cache locality (Manus pattern) | 10-20% |

## Advanced: Conversation Condensation (Level 15)

OpenHands pattern for long-running sessions:

```python
def condense_conversation(history, max_tokens=10000):
    """Condense while preserving critical info."""
    # Always keep:
    # 1. Original goal/task
    # 2. Current plan/state
    # 3. Critical files referenced
    # 4. Failing tests/errors
    # 5. Last 5 turns (full detail)
    
    # Summarize older turns:
    # "Turns 1-10: Explored repo structure, identified 3 target files"
    # "Turns 11-15: Implemented feature X, test failed on edge case"
    
    return condensed_history
```

## Level 3 Quest: Context Novice

**Objective**: Create AGENTS.md and verify agent uses it

```bash
harnessquest-quest 3 --provider ollama --model llama3.1:8b
```

**Steps**:
1. Quest explains AGENTS.md purpose
2. You create/update AGENTS.md for the repo
3. Verification: Agent references AGENTS.md content
4. Badge: 🗺️ Context Novice (+150 XP)

## Level 4 Quest: Token Minimalist

**Objective**: Implement context summarizer reducing tokens 20%+

```bash
harnessquest-quest 4 --provider ollama --model llama3.1:8b
```

**Steps**:
1. Quest explains token budget concepts
2. You implement `summarize_history()` in ContextEngine
3. Verification: Compare token counts before/after
4. Badge: 🍃 Token Minimalist (+200 XP)

## Best Practices from Industry

### OpenAI (Codex)
- AGENTS.md as TOC, not encyclopedia
- Docs/ as system of record
- Doc-gardening agents for freshness
- Progressive disclosure via pointers

### Anthropic (Claude Code)
- Initializer agent creates feature_list.json
- Coding agent makes incremental progress
- Handoff artifacts between sessions
- Self-verification gates

### Manus
- KV-cache locality optimization
- Filesystem memory (not conversation)
- Tool masking per phase
- Keep useful failures in-context

### WalkingLabs
- CAR decomposition: Control-Agency-Runtime
- Spec-driven: feature_list.json + AGENTS.md
- HarnessCard for structured reporting

## Exercises

1. **Create AGENTS.md** for a real project you're working on
2. **Measure tokens** before/after adding context
3. **Implement summarization** for a 20-turn conversation
4. **Design tool masking** for a coding agent (show only file tools in edit phase)

## Next: Tool Design Tutorial

Learn how to design tools that agents can call correctly and safely.