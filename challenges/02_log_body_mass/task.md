# 02 Log-transform body mass

Body mass in this table is in grams and is right-skewed. The model uses the natural log.

Implement `log_body_mass(body_mass) -> Series` in `starter.py`.

- The result is named `log_body_mass` and keeps the input index.
- A missing mass stays missing. Do not fill it with zero, one, or a mean.
- A non-positive mass stays missing, because the log is undefined.
- Use the natural log (`log(e) == 1`), which is what the source R script's `log()` does.
