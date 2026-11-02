# Harness Engineering Best Practices

Synthesized from OpenAI, Anthropic, Manus, LangChain, WalkingLabs, and industry practitioners.

---

## The Four Levers of Harness Engineering

### 1. Context Design
**What the model knows before it starts, and how that knowledge is structured.**

| Principle | Source | Implementation |
|-----------|--------|----------------|
| **Map, not manual** | OpenAI | AGENTS.md ≤100 lines, pointers to docs/ |
| **Progressive disclosure** | OpenAI/WalkingLabs | Load deep context only when needed |
| **KV-cache optimization** | Manus | Preserve cache locality, tool masking |
| **Filesystem memory** | Anthropic/Manus | feature_list.json, handoff artifacts |
| **Conversation condensation** | OpenHands | Summarize old turns, keep goals+failures |
| **Spec-driven context** | WalkingLabs | feature_list.json as source of truth |

### 2. Tool Selection
**Which tools the model has access to, how they're named, and dynamic management.**

| Principle | Source | Implementation |
|-----------|--------|----------------|
| **Fewer, better tools** | Vercel/Anthropic | Collapse 15→1 tools |
| **Strict schemas** | Anthropic | Pydantic validation, clear names |
| **Embedding router** | GitHub Copilot | Route to right tool via embeddings |
| **Logits masking** | Anthropic | Phase-specific tool gating |
| **Tool audit** | Anthropic | Regular review of tool necessity |

### 3. Constraint Management
**Time budgets, reasoning depth, loop detection, verification gates.**

| Principle | Source | Implementation |
|-----------|--------|----------------|
| **Turn limits** | All | max_turns=5-10 default |
| **Time budgets** | Anthropic | Max 5 min per task |
| **Loop detection** | Anthropic | Stop after 3 repeated actions |
| **Self-verification** | Anthropic/OpenAI | LLM-as-judge before completion |
| **Reasoning sandwich** | Anthropic | Think → Act → Verify |
| **Four-stage structure** | WalkingLabs | Plan → Execute → Verify → Reflect |

### 4. Production Hardening
**Sandboxing, memory compaction, observability.**

| Principle | Source | Implementation |
|-----------|--------|----------------|
| **Sandboxing** | All | gVisor, firecracker, seccomp, path validation |
| **Memory compaction** | OpenAI/Anthropic | Continuous summarization, offload to disk |
| **Observability** | OpenAI | Full stack: logs, metrics, traces |
| **Garbage collection** | OpenAI | 20% time on cleanup agents |
| **Regression CI** | LangChain | Benchmark on every PR |

---

## Architecture Patterns (from Snowan/Study Notes)

### Pattern 1: Single-Threaded Master Loop (Claude Code)
- One flat message list
- Subagents depth-limited to 1
- Simple, predictable, easy to debug

### Pattern 2: Hierarchical Planner-Executor (OpenAI Codex)
- Planner creates execution plan
- Executor implements with subagents
- Reviewer validates
- Clear separation of concerns

### Pattern 3: Multi-Agent Pipeline (Anthropic)
- Initializer → Coding Agent → Verifier
- Handoff artifacts (feature_list.json)
- Specialized roles per stage

### Pattern 4: Graph-Based Orchestration (LangGraph)
- State graph with nodes/edges
- Conditional routing
- Parallel execution support

---

## The 10 Mistakes Everyone Makes (from Snowan)

1. **Big AGENTS.md** — Writing 1000-line manuals instead of maps
2. **Too many tools** — Giving agents 20+ tools instead of 3-5 focused ones
3. **No loop detection** — Agents loop forever on failed approaches
4. **Trusting self-report** — No LLM-as-judge verification
5. **Ignoring token budget** — Burning $50 on $2 tasks
6. **Weak sandboxing** — Path traversal, dangerous commands allowed
7. **No observability** — Flying blind on token usage, latency, errors
8. **Spec-less prompting** — Vague prompts instead of feature_list.json
9. **Single-session thinking** — No state persistence across context windows
10. **No regression testing** — Harness degrades silently over time

---

## Minimum Viable Harness (MVH)

From Snowan's guide — the smallest harness that works:

