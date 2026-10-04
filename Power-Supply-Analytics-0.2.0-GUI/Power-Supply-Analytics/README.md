# Power Supply Analytics

Power Supply Analytics is an engineering diagnostic and data-analysis framework for precision power converters. The current implementation is built around CAENels CDCU-100, CDCU-200, and CDCU-300 systems, but the architecture is intentionally modular so the analysis layer can grow beyond one manufacturer or one power-supply family.

I built this tool to do more than collect plots. The intent is to turn raw power-supply measurements into traceable engineering information: operating state, power flow, efficiency, fault context, magnet-load behavior, ripple, spectral content, temperature, and eventually machine-readable correlated datasets for predictive fault analysis.

This repository is the **initial public baseline**. Internal development revision numbers are intentionally removed from the public-facing project. The repository version starts at **0.1.0**. The current release is **0.2.0**, which adds the first desktop orchestration GUI.

## Engineering principles

The project follows a few rules that matter to me as a power-supply engineer:

- Preserve measured data. Do not replace invalid telemetry with fabricated zeros.
- Keep measured, calculated, inferred, and manufacturer-specified values clearly separated.
- Do not use asynchronous Ethernet polling as if it were a hardware-timed waveform acquisition.
- Keep FFT/PSD math traceable and numerically testable.
- Use one source of truth for common frequency bands and model specifications.
- Make fault records useful after the event, not just while the power supply is still connected.
- Keep analysis modules reusable so a future AI pipeline can consume the same validated calculations without carrying the live GUI and report-generation overhead.
- Prefer explicit engineering logic over hidden heuristics.

## Current capabilities

### Live CDCU monitoring

`cdcu_monitor.py` acquires and correlates CDCU telemetry over Ethernet. The monitor supports single-unit and parallel multi-IP operation.

Core signals include:

- `MRP` — DC bus voltage
- `MGPC` — DC bus input current
- `MRV` — output voltage
- `MRI` — output current
- `MRT`, `MRT:1..4` — internal temperatures
- fault/status registers
- serial number, firmware, slew-rate, and selected configuration information

The live plot remains **dynamic**. Steady-state qualification is used only where a calculation requires it; it does not replace the displayed telemetry with steady-state averages.

The monitor also identifies magnet-cycling/transient intervals so the dynamic response can be interpreted in context.

### Power and efficiency diagnostics

The diagnostic layer calculates:

\[
P_{in}=|V_{bus}I_{bus}|
\]

\[
P_{out}=|V_{out}I_{out}|
\]

\[
\eta=\frac{P_{out}}{P_{in}}\times100\%
\]

It also supports expected DCBus current, measured-versus-expected current error, efficiency-reference provenance, load qualification, CAEN full-load efficiency checks, power-loss estimates, and confidence/state reporting.

### Magnet-load characterization

The load-analysis layer uses known magnet resistance and inductance where available and compares them with measured behavior. It supports:

- steady-state resistance estimates
- nameplate-versus-measured resistance error
- dynamic inductance estimates
- IR drop and resistive power at a selected current
- positive slew-rate headroom estimates
- steady-state DCBus operating point and converter efficiency

Dynamic inductance derived from Ethernet telemetry is treated as an engineering trend estimate because the individual network reads are sequential, not simultaneous.

### PMM acquisition and FFT/PSD

The CDCU Post-Mortem Monitor is the authoritative high-speed internal waveform source used by this project. PMM analysis supports the CDCU hardware-timed record and generates FFT, Welch PSD, integrated RMS, frequency-band results, significant components, and report artifacts.

The Set Current spectral page is intentionally not used as the primary third spectral product. The project is being expanded around independently acquired DCBus and oscilloscope measurements instead.

### Frequency-band callouts

FFT plots call out the **two strongest components in each troubleshooting band through 1 kHz**:

- 1–10 Hz: top two components
- 60–120 Hz: top two components
- 360–720 Hz: top two components
- 720–1000 Hz: top two components

The underlying standard PSD integration band remains 720–1200 Hz so the 1 kHz region remains inside the integration band. Callout selection and integrated band calculations are intentionally separate.

