# Schema-Free CUPMEM: Phase 1 Memory Context Builder

This project is an early experiment inspired by the STALE paper and CUPMEM.

The goal is **not** to train a new AI model yet. The goal is to build a small memory/context system that can decide which user memories should still be trusted when new information arrives.

In simple terms:

```text
Old user memory comes in
New user observation comes in
The system checks whether the old memory is still safe to use
The system marks memory as ACTIVE, STALE, or UNKNOWN_CURRENT
Only the right memory should become context for the assistant
```

## What This Project Is Building

This is a **memory/context manager** for long-term AI assistants.

Normal assistants may place old and new messages together in context and hope the model figures everything out. This project tries to make that context cleaner before the assistant answers.

Example:

```text
Old memory:
The user bikes to work every day.

New observation:
The user has a leg cast for six weeks.
```

A basic memory system may keep both facts as active.

This project should eventually produce context like:

```text
ACTIVE:
- The user has a leg cast for six weeks.

UNKNOWN_CURRENT:
- The user's biking commute is unsafe to assume right now.

HISTORY:
- The user previously biked to work every day.
```

That way, the assistant does not blindly recommend a cycling route just because it remembers the old biking routine.

## Phase 1 Goal

Phase 1 is about building the basic memory workflow:

1. Store an old memory.
2. Store a new observation.
3. Represent both as memory cards.
4. Decide whether the old memory is still valid.
5. Compare a naive memory system with a state-aware memory system.

At this stage, the dataset still gives the code structured helper fields such as `old_state`, `new_state`, and `affected_states`.

That means this version is **not fully intelligent yet**. It is a scaffold for testing the memory-update pipeline.

## Important Idea

This project is not currently training a model.

Instead, it is building logic around memory:

```text
Training a model = changing the AI brain
Memory/context system = deciding what information the AI brain should see
```

Later, an existing LLM may be used to help extract states or detect conflicts, but the current phase is focused on the memory structure itself.

## Current Code

Run the experiment:

```bash
python3 src/schema_free_memory.py
```

The script compares two systems:

- `NaiveMemory`: stores memories but never marks old ones as outdated.
- `SchemaFreeMemory`: stores dynamic state cards and updates old memory status when new information affects it.

Memory status values:

```text
ACTIVE
The memory is still safe to use as current context.

STALE
The memory is outdated and should not guide current answers.

UNKNOWN_CURRENT
The old memory is unsafe to assume, but the exact replacement is not fully known.
```

## Dataset

The starter dataset is stored in:

```text
data/mini_stale.jsonl
```

Each example contains:

- an old memory
- a new observation
- a structured old state
- a structured new state
- which old state gets affected
- STALE-style test queries

Right now, the dataset acts like a teacher or answer key. The code uses the structured fields to practice the memory workflow.

## Why Start With Structure?

The full problem has many hard parts:

- extracting user state from natural language
- deciding whether two state names refer to the same user state
- detecting when one state affects another state
- marking old memories as active, stale, or uncertain
- answering questions without accepting stale premises

Starting with structured examples lets this project test the memory-update pipeline before adding harder inference steps.

## Next Milestones

1. Add clear decision logs explaining why a memory was marked `STALE` or `UNKNOWN_CURRENT`.
2. Remove the manual `affected_states` shortcut.
3. Build an automatic propagation detector.
4. Extract `old_state` and `new_state` from raw text instead of reading them from the dataset.
5. Add answer generation for SR, PR, and IPA queries.
6. Track errors such as over-invalidation, under-invalidation, and premise failure.

## Research Direction

The long-term question is:

```text
Can we build a schema-free memory system that decides which memories should become current context, stale history, or uncertain assumptions?
```

This repository is the first small step toward that system.

