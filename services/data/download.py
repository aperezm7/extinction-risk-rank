"""Download the PHYLACINE 1.2.1 trait table and check its checksum."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

PHYLACINE_DOI = "10.5281/zenodo.3690867"
TRAIT_URL = (
    "https://raw.githubusercontent.com/MegaPast2Future/PHYLACINE_1.2/"
    "master/Data/Traits/Trait_data.csv"
)
TRAIT_FILENAME = "Trait_data.csv"
# SHA-256 of Trait_data.csv retrieved for this repo from TRAIT_URL.
TRAIT_SHA256 = "ab035a8fab3d18673dea1d4a56f741e3ea9f8ba460461c7a1e738621ca315ec7"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(cache_dir: Path, timeout: int = 120) -> Path:
    """Cache Trait_data.csv. Skip the download when the SHA-256 already matches."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    destination = cache_dir / TRAIT_FILENAME
    if destination.exists() and file_sha256(destination) == TRAIT_SHA256:
        return destination
    request = urllib.request.Request(TRAIT_URL, headers={"User-Agent": "extinction-risk-rank"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        destination.write_bytes(response.read())
    checksum = file_sha256(destination)
    if checksum != TRAIT_SHA256:
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"{TRAIT_FILENAME} sha256 {checksum} != {TRAIT_SHA256}")
    return destination


def main() -> None:
    path = download(Path("data/cache"))
    print(f"{path.name}: {path} sha256={file_sha256(path)}")


if __name__ == "__main__":
    main()