### External oscilloscope analysis

`cdcu_scope_fft.py` analyzes hardware-timed oscilloscope CSV files with up to four channels. Each selected channel can produce:

- FFT
- Welch PSD
- cumulative integrated RMS
- dominant spectral components
- frequency-band results
- record-stability statistics

`cdcu_dcbus_fft.py` is the specialized two-channel DCBus path for input voltage and input current. It enforces a strict 100,001-sample, 10 kHz, 10-second record when that standardized acquisition mode is used.

The external scope path is the intended home for future DCBus spectral work. It is not built from repeated `MRP` or `MGPC` Ethernet reads.

### Record stability

The scope analysis can report:

- mean and median
- minimum and maximum
- peak-to-peak excursion
- standard deviation
- AC RMS
- maximum deviation
- percent and ppm relative to an explicit reference
- linear drift across the acquired record

These values describe the acquired record. They are not presented as CAEN 24-hour or 7-day stability unless the acquisition itself meets those test conditions.

### Fault capture and reporting

The monitor supports startup, fault-triggered, and final PMM capture. Fault registers are decoded into readable event summaries so the original fault state is retained rather than reduced to a generic pass/fail result.

### Reporting

The toolkit can generate CSV, PNG, PDF, and technical worksheet outputs. The reporting layer is kept separate from core calculations so analysis code can later be reused by a headless predictive-fault pipeline.

## Architecture

The current repository is intentionally organized as flat Python modules because the live monitor and existing command-line workflows are already field-oriented around these entry points. The module boundaries are still treated as libraries:

| Module | Primary responsibility |
| --- | --- |
| `cdcu_monitor.py` | Live acquisition, orchestration, multi-IP monitoring, CSV output |
| `cdcu_diagnostics.py` | Power, efficiency, load qualification, diagnostic state |
| `cdcu_pmm.py` | CDCU PMM acquisition |
| `cdcu_pmm_fft.py` | PMM spectral orchestration |
| `cdcu_ripple_psd.py` | FFT, Welch PSD, integration, plots, spectral math |
| `cdcu_ripple_bands.py` | Shared analysis and callout frequency bands |
| `cdcu_scope_fft.py` | Generic 1–4 channel external-scope analysis |
| `cdcu_dcbus_fft.py` | Strict DCBus V/I external-capture analysis |
| `cdcu_registers.py` | CDCU status/fault-register decoding |
| `cdcu_load_map.py` | IP/serial/magnet/load metadata lookup |
| `magnet_load_diagnostics.py` | R/L and magnet-load calculations |
| `cdcu_ripple_pdf.py` | PDF and worksheet reporting |
| `cdcu_ripple_io.py` | Spectral CSV metadata and file I/O |
| `one_liners.py` | Convenience launcher and mapped-host orchestration |

See `docs/FUNCTION_LIBRARY_MAP.md` for function-level dependencies and change impact.


## Desktop GUI

Power Supply Analytics 0.2.0 adds a PySide6 desktop launcher. The GUI is intentionally a thin orchestration layer over the existing Python modules; it does not duplicate power-supply equations, FFT/PSD math, fault decoding, or calibration logic.

Install the GUI dependency:

```powershell
python -m pip install -e ".[gui]"
```

Launch it with either:

```powershell
power-supply-analytics
```

or:

```powershell
python power_supply_analytics_gui.py
```

The target selectors support two operating contexts:

| Target mode | Selection model |
| --- | --- |
| Storage Ring | Sector S01-S40 + Cabinet Cab_1-Cab_5 |
| Test Stand | B400A: Test_1, Test_2, Test_bench; L1127: Test_bench |

The selectable CDCU test-network pool is `192.168.1.2` through `192.168.8.2`. Ports 7 and 8 are available as spare selections when another port cannot be used. Multiple addresses can be selected for the existing parallel-monitor workflow.

The GUI provides command preview and validation before execution. That preview is intentional: an engineer can see the exact Python module and arguments that will run instead of relying on hidden GUI behavior. Stdout/stderr from the launched module is streamed into the live console.

