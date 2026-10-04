# Contributing

Changes to Power Supply Analytics should preserve engineering traceability.

Before submitting a change:

1. Document every new or modified function with a docstring.
2. Comment non-obvious engineering decisions, unit conversions, timing assumptions, and hardware/file operations.
3. Update `docs/FUNCTION_LIBRARY_MAP.md` when function dependencies change.
4. Add or update a regression test for changed math or data contracts.
5. Run `python -m pytest -q` with deprecation warnings treated as errors.
6. Keep measured values, calculated values, engineering estimates, specifications, and future AI predictions explicitly distinguishable.

A change that makes a plot prettier but makes the data lineage harder to explain is not an improvement.
