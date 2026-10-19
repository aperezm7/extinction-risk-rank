# 05 Greedy family cover

The watchlist already has the highest scores in one order. A short pick from that list should not be five species from the same family when other families are also high.

Implement `greedy_family_cover(records, k) -> list`.

Each record has `scientific_name`, `family`, and `score`. Each species covers only its family.

1. Sort by score descending, then family, then scientific name.
2. Take the highest-scoring species of each new family until you have `k` species or you run out of families.
3. If you still need more names to reach `k`, fill with the next-highest species that were not picked.

`k = 0` returns an empty list. A negative `k` raises `ValueError`. If `k` is longer than the list, return every record in that greedy order.
