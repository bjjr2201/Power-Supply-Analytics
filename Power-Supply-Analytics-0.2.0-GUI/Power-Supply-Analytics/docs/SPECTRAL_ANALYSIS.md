# Spectral Analysis Standard

## FFT

The single-sided FFT is reported as RMS sinusoidal component amplitude. The time-domain mean is removed before ripple analysis. Window coherent gain is accounted for so a bin-centered sinusoid produces the expected RMS amplitude.

## PSD

Welch PSD is reported in engineering-unit squared per hertz. Integrated PSD is converted back to RMS and compared with time-domain RMS as a Parseval-style quality check.

## Standard integration bands

The shared integration bands are defined in `cdcu_ripple_bands.py`:

- 1–10 Hz
- 60–120 Hz
- 360–720 Hz
- 720–1200 Hz

## FFT callout bands

Callouts are a visualization layer and use a separate final cap at 1 kHz:

- 1–10 Hz — strongest two components
- 60–120 Hz — strongest two components
- 360–720 Hz — strongest two components
- 720–1000 Hz — strongest two components

The 720–1200 Hz integration band is not changed by the 1 kHz callout cap.

## Sampling

FFT and PSD require a known time base. PMM and external oscilloscope captures are accepted when their timing satisfies the acquisition requirements. Live Ethernet polling is retained for trends and diagnostics, not presented as a hardware-timed ripple waveform.
