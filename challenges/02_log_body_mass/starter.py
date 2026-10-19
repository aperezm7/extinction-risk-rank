# Complete the functions below. Do not change the signatures.
"""Starter for challenge 02. Replace the body; do not import the hidden solution."""

from __future__ import annotations

import pandas as pd


def log_body_mass(body_mass) -> pd.Series:
    # Body mass in this table is in grams and is right-skewed. The model uses
    # the natural log.
    #
    # Steps:
    # - Take the natural log of each mass. log(e) == 1, which is what the
    #   source R script's log() does.
    # - Name the result log_body_mass and keep the input index.
    #
    # Edge cases:
    # - A missing mass stays missing. Do not fill it with zero, one, or a mean.
    # - A non-positive mass stays missing, because the log is undefined.
    #
    # Return that Series.
    raise NotImplementedError("Log-transform body mass and leave missing values missing.")
