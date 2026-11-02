"""20-Level Progressive Gamification System for HarnessQuest.

Each level teaches one core harness engineering concept through:
- Theory: Brief explanation of the concept
- Hands-on Quest: Runnable task demonstrating the concept
- Verification: Automated test proving mastery
- Badge: Unique achievement with icon
- XP Reward: Scaling with difficulty

Level Progression (20 Levels):
1. Initiate - Hello Harness (run first agent)
2. Sandbox Apprentice - Execution Boundaries
3. Context Novice - AGENTS.md & Repo Maps
4. Token Minimalist - Context Engineering
5. Tool Smith - Tool Design
6. Guardrail Guardian - Constraint Management
7. Verification Warden - Self-Verification Gates
8. Memory Keeper - State Persistence
9. Multi-Model Mage - Provider Abstraction
10. Local LLM Ranger - Ollama Integration
11. NIM Navigator - NVIDIA NIM Cloud
12. Observability Oracle - Telemetry & Tracing
13. Parallel Pilot - Multi-Agent Orchestration
14. Spec-Driven Sage - Spec-Driven Development
15. Context Condenser - Advanced Context Engineering
16. Security Sentinel - Prompt Injection Defense
17. Eval Architect - Benchmark Design
18. Harness Architect - Full System Design
19. Production Hardener - Production Hardening
20. Harness Grandmaster - Capstone Project
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import os
from pathlib import Path


class QuestStatus(Enum):
    """Status of a quest attempt."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Achievement:
    """Achievement badge earned by completing quests."""
    code: str
    title: str
    description: str
    icon: str
    level: int
    xp_reward: int = 0


@dataclass
class Quest:
    """A single learning quest in the progression."""
    level: int
    code: str
    title: str
    concept: str
    theory: str
    objective: str
    verification_prompt: str
    expected_criteria: str
    xp_reward: int
    badge: Achievement
    prerequisites: List[int] = field(default_factory=list)  # Required level numbers
    hints: List[str] = field(default_factory=list)
    difficulty: str = "beginner"  # beginner, intermediate, advanced, expert


# =============================================================================
# LEVEL DEFINITIONS - 20 Progressive Levels
# =============================================================================

