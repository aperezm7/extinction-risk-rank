"""Column order shared by the fixture, the prepared table, and Postgres."""

SPECIES_COLUMNS = (
    "scientific_name",
    "taxonomic_order",
    "family",
    "genus",
    "iucn_category",
    "body_mass_g",
    "diet_plant",
    "diet_vertebrate",
    "diet_invertebrate",
    "terrestrial",
    "marine",
    "freshwater",
    "aerial",
    "island_endemicity",
)

ID_COLUMNS = (
    "scientific_name",
    "taxonomic_order",
    "family",
    "genus",
    "iucn_category",
    "island_endemicity",
)
