# 01 Map an IUCN category

The mammal table publishes short codes: CR, EN, VU, NT, LC, DD, and sometimes EX.

Threatened means CR, EN, or VU. Not threatened means NT or LC. Data deficient is not a class in this model.

Implement these two functions in `starter.py`:

- `map_iucn_label(category) -> int | None`
- `drop_data_deficient(frame, category_col="iucn_category") -> DataFrame`

`map_iucn_label` returns 1, 0, or None. None means the category is not in the binary contrast. That includes DD, EX, EW, NE, and a blank cell.

`drop_data_deficient` removes rows whose category is DD and leaves every other row, including EX and blank categories. The service applies a second filter later so EX does not get a score. This function only drops DD.

Accept the codes in any case, and these full names: Critically Endangered, Endangered, Vulnerable, Near Threatened, Least Concern, Data Deficient. Treat `CR(PE)` and `CR(PEW)` as CR.

Do not call the Red List API. The category is already in the table.
