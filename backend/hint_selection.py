"""Select an approved level-1 hint for a matched misconception (ticket #33, 2nd MVP).

Given a misconception_id (or None), picks one approved hint from the hints table -
falling back to the existing generic hint (#34, 1st MVP) whenever there's no id, or no
approved hint exists for it yet. Randomizes among multiple matches (not the first one
found) since #70's own story explicitly wants variety: "not the exact same sentence
every time the same mistake happens."

Honest, current state: hints has 0 rows until #70's drafted batch
(docs/architecture/hint_variants_bootstrap_batch_1.md) is approved and seeded - so this
always falls back to the generic hint for now. The code is real and ready; the content
just isn't approved yet - same state misconception_matching.py was in before #9 was
seeded.
"""
import random

from db import get_client
from generic_hint import get_generic_hint

_LEVEL_1 = 1


def select_hint(misconception_id: str | None) -> str:
    """Return hint text for misconception_id, or the generic fallback.

    Only ever selects level-1 hints - level-2 (escalated) hints come exclusively from
    #72's live path, never this static pool (Overview tab's Decision C).
    """
    if misconception_id is None:
        return get_generic_hint()

    client = get_client()
    rows = (
        client.table("hints")
        .select("*")
        .eq("misconception_id", misconception_id)
        .eq("level", _LEVEL_1)
        .execute()
        .data
    )
    if not rows:
        return get_generic_hint()

    return random.choice(rows)["text"]
