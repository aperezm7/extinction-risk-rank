"""SQL the gateway runs. The annotated copy is learn/sql.md."""

WATCHLIST_SQL = """
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
""".strip()

ORDER_EXISTS_SQL = """
SELECT taxonomic_order
FROM species
WHERE upper(taxonomic_order) = upper(%(taxonomic_order)s)
LIMIT 1
""".strip()

SPECIES_SQL = """
SELECT
    scientific_name,
    taxonomic_order,
    family,
    genus,
    iucn_category,
    threatened_label,
    body_mass_g,
    diet_plant,
    diet_vertebrate,
    diet_invertebrate,
    terrestrial,
    marine,
    freshwater,
    aerial,
    island_endemicity,
    threat_score
FROM species
WHERE lower(scientific_name) = lower(%(name)s)
""".strip()

METRICS_SQL = """
SELECT
    roc_auc,
    precision_top_10,
    n_labeled,
    n_train,
    n_test,
    n_scored,
    random_state,
    positive_rate
FROM training_report
WHERE id = 1
""".strip()
