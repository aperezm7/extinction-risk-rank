"""Train on a species CSV and print the family-holdout metrics. No download."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib

from services.data.parse import read_species_csv
from services.data.validate import validate_species_frame
from src.labels import normalize_iucn_category, rows_for_service
from src.pipeline import fit_and_score

# PHYLACINE codes that are not the CR/EN/VU versus NT/LC contrast.
EXCLUDED_FROM_TRAINING = frozenset({"EP", "EX", "EW", "DD"})


def train_species_table(frame, random_state: int = 0, test_size: float = 0.25):
    validate_species_frame(frame)
    served = rows_for_service(frame)
    codes = served["iucn_category"].map(normalize_iucn_category)
    leaked = sorted(set(codes.dropna()) & EXCLUDED_FROM_TRAINING)
    if leaked:
        raise RuntimeError(f"excluded categories reached training: {leaked}")
    scored, report, model = fit_and_score(served, random_state=random_state, test_size=test_size)
    return scored, report, model


def format_report(report: dict) -> str:
    return "\n".join(
        [
            (
                f"Family holdout (random_state={report['random_state']}, "
                f"test_size={report['test_size']})"
            ),
            f"  labeled species: {report['n_labeled']}",
            f"  train / test: {report['n_train']} / {report['n_test']}",
            f"  ROC AUC: {report['roc_auc']:.3f}",
            f"  precision in the top 10% of scores: {report['precision_top_10']:.3f}",
            f"Serving model refit on all labeled species and scored {report['n_scored']} rows.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the mammal trait booster on a local CSV.")
    parser.add_argument("--species", type=Path, required=True, help="Fixture or prepared species CSV")
    parser.add_argument("--model-out", type=Path, default=Path("artifacts/model.joblib"))
    parser.add_argument("--report-out", type=Path, default=Path("artifacts/metrics.json"))
    parser.add_argument("--random-state", type=int, default=0)
    args = parser.parse_args()
    frame = read_species_csv(args.species)
    _scored, report, model = train_species_table(frame, random_state=args.random_state)
    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, args.model_out)
    args.report_out.write_text(json.dumps(report, indent=2) + "\n")
    print(format_report(report))
    print(f"model: {args.model_out}")
    print(f"report: {args.report_out}")


if __name__ == "__main__":
    main()
