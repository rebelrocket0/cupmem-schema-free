# Schema-Free STALE Memory Experiment

This project is a tiny starting point for experimenting with a CUPMEM-inspired memory system without a fixed schema.

The first goal is not to build a perfect assistant. The first goal is to create a measurable loop:

1. Add an old memory.
2. Add a newer observation.
3. Decide whether the old memory is still active, stale, or uncertain.
4. Test the system with STALE-style queries.
5. Record the failure type and improve one module.

## First Step

Run the structured experiment:

```bash
python3 src/schema_free_memory.py
```

This compares two systems:

- `NaiveMemory`: stores old and new memories but never adjudicates stale state.
- `SchemaFreeMemory`: uses dynamically named state cards and example-level causal links to decide whether old memory should become `STALE` or `UNKNOWN_CURRENT`.

## Why Structured First?

The full research problem has several hard parts:

- extracting state from natural language
- matching whether two states describe the same hidden attribute
- detecting causal propagation between different states
- deciding whether to keep, stale, replace, or mark uncertain
- answering without accepting stale premises

This first version starts with structured state cards so we can test the memory-adjudication idea before adding LLM-based extraction.

## Next Experiments

After this runs, improve it in this order:

1. Add more examples to `data/mini_stale.jsonl`.
2. Add failure labels for wrong decisions.
3. Replace the manual `affected_states` field with a dynamic propagation detector.
4. Add an LLM or embedding-based state extractor.
5. Compare against a naive retrieval baseline on SR, PR, and IPA queries.

