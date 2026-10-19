# Watchlist query

Postgres stores one row per species. `threat_score` is the probability from the gradient booster, written when the gateway starts. The watchlist route does not train a second model. It reads this query, then a short greedy pick in Python spreads those names across families (`src/cover.py`). The greedy step is not SQL: each species covers one family, and the pick walks the already-sorted scores.

`%(taxonomic_order)s` and `%(n)s` are bound parameters. `Carnivora` matches `CARNIVORA` because both sides are uppercased. Species with no score are left out. Ties break by scientific name so the order is stable.

```sql
SELECT
    scientific_name,
    taxonomic_order,
    family,
    genus,
    iucn_category,
    threatened_label,
    threat_score
FROM species
WHERE upper(taxonomic_order) = upper(%(taxonomic_order)s)
  AND threat_score IS NOT NULL
ORDER BY threat_score DESC, scientific_name ASC
LIMIT %(n)s
```

`threatened_label` is 1 for CR, EN, and VU, and 0 for NT and LC. EP, EX, EW, and DD are not loaded. Near Threatened is not the positive class.
