# 03 Family-grouped split

Related species share a family, and the paper's models gave each family its own intercept. A row-wise split leaks that dependence into the test score.

Implement `family_grouped_split(frame, group_col="family", test_size=0.2, random_state=0)` in `starter.py`.

Return `(train, test)` as copies.

- No family appears on both sides.
- Every input row appears on exactly one side.
- Both sides are non-empty.
- Raise `ValueError` if the frame has fewer than two families.
- Use `sklearn.model_selection.GroupShuffleSplit` so the seed is reproducible.
