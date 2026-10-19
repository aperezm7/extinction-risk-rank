"""Hidden solution for challenge 05. Mirrors src.cover."""

from __future__ import annotations


def greedy_family_cover(records, k: int) -> list:
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