```python
class MinimumViableHarness:
    def __init__(self):
        self.max_turns = 5
        self.tools = ["read_file", "write_file", "run_command"]
        self.verification = LLMAssistantJudge()
    
    async def run(self, task):
        for turn in range(self.max_turns):
            response = await llm.complete(self.build_prompt(task))
            if self.is_complete(response):
                if await self.verification.verify(task, response):
                    return response
            action = self.parse_action(response)
            result = self.execute(action)
            self.history.append(result)
        raise MaxTurnsExceeded()
```

---

## CAR Decomposition (WalkingLabs)

**Control–Agency–Runtime** — Three dimensions of harness design:

### Control (Constraints)
- Turn limits, time budgets
- Loop detection, verification gates
- Permission systems, tool allowlists
- Safety filters, prompt injection defense

### Agency (Autonomy)
- Tool set available
- Decision-making scope
- Subagent spawning permission
- Resource allocation (tokens, time)

### Runtime (Infrastructure)
- Sandbox implementation
- State persistence
- Context management
- Provider abstraction
- Observability stack

---

## HarnessCard (WalkingLabs)

Standardized reporting for harness designs:

```yaml
harness_card:
  name: "MyHarness v1.0"
  control:
    max_turns: 10
    time_budget_min: 5
    loop_detection: true
    verification: llm_as_judge
  agency:
    tools: [read, write, run, grep, task]
    subagents: true
    max_subagents: 3
  runtime:
    sandbox: "gvisor"
    context: "progressive_disclosure"
    providers: ["openai", "anthropic", "ollama"]
    observability: "otel"
  eval:
    benchmark: "custom_golden_set"
    metrics: ["pass@1", "tokens", "latency", "cost"]
```

---

## Evaluation Metrics That Matter

| Metric | Description | Target |
|--------|-------------|--------|
| **Pass@1** | First-try success rate | >80% |
| **Tokens/task** | Average token consumption | <2000 |
| **Latency** | End-to-end time | <60s |
| **Cost/task** | API cost per completion | <$0.10 |
| **Fault rate** | Sandbox errors per run | 0 |
| **Loop rate** | Turns wasted on loops | <10% |
| **Regression** | Benchmark delta vs baseline | 0% |

---

## When to Iterate vs. Rewrite (from Snowan)

**Iterate when:**
- Single component underperforming
- New model release needs integration
- Benchmark regression <5%
- Adding one tool/constraint

**Rewrite when:**
- Architecture pattern mismatch (e.g., single-thread → multi-agent)
- Multiple components failing simultaneously
- Benchmark regression >20%
- Fundamental security flaw discovered
- Context strategy needs complete overhaul (e.g., conversation → filesystem memory)

---

## Production Checklist (OpenAI-inspired)

- [ ] AGENTS.md exists and is <100 lines
- [ ] docs/ is system of record with freshness checks
- [ ] feature_list.json for spec-driven tasks
- [ ] Sandbox: path validation + forbidden commands + timeout
- [ ] LLM-as-judge verification gate
- [ ] Loop detection (3+ repeated actions)
- [ ] Token budget tracking + MINIMALIST target
- [ ] Observability: tokens, latency, cost, errors per run
- [ ] CI: benchmark suite on every PR
- [ ] Doc-gardening agent for stale docs
- [ ] Cleanup agent for technical debt
- [ ] Multi-provider fallback routing
- [ ] State persistence for long-running tasks
- [ ] Security: prompt injection analyzer
- [ ] HarnessCard documented

---

## Further Reading

### Primary Sources
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)
- [Anthropic: Effective Harnesses](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)
- [Anthropic: Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [LangChain: Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)
- [WalkingLabs: Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/en/)
- [Snowan: How to Build an Agent Harness](https://snowan.gitbook.io/study-notes/ai-blogs/how-to-build-agent-harness)
- [Engineer at Heart: Definitive Guide](https://engineeratheart.medium.com/the-definitive-guide-to-agent-harness-engineering-5f5edf25fd73)

### Courses
- [WalkingLabs Learn Harness Engineering](https://github.com/walkinglabs/learn-harness-engineering) — Project-based with Electron app
- [Phelan164: Codex Howto](https://github.com/Phelan164/codex-howto) — Codex-focused curriculum

### Reference Implementations
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) — Production coding agent
- [Claude Code](https://github.com/anthropics/claude-code) — Anthropic's harness (source leaked v2.1.88)
- [Codex CLI](https://github.com/openai/codex) — OpenAI's harness
- [LangChain DeepAgents](https://github.com/langchain-ai/langchain) — Rank 30→5 on Terminal Bench