The first GUI release can launch:

- Live Monitor / multi-IP monitor
- PMM FFT / PSD
- DCBus FFT / PSD / record stability
- Generic 1-4 channel oscilloscope FFT / PSD / record stability

Operational values are stored in `power_supply_analytics_config.json` and parsed by `psa_gui_config.py`, keeping location, station, sector, cabinet, and IP definitions out of widget code.

## Installation

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Examples

### Single CDCU live monitor

```bash
python cdcu_monitor.py --host 192.168.1.2 --cabinet Cab_1 --sector S31
```

### Parallel CDCU monitoring

```bash
python cdcu_monitor.py --hosts 192.168.1.2 192.168.2.2 192.168.3.2 --cabinet Cab_1 --sector S31
```

### External two-channel DCBus capture

```bash
python cdcu_dcbus_fft.py --csv dcbus_scope.csv
```

### Generic four-channel scope capture

```bash
python cdcu_scope_fft.py \
  --csv scope4.csv \
  --channel "CH1,DCBus Input Voltage,V,40" \
  --channel "CH2,DCBus Input Current,A,200" \
  --channel "CH3,Output Voltage,V" \
  --channel "CH4,Output Current,A"
```

## Data integrity and spectral limits

A valid FFT/PSD needs a known, sufficiently uniform time base. The software checks timestamp spacing where timestamps are available. Live Ethernet telemetry is useful for trends, operating-state analysis, power balance, and fault context, but it is not treated as a substitute for a synchronized high-speed acquisition.

For a 10 kHz acquisition:

\[
\Delta t=100\ \mu s
\]

and the Nyquist frequency is:

\[
f_N=5\text{ kHz}
\]

The FFT/PSD code therefore never claims information above the physical Nyquist limit of the imported waveform.

## Code documentation standard

Every function and class in the repository has a docstring. Source comments explain engineering intent, important transformations, state changes, hardware/file operations, and non-obvious numerical decisions. The goal is not to comment Python syntax; the goal is to make the engineering reason for the code understandable to the next engineer who has to troubleshoot or extend it.

The function/library dependency map is generated from the source and checked into the repository so a change can be reviewed for impact before it is merged.

## Deprecation policy

The public baseline uses supported APIs in the current numerical stack. Examples include `scipy.integrate.trapezoid` instead of deprecated trapezoidal-integration paths and timezone-safe/current datetime usage where UTC semantics are required.

Deprecation warnings from project code are treated as defects. The test configuration is also explicit about asynchronous fixture scope so third-party pytest plugin defaults do not generate avoidable deprecation noise.

## AI model direction

Power Supply Analytics is intended to become the engineering backbone for a separate predictive-fault project.

The future AI-facing application will be a stripped-down, headless derivative of this repository. It will keep the validated acquisition, feature engineering, register decoding, spectral metrics, and correlation logic while removing GUI/reporting code that is not needed for model inference.

The AI pipeline is expected to create a correlated CSV dataset containing synchronized or timestamp-aligned power-supply features, operating state, fault labels, load context, spectral features, and derived diagnostic quantities. That dataset will be the interface between deterministic engineering analysis and the language-model/anomaly-detection layer.

The current project does **not** silently label anomalies as faults. Predictive classifications will remain separate from measured facts and deterministic fault registers.

See `docs/AI_DATA_CONTRACT.md` for the planned handoff boundary.

## Testing

The repository includes regression coverage for:

- CAEN efficiency thresholds and model specifications
- expected DCBus current math
- ppm semantics
- FFT amplitude normalization
- Welch PSD / Parseval consistency
- standard frequency bands
- DCBus external-capture validation
- 1–4 channel scope analysis
- magnet-load calculations

Run:

```bash
python -m pytest -q
```

## Author

**Byron Jordan**  
Power Supply Engineer  
Advanced Photon Source (APS)  
Argonne National Laboratory

The code is written as an engineering tool first: measurements should be traceable, calculations should be explainable, and an automated conclusion should never be allowed to hide the data that produced it.
