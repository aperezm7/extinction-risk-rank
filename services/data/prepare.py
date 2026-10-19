"""Build the species table from the cached PHYLACINE trait file."""

from __future__ import annotations

from pathlib import Path

from services.data.parse import read_phylacine_traits
from services.data.validate import validate_species_frame


def build_species_table(trait_csv: Path):
    frame = read_phylacine_traits(trait_csv)
    validate_species_frame(frame)
    return frame


def main() -> None:
    trait_csv = Path("data/cache/Trait_data.csv")
    if not trait_csv.exists():
        raise SystemExit("missing cache. Run: python -m services.data.download")
    frame = build_species_table(trait_csv)
    destination = Path("data/cache/species.csv")
    frame.to_csv(destination, index=False)
    labeled = frame["iucn_category"].isin(["CR", "EN", "VU", "NT", "LC"]).sum()
    print(f"wrote {destination} rows={len(frame)} binary_label={int(labeled)}")


if __name__ == "__main__":
    main()
