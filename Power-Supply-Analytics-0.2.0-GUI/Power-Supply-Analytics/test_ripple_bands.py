#!/usr/bin/env python3
"""Regression checks for Power Supply Analytics spectral bands and callout ranking."""

import math

import numpy as np

from cdcu_ripple_bands import ANALYSIS_BANDS, BAND_STR, CALLOUT_BANDS, CALLOUT_FMAX_HZ
from cdcu_ripple_psd import (
    _top_peaks_by_callout_band,
    integrate_psd_rms,
    parse_bands,
    welch_psd,
)


def test_standard_band_definition_and_1khz_integration() -> None:
    """Verify the shared integration bands preserve the established 1 kHz behavior."""
    # Parse the compact configuration through the production parser so the text
    # representation and tuple representation cannot silently diverge.
    parsed = parse_bands(BAND_STR)
    assert parsed == ANALYSIS_BANDS

    # The standard high-frequency integration band must contain 1 kHz rather
    # than placing the tone directly on a band edge.
    one_khz_band = [band for band in ANALYSIS_BANDS if band[0] < 1000.0 < band[1]]
    assert len(one_khz_band) == 1, ANALYSIS_BANDS
    lo_hz, hi_hz, label = one_khz_band[0]
    assert (lo_hz, hi_hz, label) == (720.0, 1200.0, "720-1200 Hz")

    # Build a 1.000 A RMS, 1 kHz sinusoid on the same 10 kHz/100,001-sample
    # time base used by the standardized CDCU PMM analysis.
    sample_rate_hz = 10_000.0
    sample_count = 100_001
    time_s = np.arange(sample_count, dtype=float) / sample_rate_hz
    signal_a = math.sqrt(2.0) * np.sin(2.0 * np.pi * 1000.0 * time_s)

    # Run the production Welch and integration functions rather than duplicating
    # their mathematics inside the test.
    frequency_hz, psd = welch_psd(signal_a, fs=sample_rate_hz, nperseg=16384)
    rms_1k_band = integrate_psd_rms(psd, frequency_hz, lo_hz, hi_hz)
    rms_lower_band = integrate_psd_rms(psd, frequency_hz, 360.0, 720.0)

    # Allow small Welch/window numerical tolerance while requiring the full RMS
    # tone to remain in the expected integration band.
    assert 0.98 <= rms_1k_band <= 1.02, rms_1k_band
    assert rms_lower_band < 0.01, rms_lower_band


def test_callouts_select_two_components_per_band_through_1khz() -> None:
    """Verify callouts rank two components independently in every band and stop at 1 kHz."""
    # Use a simple 1 Hz grid so the expected peak bins are exact and easy to
    # audit when this test fails in the future.
    frequency_hz = np.arange(0.0, 1201.0, 1.0)
    amplitude = np.zeros_like(frequency_hz)

    # Place two known dominant components in each visualization band.
    expected = {
        "1-10 Hz": [(7.0, 8.0), (3.0, 7.0)],
        "60-120 Hz": [(90.0, 6.0), (60.0, 5.0)],
        "360-720 Hz": [(500.0, 4.0), (700.0, 3.0)],
        "720-1000 Hz": [(999.0, 2.0), (800.0, 1.0)],
    }
    for peaks in expected.values():
        for freq_hz, magnitude in peaks:
            amplitude[int(freq_hz)] = magnitude

    # Add a deliberately larger component above 1 kHz; it must never appear in
    # the callout result even though the integration/display data may include it.
    amplitude[1100] = 100.0

    selected = _top_peaks_by_callout_band(
        frequency_hz,
        amplitude,
        xmin=0.0,
        xmax=1200.0,
        n_per_band=2,
    )

    # Four callout bands times two peaks produces eight deterministic records.
    assert len(selected) == len(CALLOUT_BANDS) * 2
    assert max(record[2] for record in selected) <= CALLOUT_FMAX_HZ
    assert all(record[2] != 1100.0 for record in selected)

    # Confirm the strongest two bins are ranked independently inside each band.
    grouped: dict[str, list[tuple[int, float, float]]] = {}
    for band_label, rank, freq_hz, magnitude, _index in selected:
        grouped.setdefault(band_label, []).append((rank, freq_hz, magnitude))
    for band_label, peaks in expected.items():
        assert grouped[band_label] == [
            (1, peaks[0][0], peaks[0][1]),
            (2, peaks[1][0], peaks[1][1]),
        ]
