# AI Data Contract — Planned Interface

The future predictive-fault application will be a stripped-down derivative of Power Supply Analytics. The purpose of this document is to protect the boundary between deterministic engineering data and model-generated conclusions.

## Planned output

The AI-facing process should produce a correlated CSV or equivalent tabular dataset. One row should represent a defined observation interval or event window, not an arbitrary mixture of unsynchronized samples.

Recommended field groups:

- identity: host, serial number, model, sector, cabinet, magnet/load ID
- acquisition: UTC/local timestamp, source, sample rate, sample count, timing quality
- operating state: enabled/off, steady/transient/cycling, current setpoint, load fraction
- DCBus: voltage/current/power statistics and protection margins
- output: voltage/current/power statistics
- efficiency/power balance: measured efficiency, reference, source, expected Ibus, error
- temperatures: individual sensor values and gradients/trends where supported
- faults: raw register values plus decoded active bits
- spectral features: band RMS, dominant frequencies, peak amplitudes, PSD-integrated RMS
- magnet/load context: R, L, measured resistance, estimated inductance, slew-rate context
- labels: deterministic fault/event labels kept separate from AI-predicted labels

## Correlation rules

- Preserve original timestamps.
- Record the acquisition source for every high-speed feature.
- Do not combine sequential Ethernet reads into a claim of simultaneous high-speed power.
- Do not resample irregular telemetry for precision FFT/PSD unless the method is explicitly selected and documented.
- Keep raw register values alongside decoded text.
- Keep model inputs reproducible from stored data whenever practical.

## Model output rules

A future model may emit anomaly score, predicted fault family, confidence, supporting features, and comparison to known-good baseline. Those fields must never overwrite measured fault bits or deterministic engineering results.
