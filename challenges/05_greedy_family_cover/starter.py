# Complete the functions below. Do not change the signatures.
"""Starter for challenge 05. Replace the body; do not import the hidden solution."""

from __future__ import annotations


def greedy_family_cover(records, k: int) -> list:
    # The watchlist already has the highest scores in one order. A short pick
    # from that list should not be five species from the same family when other
    # families are also high.
    #
    # Each record has scientific_name, family, and score. Each species covers
    # only its family.
    #
    # Steps:
    # 1. Sort by score descending, then family, then scientific name.
    # 2. Take the highest-scoring species of each new family until you have k
    #    species or you run out of families.
    # 3. If you still need more names to reach k, fill with the next-highest
    #    species that were not picked.
    #
    # Edge cases:
    # - k = 0 returns an empty list.
    # - A negative k raises ValueError.
    # - If k is longer than the list, return every record in that greedy order.
    #
    # Return the picked records.
    raise NotImplementedError("Pick k species that cover as many families as possible.")
