# Complete the functions below. Do not change the signatures.
"""Starter for challenge 01. Replace the bodies; do not import the hidden solution."""

from __future__ import annotations

import pandas as pd


def map_iucn_label(category) -> int | None:
    # The mammal table publishes short codes: CR, EN, VU, NT, LC, DD, and sometimes EX.
    # Threatened means CR, EN, or VU. Not threatened means NT or LC.
    # Data deficient is not a class in this model.
    #
    # Return 1 for threatened, 0 for not threatened, or None when the category
    # is not in the binary contrast. None includes DD, EX, EW, NE, and a blank cell.
    #
    # Accept the codes in any case, and these full names: Critically Endangered,
    # Endangered, Vulnerable, Near Threatened, Least Concern, Data Deficient.
    # Treat CR(PE) and CR(PEW) as CR.
    #
    # Do not call the Red List API. The category is already in the table.
    raise NotImplementedError("Map CR/EN/VU to 1, NT/LC to 0, and return None for DD.")


def drop_data_deficient(frame: pd.DataFrame, category_col: str = "iucn_category") -> pd.DataFrame:
    # Remove rows whose category is DD and leave every other row, including EX
    # and blank categories. The service applies a second filter later so EX does
    # not get a score. This function only drops DD.
    #
    # Accept the code in any case, and the full name Data Deficient.
    #
    # Return the filtered DataFrame.
    raise NotImplementedError("Drop rows whose IUCN category is DD.")
