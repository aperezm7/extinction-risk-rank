"""Hidden solution for challenge 02. Mirrors src.features.log_body_mass."""

from __future__ import annotations

import numpy as np
import pandas as pd


def log_body_mass(body_mass) -> pd.Series:
    values = pd.to_numeric(pd.Series(body_mass, copy=True), errors="coerce")
    return pd.Series(np.log(values.where(values > 0)), index=values.index, name="log_body_mass")
