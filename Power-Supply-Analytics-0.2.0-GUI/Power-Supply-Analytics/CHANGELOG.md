# Changelog

## 0.1.0 — Initial public baseline

- Established the public project name **Power Supply Analytics**.
- Removed internal toolkit revision history from public-facing documentation.
- Changed FFT callouts to the two strongest components in each troubleshooting band through 1 kHz.
- Preserved the standard 720–1200 Hz PSD integration band while capping its visualization callout band at 1 kHz.
- Added complete function/class docstring coverage across production code, tests, and repository tools.
- Added a generated function/library dependency map for engineering change-impact review.
- Added architecture, spectral-analysis, and planned AI data-contract documentation.
- Added modern `pyproject.toml` packaging/dependency metadata and explicit pytest deprecation handling.
- Added regression coverage for per-band FFT callout ranking and the 1 kHz integration band.
- Retained the established live-monitor, PMM, DCBus, oscilloscope, diagnostics, magnet-load, register-decoding, and reporting workflows.

## 0.2.0 - GUI orchestration

- Added the first PySide6 desktop launcher for Power Supply Analytics.
- Added separate **Storage Ring** and **Test Stand** target modes.
- Storage Ring selectors cover S01-S40 and Cab_1-Cab_5.
- Test Stand configuration now maps B400A to Test_1, Test_2, and Test_bench, and maps L1127 to Test_bench.
- Expanded the selectable CDCU IP pool through 192.168.8.2 so ports 7 and 8 can be used when another test-network port is unavailable.
- Added transparent command preview, pre-run validation, live console output, Run, and Stop controls.
- Added GUI launch paths for the live monitor, PMM FFT/PSD, DCBus FFT/PSD/stability, and generic external-scope FFT/PSD/stability workflows.
- Kept engineering calculations in their existing modules; the GUI only validates, translates, and orchestrates the established command-line interfaces.
- Added regression tests for location/station mapping, sector/cabinet ranges, spare IP ports, and monitor command generation.