QUESTS: Dict[int, Quest] = {
    1: Quest(
        level=1,
        code="INITIATE",
        title="Hello Harness",
        concept="Agent Loop Fundamentals",
        theory="""Every AI agent harness runs a loop: observe → reason → act → repeat. 
The harness provides the scaffolding: context injection, tool execution, turn limits, 
and completion detection. Understanding this loop is the foundation of all harness engineering.""",
        objective="Run your first agent task and observe the complete loop execution",
        verification_prompt="List the files in the current directory and output [TASK_COMPLETE]",
        expected_criteria="Agent successfully lists files and includes [TASK_COMPLETE] marker",
        xp_reward=100,
        badge=Achievement("INITIATE", "Initiate", "Completed first agent run", "🌱", 1, 100),
        hints=[
            "Use --provider ollama for free local testing",
            "The agent needs to output [TASK_COMPLETE] to finish",
            "Watch the turn counter - it should complete in 1-2 turns"
        ],
        difficulty="beginner",
    ),
    
    2: Quest(
        level=2,
        code="SANDBOX_APPRENTICE",
        title="Sandbox Apprentice",
        concept="Execution Boundaries & Security",
        theory="""A secure sandbox is the harness's immune system. It validates paths 
to prevent directory traversal, blocks dangerous commands (rm -rf, fork bombs), 
and enforces timeouts. Every production harness needs these guardrails.""",
        objective="Demonstrate sandbox path validation and command blocking",
        verification_prompt="Try to read a file outside the workspace (../../../etc/passwd) and run a blocked command (rm -rf /). Verify both are rejected.",
        expected_criteria="Agent attempts dangerous operations and sandbox correctly rejects them with PermissionError",
        xp_reward=150,
        badge=Achievement("SANDBOX_APPRENTICE", "Sandbox Apprentice", "Mastered execution boundaries", "🛡️", 2, 150),
        prerequisites=[1],
        hints=[
            "The sandbox validates paths with _validate_path()",
            "Forbidden commands are defined in run_command()",
            "Test both path traversal AND command blocking"
        ],
        difficulty="beginner",
    ),
    
    3: Quest(
        level=3,
        code="CONTEXT_NOVICE",
        title="Context Novice",
        concept="AGENTS.md & Repository Maps",
        theory="""Context is the agent's working memory. AGENTS.md serves as a table of 
contents - not an encyclopedia. The ContextEngine loads AGENTS.md or generates a 
repo tree map. Progressive disclosure: give the agent a map, not a 1000-page manual.""",
        objective="Create an AGENTS.md for this repo and verify the agent uses it",
        verification_prompt="Inspect the repository structure using the context engine and output [TASK_COMPLETE]",
        expected_criteria="Agent references AGENTS.md content in its response",
        xp_reward=150,
        badge=Achievement("CONTEXT_NOVICE", "Context Novice", "Learned repository context injection", "🗺️", 3, 150),
        prerequisites=[1],
        hints=[
            "Check harnessquest/core/context.py for ContextEngine",
            "AGENTS.md is loaded automatically if present",
            "The agent receives repo context in its system prompt"
        ],
        difficulty="beginner",
    ),
    
    4: Quest(
        level=4,
        code="TOKEN_MINIMALIST",
        title="Token Minimalist",
        concept="Context Engineering & Token Efficiency",
        theory="""Tokens are money and context window is scarce. OpenAI's Codex team 
learned: 'give Codex a map, not a 1000-page manual.' Techniques: summarization, 
progressive disclosure, KV-cache optimization, tool masking. Target: 20%+ reduction.""",
        objective="Implement a context summarizer that reduces token usage by 20%",
        verification_prompt="Run the same task twice - once with full context, once with your summarizer. Compare token counts.",
        expected_criteria="Token usage reduced by at least 20% while maintaining task success",
        xp_reward=200,
        badge=Achievement("TOKEN_MINIMALIST", "Token Minimalist", "Reduced token usage by 20%+", "🍃", 4, 200),
        prerequisites=[3],
        hints=[
            "Look at harnessquest/core/context.py assemble_context()",
            "Summarize history instead of passing full conversation",
            "Use the MINIMALIST badge criteria as reference (<1200 tokens)"
        ],
        difficulty="intermediate",
    ),
    
    5: Quest(
        level=5,
        code="TOOL_SMITH",
        title="Tool Smith",
        concept="Tool Design & Schema Validation",
        theory="""Tools are the agent's hands. Good tools have: clear names, strict schemas, 
minimal parameters, and predictable outputs. Vercel collapsed 15 tools to 1. 
Anthropic: 'tools should be easier for models to call correctly.'""",
        objective="Create a custom tool with JSON schema validation and test it",
        verification_prompt="Create a tool 'calculate' that takes two numbers and an operation (+,-,*,/) and returns result. Use it to compute 15 * 23.",
        expected_criteria="Custom tool executes correctly with validated inputs and returns structured output",
        xp_reward=200,
        badge=Achievement("TOOL_SMITH", "Tool Smith", "Designed a validated custom tool", "🔨", 5, 200),
        prerequisites=[2],
        hints=[
            "Extend ExecutionSandbox with a new tool method",
            "Use Pydantic for input validation",
            "Return structured JSON for reliable parsing"
        ],
        difficulty="intermediate",
    ),
    
    6: Quest(
        level=6,
        code="GUARDRAIL_GUARDIAN",
        title="Guardrail Guardian",
        concept="Constraint Management: Loops, Turns, Time Budgets",
        theory="""Agents loop, drift, and declare victory early. Constraints prevent this: 
turn limits (max 5-10), time budgets (max 5 min), loop detection (repeated actions), 
self-verification gates. Anthropic's Claude Code uses ~40 conditional prompt sections.""",
        objective="Add loop detection that stops the agent if it repeats the same action 3 times",
        verification_prompt="Create a task that would cause looping. Verify your detector stops it.",
        expected_criteria="Agent stops with 'loop detected' after 3 repeated actions",
        xp_reward=250,
        badge=Achievement("GUARDRAIL_GUARDIAN", "Guardrail Guardian", "Implemented loop detection and turn limits", "⛔", 6, 250),
        prerequisites=[2, 5],
        hints=[
            "Track action history in the runner",
            "Compare last N actions for similarity",
            "Add time budget injection in system prompt"
        ],
        difficulty="intermediate",
    ),
    
    7: Quest(
        level=7,
        code="VERIFICATION_WARDEN",
        title="Verification Warden",
        concept="Self-Verification Gates & LLM-as-Judge",
        theory="""Don't trust the agent's self-report. Use LLM-as-judge: a separate model 
evaluates output against criteria. OpenAI uses agent-to-agent review. Anthropic uses 
initializer + coding agent with handoff artifacts. Evaluation must be automated.""",
        objective="Implement a verification step that checks agent output before marking complete",
        verification_prompt="Run a task where agent output is subtly wrong. Verify your judge catches it.",
        expected_criteria="Judge correctly identifies incorrect output and prevents false completion",
        xp_reward=300,
        badge=Achievement("VERIFICATION_WARDEN", "Verification Warden", "Built LLM-as-judge evaluation gate", "⚖️", 7, 300),
        prerequisites=[6],
        hints=[
            "Check harnessquest/eval/judge.py for HarnessJudge",
            "Use a different model for judging than execution",
            "Structured JSON output for reliable parsing"
        ],
        difficulty="advanced",
    ),
    
    8: Quest(
        level=8,
        code="MEMORY_KEEPER",
        title="Memory Keeper",
        concept="State Persistence & Session Resumption",
        theory="""Long-running tasks span multiple sessions. Anthropic's initializer agent 
creates feature_list.json with 200+ features marked 'failing'. Coding agent makes 
incremental progress, leaves handoff artifacts. State must survive context window limits.""",
        objective="Implement session save/restore: persist history, progress, and resume seamlessly",
        verification_prompt="Start a task, interrupt it, resume from saved state and complete it",
        expected_criteria="Agent resumes from exact interruption point with full context",
        xp_reward=300,
        badge=Achievement("MEMORY_KEEPER", "Memory Keeper", "Mastered session persistence and resumption", "💾", 8, 300),
        prerequisites=[7],
        hints=[
            "Save history + progress to JSON file",
            "Load on resume and inject into context",
            "Track feature_list.json style progress markers"
        ],
        difficulty="advanced",
    ),
    
    9: Quest(
        level=9,
        code="MULTI_MODEL_MAGE",
        title="Multi-Model Mage",
        concept="Provider Abstraction & Seamless Switching",
        theory="""Different models for different tasks: GPT-4o for reasoning, Haiku for speed, 
Nemotron for coding. Provider abstraction lets you switch without code changes. 
LiteLLM unifies 100+ providers. Fallback routing for resilience.""",
        objective="Configure 3 providers and demonstrate mid-task fallback on failure",
        verification_prompt="Run a task with primary provider, simulate failure, verify fallback to secondary",
        expected_criteria="Task completes successfully despite primary provider failure",
        xp_reward=350,
        badge=Achievement("MULTI_MODEL_MAGE", "Multi-Model Mage", "Orchestrated multi-provider fallback", "🔮", 9, 350),
        prerequisites=[1],
        hints=[
            "Use harnessquest/core/providers.py factory",
            "Implement try/except with provider switching",
            "Test with --provider flag"
        ],
        difficulty="intermediate",
    ),
    
    10: Quest(
        level=10,
        code="LOCAL_LLM_RANGER",
        title="Local LLM Ranger",
        concept="Ollama Integration & Offline Privacy",
        theory="""Local LLMs enable: privacy (data never leaves), offline work, zero API costs, 
custom models. Ollama makes this accessible. Trade-off: smaller models, slower inference. 
Harness must handle variable context windows and capabilities.""",
        objective="Run a complete quest using only local Ollama models (no cloud API)",
        verification_prompt="Complete Level 1 quest using ollama provider with llama3.1:8b",
        expected_criteria="Full quest completion with local model, no external API calls",
        xp_reward=300,
        badge=Achievement("LOCAL_LLM_RANGER", "Local LLM Ranger", "Ran harness fully offline with Ollama", "🏔️", 10, 300),
        prerequisites=[9],
        hints=[
            "Install ollama: https://ollama.com",
            "Pull model: ollama pull llama3.1:8b",
            "Run server: ollama serve",
            "Use --provider ollama --model llama3.1:8b"
        ],
        difficulty="intermediate",
    ),
    
    11: Quest(
        level=11,
        code="NIM_NAVIGATOR",
        title="NIM Navigator",
        concept="NVIDIA NIM Cloud & Specialized Models",
        theory="""NVIDIA NIM provides optimized, containerized models: Nemotron (reasoning), 
Llama (general), Mistral (multilingual). Enterprise-grade: SLA, compliance, GPU-optimized. 
API compatible with OpenAI format. Requires NVIDIA_API_KEY from build.nvidia.com.""",
        objective="Configure NIM and run a coding task with Nemotron 3 Ultra",
        verification_prompt="Use NIM provider with nemotron-3-ultra to write a Python function with tests",
        expected_criteria="Successful completion using NVIDIA NIM endpoint",
        xp_reward=400,
        badge=Achievement("NIM_NAVIGATOR", "NIM Navigator", "Harnessed NVIDIA NIM cloud models", "🚀", 11, 400),
        prerequisites=[9],
        hints=[
            "Get API key: https://build.nvidia.com",
            "Set NVIDIA_API_KEY and NVIDIA_NIM_BASE_URL in .env",
            "Try nemotron-3-ultra for reasoning tasks"
        ],
        difficulty="advanced",
    ),
    
    12: Quest(
        level=12,
        code="OBSERVABILITY_ORACLE",
        title="Observability Oracle",
        concept="Telemetry, Tracing & Metrics",
        theory="""You can't improve what you don't measure. OpenAI gives Codex full observability 
stack: logs (LogQL), metrics (PromQL), traces (TraceQL). Instrument: token usage, latency, 
tool calls, errors, turn count. Export to OpenTelemetry for Grafana/Jaeger.""",
        objective="Add OpenTelemetry tracing to the runner with spans for each turn",
        verification_prompt="Run a task and verify traces appear in console/OTEL collector",
        expected_criteria="Each turn creates a span with: model, tokens, duration, tools_called, status",
        xp_reward=350,
        badge=Achievement("OBSERVABILITY_ORACLE", "Observability Oracle", "Implemented full telemetry and tracing", "🔮", 12, 350),
        prerequisites=[7],
        hints=[
            "Add opentelemetry-api and opentelemetry-sdk dependencies",
            "Create spans in runner.run() loop",
            "Export to console or OTLP endpoint"
        ],
        difficulty="advanced",
    ),
    
    13: Quest(
        level=13,
        code="PARALLEL_PILOT",
        title="Parallel Pilot",
        concept="Multi-Agent Orchestration & Handoff",
        theory="""Complex tasks need specialization: planner → coder → reviewer → tester. 
Anthropic's initializer + coding agent pattern. Each sub-agent gets scoped context, 
produces handoff artifact. Parent coordinates, merges results. Avoid shared state chaos.""",
        objective="Implement a 2-agent pipeline: planner creates plan, executor implements it",
        verification_prompt="Give a multi-step task. Verify planner creates plan, executor follows it",
        expected_criteria="Two agents collaborate via structured handoff artifact",
        xp_reward=450,
        badge=Achievement("PARALLEL_PILOT", "Parallel Pilot", "Orchestrated multi-agent pipeline", "✈️", 13, 450),
        prerequisites=[8, 9],
        hints=[
            "Create sub-agent runner with scoped workspace",
            "Pass handoff artifact (JSON) between agents",
            "Use feature_list.json pattern from Anthropic"
        ],
        difficulty="expert",
    ),
    
    14: Quest(
        level=14,
        code="SPEC_DRIVEN_SAGE",
        title="Spec-Driven Sage",
        concept="Spec-Driven Development (SDD)",
        theory="""WalkingLabs course teaches: specs first, code second. feature_list.json defines 
what to build (200+ features). AGENTS.md defines how to work. Agents execute from specs, 
not vague prompts. This is how OpenAI built 1M lines with 3 engineers.""",
        objective="Create feature_list.json for a small project and have agent implement from it",
        verification_prompt="Define 5 features in feature_list.json. Agent implements all 5 with tests",
        expected_criteria="All features implemented and marked 'passing' in feature_list.json",
        xp_reward=400,
        badge=Achievement("SPEC_DRIVEN_SAGE", "Spec-Driven Sage", "Built from specification, not prompt", "📋", 14, 400),
        prerequisites=[8, 13],
        hints=[
            "Format: [{id, name, description, status: failing/passing}]",
            "Agent reads spec, implements one feature at a time",
            "Update status after verification"
        ],
        difficulty="advanced",
    ),
    
    15: Quest(
        level=15,
        code="CONTEXT_CONDENSER",
        title="Context Condenser",
        concept="Advanced Context Engineering: KV-Cache, Compression",
        theory="""Manus optimizes KV-cache locality. OpenHands condenses conversation: keep goals, 
progress, critical files, failing tests. HumanLayer: context-efficient backpressure. 
Techniques: summarization, tool masking, filesystem memory, keeping useful failures in-context.""",
        objective="Implement conversation condensation that preserves goals+progress+failures",
        verification_prompt="Run a 20-turn task. Verify condensed context retains goals and failures",
        expected_criteria="Context size stays bounded while critical info preserved",
        xp_reward=500,
        badge=Achievement("CONTEXT_CONDENSER", "Context Condenser", "Mastered KV-cache optimization and condensation", "📦", 15, 500),
        prerequisites=[4, 12],
        hints=[
            "Summarize old turns, keep last 5 full",
            "Preserve: original goal, current plan, failing tests, critical files",
            "Tool masking: only show relevant tools per phase"
        ],
        difficulty="expert",
    ),
    
    16: Quest(
        level=16,
        code="SECURITY_SENTINEL",
        title="Security Sentinel",
        concept="Prompt Injection Defense & Hardened Sandbox",
        theory="""OpenHands: confirmation mode, analyzers, sandboxing, hard policies. 
MCP Guardian: progressive tool discovery, scope-based allow/block, audit logging. 
APort: pre-action authorization hooks. Defense in depth: multiple layers.""",
        objective="Add prompt injection analyzer that scans tool commands before execution",
        verification_prompt="Attempt prompt injection via crafted tool input. Verify it's blocked and logged",
        expected_criteria="Injection attempts detected, blocked, and logged with severity",
        xp_reward=500,
        badge=Achievement("SECURITY_SENTINEL", "Security Sentinel", "Hardened against prompt injection", "🛡️", 16, 500),
        prerequisites=[2, 12],
        hints=[
            "Scan for: ignore previous, system prompt, base64, encoded payloads",
            "Add pre-execution hook in sandbox.run_command()",
            "Log all blocked attempts with timestamp and context"
        ],
        difficulty="expert",
    ),
    
    17: Quest(
        level=17,
        code="EVAL_ARCHITECT",
        title="Eval Architect",
        concept="Benchmark Design & Regression CI",
        theory="""LangChain DeepAgents: rank 30→5 (52.8%→66.5%) via harness only. 
Golden datasets: input + expected output + criteria. CI runs on every PR. 
Metrics: pass rate, token efficiency, latency, cost. Regression detection alerts.""",
        objective="Build a benchmark suite with 10 golden tasks and CI integration",
        verification_prompt="Run benchmark suite. Verify CI runs it on PR and reports regression",
        expected_criteria="CI passes, detects intentional regression, reports metrics",
        xp_reward=550,
        badge=Achievement("EVAL_ARCHITECT", "Eval Architect", "Designed benchmark suite with CI regression detection", "📊", 17, 550),
        prerequisites=[7, 12],
        hints=[
            "Create tests/golden/ with task JSON files",
            "Extend .github/workflows/quest_eval.yml",
            "Track: pass@1, tokens, latency, cost per task"
        ],
        difficulty="expert",
    ),
    
    18: Quest(
        level=18,
        code="HARNESS_ARCHITECT",
        title="Harness Architect",
        concept="Full System Design: CAR Decomposition",
        theory="""WalkingLabs CAR: Control–Agency–Runtime. Control: constraints, guards. 
Agency: tools, permissions, autonomy level. Runtime: sandbox, state, orchestration. 
HarnessCard: structured reporting. Design a harness for a real project end-to-end.""",
        objective="Design and document a complete harness for a real-world use case",
        verification_prompt="Produce: ARCHITECTURE.md, AGENTS.md, feature_list.json, provider config, eval plan",
        expected_criteria="Complete harness design document covering all CAR components",
        xp_reward=600,
        badge=Achievement("HARNESS_ARCHITECT", "Harness Architect", "Designed production harness end-to-end", "🏗️", 18, 600),
        prerequisites=[14, 15, 16],
        hints=[
            "Follow WalkingLabs CAR framework",
            "Include: context strategy, tool set, constraints, runtime, eval",
            "Document trade-offs and decisions"
        ],
        difficulty="expert",
    ),
    
    19: Quest(
        level=19,
        code="PRODUCTION_HARDENER",
        title="Production Hardener",
        concept="Production Hardening: Sandboxing, Compaction, Observability",
        theory="""OpenAI: 'garbage collection' for technical debt. Continuous cleanup agents. 
Memory compaction: summarize, offload, preserve critical. Sandboxing: gVisor, firecracker, 
seccomp. Observability: full stack. 20% time on maintenance, not features.""",
        objective="Harden the harness: add sandboxing, compaction scheduler, maintenance agents",
        verification_prompt="Run stress test: 100 concurrent tasks. Verify stability, no leaks, cleanup works",
        expected_criteria="Stable under load, memory bounded, auto-cleanup functional",
        xp_reward=700,
        badge=Achievement("PRODUCTION_HARDENER", "Production Hardener", "Hardened harness for production scale", "🏭", 19, 700),
        prerequisites=[12, 15, 16],
        hints=[
            "Add background compaction task",
            "Implement resource quotas per task",
            "Add health checks and auto-recovery"
        ],
        difficulty="expert",
    ),
    
    20: Quest(
        level=20,
        code="GRANDMASTER",
        title="Harness Grandmaster",
        concept="Capstone: Build & Document Your Own Harness",
        theory="""The ultimate test: create a harness from scratch for a domain of your choice. 
Apply everything: multi-provider, sandbox, context, constraints, eval, observability, 
multi-agent, spec-driven, security, production hardening. Document for others to learn.""",
        objective="Build a complete, documented harness for a new domain and publish it",
        verification_prompt="Submit: GitHub repo with working harness, docs, 5+ quests, CI passing",
        expected_criteria="Independent harness project usable by others, all CI green",
        xp_reward=1000,
        badge=Achievement("GRANDMASTER", "Harness Grandmaster", "Created and published an original harness", "👑", 20, 1000),
        prerequisites=[18, 19],
        hints=[
            "Choose a domain: data analysis, web scraping, code review, etc.",
            "Reuse HarnessQuest components where applicable",
            "Write tutorials for each quest level"
        ],
        difficulty="expert",
    ),
}


