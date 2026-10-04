# Quality Audit — Power Supply Analytics 0.2.0

This audit records the checks applied to the current repository baseline before packaging.

## Documentation

- Every project Python module has a module docstring.
- Every project function, method, nested helper, and class has a docstring.
- Engineering comments are retained around numerical transformations, operating-state decisions, acquisition timing, hardware/file operations, GUI orchestration, and report-generation logic.
- `FUNCTION_LIBRARY_MAP.md` is generated directly from the source tree and now includes the GUI/configuration modules.
- The desktop GUI remains an orchestration layer; diagnostic equations and spectral calculations stay in their established engineering modules.

## Deprecated API review

The source tree is checked for common retired/deprecated interfaces including legacy NumPy scalar aliases, legacy trapezoid integration calls, `datetime.utcnow()`, pandas append APIs, `distutils`, `pkg_resources`, and older Matplotlib colormap access patterns. The current code uses supported equivalents.

The spectral integration path uses `scipy.integrate.trapezoid`.

## Regression and syntax checks

The regression suite is executed with `DeprecationWarning` promoted to an error through `pyproject.toml`.

Validation commands:

```bash
python -m py_compile power_supply_analytics_gui.py psa_gui_config.py
python -W error::DeprecationWarning -m pytest -q
```

The 0.2.0 build passes **19 regression tests**, including configuration checks for B400A, L1127, S01-S40, Cab_1-Cab_5, and the eight-address `192.168.1.2` through `192.168.8.2` pool.

## GUI runtime qualification

The GUI implementation is based on PySide6 and uses `QProcess` so long-running acquisition/analysis modules do not block the desktop event loop. The build environment used for this repository package did not contain PySide6 and had no package-network access, so the Qt window itself was not interactively launched in this environment. GUI-independent configuration and command-generation logic is isolated in `psa_gui_config.py` and covered by regression tests.

A field workstation should complete the following smoke check after installing `.[gui]`:

1. launch `power-supply-analytics`;
2. verify Storage Ring and Test Stand selector dependencies;
3. validate one dry configuration for B400A and one for L1127;
4. run a short live-monitor acquisition against a known test supply;
5. confirm stdout/stderr streams into the GUI and Stop terminates the child process cleanly.

## Change-control rule

Any future change to a numerical result, CSV field, result dictionary, fault decoding, spectral band definition, GUI-to-CLI argument mapping, or AI-facing exported schema should update the relevant regression test and the AI data contract when applicable.
