# Architecture and Change-Control Notes

Power Supply Analytics separates acquisition, deterministic calculations, spectral analysis, metadata, and presentation so each layer can be tested and reused independently.

## Data flow

```text
CDCU Ethernet / PMM / External Oscilloscope
                    |
                    v
             Acquisition layer
                    |
                    v
         Normalized engineering data
                    |
          +---------+----------+
          |                    |
          v                    v
  Deterministic diagnostics   Spectral/stability analysis
          |                    |
          +---------+----------+
                    |
                    v
             Correlated results
                    |
          +---------+----------+
          |                    |
          v                    v
       Reports/plots       Future AI dataset
```

## Design rule: measured versus inferred

The repository distinguishes four categories:

1. **Measured** — telemetry or waveform values delivered by hardware.
2. **Calculated** — direct math from measured values, such as `P = VI`.
3. **Estimated** — engineering estimates with assumptions, such as inductance from sequential telemetry.
4. **Reference/specification** — manufacturer limits, model ratings, or configured load-map values.

Future AI output is a fifth category and must remain explicitly labeled as **predicted/inferred by model**.

## Module boundaries

- Acquisition modules own communication timing and raw-data validity.
- Diagnostic modules own deterministic engineering calculations.
- Spectral modules own FFT/PSD math and sampling validation.
- Reporting modules consume completed result dictionaries; they should not redefine engineering calculations.
- Metadata/load-map modules resolve context but should not fabricate missing measurements.

## Change-impact workflow

Before changing a function:

1. Locate it in `FUNCTION_LIBRARY_MAP.md`.
2. Review its local callers and local callees.
3. Review external libraries used by the function's module.
4. Run the targeted test and the full regression suite.
5. If a result schema changes, update the AI data contract and any report reader in the same change.

## Public baseline

This repository intentionally starts at `0.1.0`. Historical internal toolkit revision numbers are not part of the public API or documentation.

## GUI orchestration layer (0.2.0)

The desktop GUI is not an analysis engine. It is an operator interface over the same command-line modules used for engineering and automated workflows.

```text
Operator
   |
   v
power_supply_analytics_gui.py       presentation, validation, process control
   |
   v
psa_gui_config.py                   configuration model + command construction
   |
   +--> cdcu_monitor.py             live acquisition / PMM / diagnostics / reports
   +--> cdcu_pmm_fft.py             saved PMM spectral analysis
   +--> cdcu_dcbus_fft.py           standardized external DCBus analysis
   +--> cdcu_scope_fft.py           generic external-scope analysis
```

This boundary is deliberate. A GUI update must not change diagnostic math. A diagnostic-library update must remain testable without Qt. The future AI-facing application can therefore reuse the deterministic acquisition and feature layers without inheriting desktop GUI dependencies.

The GUI configuration is stored in `power_supply_analytics_config.json`. The current operational map contains:

- Storage Ring: S01-S40, Cab_1-Cab_5
- B400A: Test_1, Test_2, Test_bench
- L1127: Test_bench
- Test-network addresses: 192.168.1.2 through 192.168.8.2