# =============================================================================
# PROGRESSION ENGINE
# =============================================================================

class ProgressionEngine:
    """Manages player progression through the 20 levels."""
    
    def __init__(self, storage_path: str = ".harnessquest_progress.json"):
        self.storage_path = Path(storage_path)
        self.player_data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load player progress from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_xp": 0,
            "level": 1,
            "completed_quests": [],
            "unlocked_badges": [],
            "current_quest": 1,
            "quest_attempts": {},
        }
    
    def _save(self):
        """Save player progress to disk."""
        with open(self.storage_path, "w") as f:
            json.dump(self.player_data, f, indent=2)
    
    def get_quest(self, level: int) -> Optional[Quest]:
        """Get quest by level number."""
        return QUESTS.get(level)
    
    def get_available_quests(self) -> List[Quest]:
        """Get all quests the player can currently attempt."""
        available = []
        for level in range(1, 21):
            quest = QUESTS[level]
            status = self.get_quest_status(level)
            if status in [QuestStatus.AVAILABLE, QuestStatus.IN_PROGRESS]:
                available.append(quest)
        return available
    
    def get_quest_status(self, level: int) -> QuestStatus:
        """Get status of a specific quest."""
        if level in self.player_data.get("completed_quests", []):
            return QuestStatus.COMPLETED
        
        # Check prerequisites
        quest = QUESTS.get(level)
        if not quest:
            return QuestStatus.LOCKED
        
        for prereq in quest.prerequisites:
            if prereq not in self.player_data.get("completed_quests", []):
                return QuestStatus.LOCKED
        
        if level == self.player_data.get("current_quest", 1):
            return QuestStatus.IN_PROGRESS
        
        # A level is only COMPLETED if it is in completed_quests (checked above);
        # jumping ahead no longer marks skipped levels as completed.
        return QuestStatus.AVAILABLE
    
    def start_quest(self, level: int) -> bool:
        """Mark a quest as in progress."""
        # Allow AVAILABLE, IN_PROGRESS (the current quest) and COMPLETED (replays);
        # only locked quests are refused. Previously Level 1 could never be "started".
        if self.get_quest_status(level) == QuestStatus.LOCKED:
            return False
        attempts = self.player_data.setdefault("quest_attempts", {})
        key = str(level)  # JSON object keys are strings; int keys broke after reload
        attempts[key] = attempts.get(key, 0) + 1
        if level not in self.player_data.get("completed_quests", []):
            self.player_data["current_quest"] = level
        self._save()
        return True
    
    def complete_quest(self, level: int) -> Dict[str, Any]:
        """Mark quest complete and award XP/badge."""
        quest = QUESTS.get(level)
        if not quest:
            return {"success": False, "error": "Quest not found"}
        
        if level in self.player_data.get("completed_quests", []):
            return {"success": False, "error": "Already completed"}
        
        # Award XP
        xp = quest.xp_reward
        self.player_data["total_xp"] += xp
        self.player_data["completed_quests"].append(level)
        self.player_data["unlocked_badges"].append({
            "code": quest.badge.code,
            "title": quest.badge.title,
            "icon": quest.badge.icon,
            "level": level,
        })
        
        # Calculate new level (every 500 XP = 1 level)
        new_level = (self.player_data["total_xp"] // 500) + 1
        self.player_data["level"] = new_level
        
        # Unlock next quest
        if level < 20:
            self.player_data["current_quest"] = level + 1
        
        self._save()
        
        return {
            "success": True,
            "xp_earned": xp,
            "total_xp": self.player_data["total_xp"],
            "new_level": new_level,
            "badge": {
                "code": quest.badge.code,
                "title": quest.badge.title,
                "icon": quest.badge.icon,
            },
        }
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary."""
        completed = len(self.player_data.get("completed_quests", []))
        return {
            "level": self.player_data.get("level", 1),
            "total_xp": self.player_data.get("total_xp", 0),
            "quests_completed": f"{completed}/20",
            "completion_pct": round(completed / 20 * 100, 1),
            "badges": self.player_data.get("unlocked_badges", []),
            "current_quest": self.player_data.get("current_quest", 1),
        }


# Global progression engine instance
_progression_engine: Optional[ProgressionEngine] = None


def get_progression_engine(storage_path: Optional[str] = None) -> ProgressionEngine:
    """Get global progression engine instance."""
    global _progression_engine
    if _progression_engine is None:
        path = storage_path or ".harnessquest_progress.json"
        _progression_engine = ProgressionEngine(path)
    return _progression_engine