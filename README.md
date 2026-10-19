# Extinction risk rank

Which mammal species look high priority from traits, relative to their published IUCN status?

A gradient booster scores species from PHYLACINE 1.2.1 traits: log body mass, diet composition, life habit, island endemicity, and order. Family is the holdout group, not a covariate. The label is `IUCN.Status.1.2`: threatened (CR, EN, VU) against not threatened (NT, LC). EP, EX, EW, and DD are dropped before training. The score is not a Red List category and not a substitute for an IUCN assessment.

The booster is fit once, on a family holdout of that full labeled set, and the serving scores come from a refit on every labeled species. `GET /watchlist` does not train another model. It reads stored scores for one order and then makes a short greedy pick that spreads those names across families.

## Data

Faurby et al. (2018), PHYLACINE 1.2, Ecology, [10.1002/ecy.2443](https://doi.org/10.1002/ecy.2443), and the 1.2.1 update, [10.5281/zenodo.3690867](https://doi.org/10.5281/zenodo.3690867). The trait file is `Data/Traits/Trait_data.csv`. The project README licenses that distribution CC0.

Details of columns, the dropped statuses, and what is committed are in [DATA.md](DATA.md). The table has 5,831 species. After dropping EP (270), EX (82), EW (1), and DD (777), 4,701 species have a binary label (1,194 threatened).

The family split keeps every family entirely in train or entirely in test. The reported split is `random_state=0` and `test_size=0.25`, fixed before looking at the score. On the 4,701 labeled species that split is 3,185 train and 1,516 test. ROC AUC is 0.749. Precision in the top 10 percent of those 1,516 scores is 0.803 (122 of 152). Both numbers describe that one split of the full labeled set. They are not the metrics of a smaller fixture. Serving scores are a refit on all 4,701 labeled species, so a species that was in the test fold is not scored out of sample by the model the API returns.

## Run

From this directory, with Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m services.model.train --species tests/fixtures/mammals.csv
```

`pytest` runs the challenge tests against the hidden solutions and trains on the committed PHYLACINE extract. It does not download the trait file. Set `DATABASE_URL` to a Postgres URL to include the SQL test. Set `CHALLENGE_USE_HIDDEN=0` if you want the starters, which raise `NotImplementedError` until you implement them.

Docker Compose serves that same table. Postgres holds the species rows. The gateway trains on startup, writes scores, and listens on port 8091.

```bash
docker compose up --build
```

In another shell:

```bash
curl -s http://127.0.0.1:8091/species/Varecia%20rubra
curl -s "http://127.0.0.1:8091/watchlist?order=Carnivora&n=20"
curl -s http://127.0.0.1:8091/metrics
```

`Varecia rubra` is published as CR. The watchlist returns the 20 highest scores in Carnivora and a greedy pick of 5 names from different families. `k` defaults to `min(5, n)`. `/metrics` is the family holdout on the 4,701 labeled species.

Regenerate the extract from the upstream CSV, which uses the network once:

```bash
python -m services.data.download
python -m services.data.prepare
python -m services.model.train --species data/cache/species.csv
```

`tests/fixtures/mammals.csv` is that prepared table. Replacing it changes the committed training data.

## API

| Method | Path | What it returns |
| --- | --- | --- |
| GET | `/species/{name}` | Published category, binary label, traits, and threat score. Spaces or underscores in the name both work. |
| GET | `/watchlist?order=Carnivora&n=20` | Highest stored scores in that order, plus `greedy_pick`. |
| GET | `/metrics` | Family-holdout ROC AUC and top-decile precision on the full labeled set. |
| GET | `/health` | `{"status": "ok"}` |

Unknown species and unknown orders are 404. EP, EX, EW, and DD names are 404. `k` larger than `n` is 422.

## Challenges

Starters are in `challenges/NN_slug/starter.py`. Public tests are `test_challenge.py`. Hidden solutions are in `challenges/hidden/` and match `src/`.

```bash
python -m challenges reveal 03
```

| # | Directory | Task |
| --- | --- | --- |
| 01 | [challenges/01_iucn_label](challenges/01_iucn_label/task.md) | Map a category to 0/1 and drop DD. |
| 02 | [challenges/02_log_body_mass](challenges/02_log_body_mass/task.md) | Log body mass. Leave missing values missing. |
| 03 | [challenges/03_family_split](challenges/03_family_split/task.md) | Split so no family is on both sides. |
| 04 | [challenges/04_top_decile_precision](challenges/04_top_decile_precision/task.md) | Precision in the top 10 percent of scores. |
| 05 | [challenges/05_greedy_family_cover](challenges/05_greedy_family_cover/task.md) | Pick k species covering as many families as possible. |

## Layout

```text
services/gateway     FastAPI. Only public entrypoint.
services/data        download, cache, validate
services/features    domain transforms
services/model       train and infer
src/                 functions the services import
challenges/          starters, tests, hidden solutions
learn/why-python.md  why the ranking service stays Python
learn/sql.md         annotated watchlist query
tests/               service tests on the committed PHYLACINE extract
```
