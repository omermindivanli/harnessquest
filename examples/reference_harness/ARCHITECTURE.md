# Architecture

## Context
AGENTS.md map injected into the system prompt; history trimmed to a token budget.

## Tools
Validated tools returning structured results.

## Constraints
Turn limit, loop detection, timeouts.

## Verification
A gate checks output before accepting completion.

## Memory
Agent state saved to JSON and resumed.
