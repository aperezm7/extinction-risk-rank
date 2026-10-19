# Why this stays Python

PHYLACINE 1.2.1 publishes the trait table as a CSV. The ranking service is a family-grouped gradient booster, two HTTP routes, and a Postgres table of stored scores. Those pieces stay in one Python process: `HistGradientBoostingClassifier` scores the species, `GroupShuffleSplit` holds out whole families, `psycopg` reads the watchlist, and `pytest` checks the five challenges. The service does not call the IUCN Red List API.

An earlier draft of this repo used a Figshare workbook whose raw IUCN column covered 60 mammals. That deposit's R script fits binomial GLMMs with `glmmTMB` and pools slopes with `metafor`. This service does not reimplement that meta-analysis. The label and the holdout now come from `IUCN.Status.1.2` on the PHYLACINE trait table.
