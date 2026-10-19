"""Pick a short list that covers as many families as possible."""

from __future__ import annotations


def greedy_family_cover(records, k: int) -> list:
    """Return up to k records, preferring a new family at each step.

    Each species covers only its own family, so the maximum number of
    families in a list of length k is min(k, number of families). The
    greedy rule takes the highest-scoring species of each new family
    first, then fills any remaining slots with the next-highest species.
    Sort order is score descending, then family, then scientific name.
    """
    if k < 0:
        raise ValueError("k must be >= 0")
    rows = list(records)
    for row in rows:
        if "family" not in row or "score" not in row or "scientific_name" not in row:
            raise KeyError("records need scientific_name, family, and score")
    ranked = sorted(
        rows,
        key=lambda row: (-float(row["score"]), str(row["family"]), str(row["scientific_name"])),
    )
    if k == 0:
        return []
    picked: list = []
    seen: set[str] = set()
    picked_ids: set[int] = set()
    for index, row in enumerate(ranked):
        family = str(row["family"])
        if family in seen:
            continue
        picked.append(row)
        seen.add(family)
        picked_ids.add(index)
        if len(picked) == k:
            return picked
    for index, row in enumerate(ranked):
        if index in picked_ids:
            continue
        picked.append(row)
        if len(picked) == k:
            break
    return picked
