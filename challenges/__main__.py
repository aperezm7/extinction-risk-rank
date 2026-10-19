"""Print a hidden solution and a short explanation.

    python -m challenges reveal 03
"""

from __future__ import annotations

import argparse
from pathlib import Path

from challenges.loader import SLUGS

EXPLANATIONS = {
    "01": (
        "CR, EN, and VU are the threatened categories. NT and LC are not. "
        "DD has no label, so those rows leave the training table. "
        "EX and EW are not part of the contrast either: map_iucn_label returns None, "
        "while drop_data_deficient removes only DD."
    ),
    "02": (
        "Body mass enters the model as a natural log, the same log() the source "
        "R script applies when log_rules marks BODY_SIZE. A missing mass stays "
        "missing. Filling it with zero or a mean would invent a measurement."
    ),
    "03": (
        "A random row split can put two murids on opposite sides, so the test "
        "score is partly a prediction for a species the model has already seen "
        "a close relative of. GroupShuffleSplit keeps each family entirely in "
        "train or entirely in test. That is the same dependence the paper "
        "modeled with a family random effect. The holdout is noisy: only 55 "
        "mammals in this deposit have a raw IUCN category, and many families "
        "have a single species."
    ),
    "04": (
        "ROC AUC treats every threshold equally. The watchlist does not: it "
        "shows the top of the score list. Precision in the top 10 percent is "
        "the fraction of those names whose published category is threatened. "
        "The cutoff is k = max(1, ceil(n * 0.1)), with ties keeping the earlier row."
    ),
    "05": (
        "Each species covers one family. The longest family list you can make "
        "with k names is min(k, number of families). Walking the scores from "
        "high to low and taking a species only when its family is new hits that "
        "maximum, and it prefers the higher score inside each family. If k is "
        "larger than the number of families, the leftover slots go to the "
        "next-highest species even if the family is already represented."
    ),
}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m challenges")
    sub = parser.add_subparsers(dest="command", required=True)
    reveal = sub.add_parser("reveal", help="Print one hidden solution and a short explanation")
    reveal.add_argument("number", help="Challenge number, for example 03")
    args = parser.parse_args(argv)
    number = args.number.zfill(2)
    if number not in SLUGS:
        known = ", ".join(SLUGS)
        raise SystemExit(f"unknown challenge {args.number!r}. Known: {known}")
    path = Path(__file__).resolve().parent / "hidden" / f"{SLUGS[number]}.py"
    print(path.read_text())
    print(EXPLANATIONS[number])


if __name__ == "__main__":
    main()
