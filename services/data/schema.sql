-- Species trait table loaded by the gateway.
-- threat_score is written by the gradient booster after training.
-- The watchlist query reads that column. It does not fit a model.

CREATE TABLE IF NOT EXISTS species (
    scientific_name TEXT PRIMARY KEY,
    taxonomic_order TEXT NOT NULL,
    family TEXT NOT NULL,
    genus TEXT,
    iucn_category TEXT,
    threatened_label INTEGER,
    body_mass_g DOUBLE PRECISION,
    diet_plant DOUBLE PRECISION,
    diet_vertebrate DOUBLE PRECISION,
    diet_invertebrate DOUBLE PRECISION,
    terrestrial DOUBLE PRECISION,
    marine DOUBLE PRECISION,
    freshwater DOUBLE PRECISION,
    aerial DOUBLE PRECISION,
    island_endemicity TEXT,
    threat_score DOUBLE PRECISION,
    CONSTRAINT species_label_chk CHECK (
        threatened_label IS NULL OR threatened_label IN (0, 1)
    )
);

CREATE INDEX IF NOT EXISTS species_order_score_idx
    ON species (taxonomic_order, threat_score DESC);

CREATE TABLE IF NOT EXISTS training_report (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    roc_auc DOUBLE PRECISION,
    precision_top_10 DOUBLE PRECISION,
    n_labeled INTEGER NOT NULL,
    n_train INTEGER NOT NULL,
    n_test INTEGER NOT NULL,
    n_scored INTEGER NOT NULL,
    random_state INTEGER NOT NULL,
    positive_rate DOUBLE PRECISION NOT NULL
);
