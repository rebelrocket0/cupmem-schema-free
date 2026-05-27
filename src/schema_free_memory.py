from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ACTIVE = "ACTIVE"
STALE = "STALE"
UNKNOWN_CURRENT = "UNKNOWN_CURRENT"


@dataclass
class StateCard:
    id: str
    name: str
    value: str
    evidence: str
    status: str = ACTIVE
    confidence: float = 1.0
    related_states: list[str] = field(default_factory=list)


class NaiveMemory:
    """Retrieval-only baseline: stores everything and never retires old memories."""

    def __init__(self) -> None:
        self.cards: list[StateCard] = []

    def add(self, card: StateCard) -> None:
        self.cards.append(card)

    def statuses(self) -> dict[str, str]:
        return {card.id: card.status for card in self.cards}


class SchemaFreeMemory:
    """
    Tiny CUPMEM-style prototype.

    This first version is schema-free in the sense that state names are dynamic strings,
    not fixed slots like health_and_mobility.current_health_state.
    """

    def __init__(self) -> None:
        self.cards: list[StateCard] = []

    def add_old_state(self, example: dict) -> None:
        old = example["old_state"]
        self.cards.append(
            StateCard(
                id=f"{example['id']}:old",
                name=old["name"],
                value=old["value"],
                evidence=example["old_memory"],
            )
        )

    def add_new_state_and_adjudicate(self, example: dict) -> None:
        new = example["new_state"]
        new_card = StateCard(
            id=f"{example['id']}:new",
            name=new["name"],
            value=new["value"],
            evidence=example["new_observation"],
        )

        for card in self.cards:
            if card.status != ACTIVE:
                continue

            if self._same_dynamic_state(card.name, new_card.name):
                card.status = STALE
                card.related_states.append(new_card.name)
                continue

            if self._is_affected_by_new_state(card.name, example):
                card.status = UNKNOWN_CURRENT
                card.related_states.append(new_card.name)

        self.cards.append(new_card)

    def statuses(self) -> dict[str, str]:
        return {card.id: card.status for card in self.cards}

    @staticmethod
    def _same_dynamic_state(old_name: str, new_name: str) -> bool:
        return normalize(old_name) == normalize(new_name)

    @staticmethod
    def _is_affected_by_new_state(old_name: str, example: dict) -> bool:
        affected = {normalize(name) for name in example.get("affected_states", [])}
        return normalize(old_name) in affected


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("’", "'").split())


def load_examples(path: Path) -> Iterable[dict]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def expected_old_status(example: dict) -> str:
    if example["relation"] == "same_state":
        return STALE
    if example["relation"] == "propagated":
        return UNKNOWN_CURRENT
    return ACTIVE


def run() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = list(load_examples(root / "data" / "mini_stale.jsonl"))

    naive_correct = 0
    schema_free_correct = 0

    print("Schema-Free STALE Memory Starter")
    print("=" * 40)

    for example in examples:
        naive = NaiveMemory()
        old = example["old_state"]
        naive.add(
            StateCard(
                id=f"{example['id']}:old",
                name=old["name"],
                value=old["value"],
                evidence=example["old_memory"],
            )
        )
        naive.add(
            StateCard(
                id=f"{example['id']}:new",
                name=example["new_state"]["name"],
                value=example["new_state"]["value"],
                evidence=example["new_observation"],
            )
        )

        memory = SchemaFreeMemory()
        memory.add_old_state(example)
        memory.add_new_state_and_adjudicate(example)

        expected = expected_old_status(example)
        naive_old_status = naive.statuses()[f"{example['id']}:old"]
        memory_old_status = memory.statuses()[f"{example['id']}:old"]

        naive_hit = naive_old_status == expected
        memory_hit = memory_old_status == expected
        naive_correct += int(naive_hit)
        schema_free_correct += int(memory_hit)

        print(f"\n{example['id']} ({example['type']})")
        print(f"  expected old status:     {expected}")
        print(f"  naive old status:        {naive_old_status}")
        print(f"  schema-free old status:  {memory_old_status}")
        print(f"  hidden logic: {example['hidden_logic']}")

    total = len(examples)
    print("\nSummary")
    print("=" * 40)
    print(f"NaiveMemory:       {naive_correct}/{total}")
    print(f"SchemaFreeMemory:  {schema_free_correct}/{total}")


if __name__ == "__main__":
    run()

