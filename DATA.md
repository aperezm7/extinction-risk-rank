# Data

Faurby, S., Davis, M., Pedersen, R. Ø., Schowanek, S. D., Antonelli, A., and Svenning, J.-C. (2018). PHYLACINE 1.2: The Phylogenetic Atlas of Mammal Macroecology. Ecology. https://doi.org/10.1002/ecy.2443

Faurby, S., Pedersen, R. Ø., Davis, M., Schowanek, S. D., Jarvie, S., Antonelli, A., and Svenning, J.-C. (2020). PHYLACINE 1.2.1: An update to the Phylogenetic Atlas of Mammal Macroecology. https://doi.org/10.5281/zenodo.3690867

Trait file: https://github.com/MegaPast2Future/PHYLACINE_1.2/blob/master/Data/Traits/Trait_data.csv

The PHYLACINE repository states that this distribution is under a Creative Commons Zero license (CC0).

## What is downloaded

`python -m services.data.download` caches one file under `data/cache/` (gitignored):

| File | Role |
| --- | --- |
| `Trait_data.csv` | PHYLACINE 1.2.1 traits and `IUCN.Status.1.2` for 5,831 extant and recently extinct mammals. |

The download checks SHA-256 `ab035a8fab3d18673dea1d4a56f741e3ea9f8ba460461c7a1e738621ca315ec7`. A mismatch deletes the file and raises.

`python -m services.data.prepare` writes `data/cache/species.csv` with the columns this repo keeps. That file is the same table as `tests/fixtures/mammals.csv`.

## Label

Positive class is CR, EN, and VU. NT and LC are the negative class. Training drops:

| Code | Meaning in this table | Rows |
| --- | --- | --- |
| EP | Extinct prehistoric | 270 |
| EX | Extinct | 82 |
| EW | Extinct in the wild | 1 |
| DD | Data deficient | 777 |

That leaves 4,701 labeled species (CR 205, EN 464, VU 525, NT 350, LC 3,157). The family-grouped holdout is this set, not a smaller excerpt. `random_state=0`, `test_size=0.25`: 3,185 train and 1,516 test. ROC AUC is 0.749. Precision in the top 10 percent of the test scores is 0.803, which is 122 of k = 152. The serving model is refit on all 4,701 and scores those same 4,701 rows. EP, EX, EW, and DD are not scored.

`IUCN.Status.1.2` is the category. `Added.IUCN.Status.1.2` is not used.

## Columns used

| PHYLACINE column | Species table | Role |
| --- | --- | --- |
| `Binomial.1.2` | `scientific_name` | Underscores become a single space. |
| `Order.1.2` | `taxonomic_order` | Watchlist filter and a one-hot covariate. Published capitalization is kept (`Carnivora`). |
| `Family.1.2` | `family` | Group for the holdout and for the greedy watchlist pick. Not a model covariate. |
| `Genus.1.2` | `genus` | Stored for the species response. |
| `Mass.g` | `body_mass_g` | Natural log. Non-positive or missing masses stay missing. This file has no missing masses. |
| `Diet.Plant`, `Diet.Vertebrate`, `Diet.Invertebrate` | `diet_plant`, `diet_vertebrate`, `diet_invertebrate` | Percent of the diet. Each row sums to 100. `Diet.Method` and `Diet.Source` are not features. |
| `Terrestrial`, `Marine`, `Freshwater`, `Aerial` | same names | Binary life habit. `Life.Habit.Method` and `Life.Habit.Source` are not features. |
| `Island.Endemicity` | `island_endemicity` | Five published levels, one-hot encoded. |
| `IUCN.Status.1.2` | `iucn_category` | Label source. |

Order and island use fixed vocabularies from PHYLACINE 1.2.1 so the train and test matrices have the same columns. Histogram gradient boosting in scikit-learn 1.9.1 is fit on that numeric matrix. Family is held out with `GroupShuffleSplit`, so a family indicator would be an unseen level on every test species and would also memorize family threat rates in the training families.

Litopterna and Notoungulata have only EP species in this file, so they do not appear in the scored table.

No Red List API calls are made.
