# 04 Precision in the top 10 percent of scores

The watchlist is the top of the score list, not a threshold of 0.5. Precision there is the fraction of those species whose published label is threatened.

Implement `precision_at_top_fraction(y_true, y_score, fraction=0.1) -> float`.

- Let `n` be the number of rows and `k = max(1, ceil(n * fraction))`.
- Take the `k` highest scores. Ties keep the earlier row (stable sort).
- Return the mean of `y_true` on those rows.
- Raise `ValueError` on an empty input, a bad fraction, unequal lengths, or a NaN score.
