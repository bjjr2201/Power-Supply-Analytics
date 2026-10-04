#!/usr/bin/env python3
"""Regression tests for magnet R/L characterization and slew-headroom math."""

import magnet_load_diagnostics as diagnostics


def test_magnet_nameplate_and_dynamic_calculations() -> None:
    """Verify nameplate parsing, measured R/L math, deviation, and slew-rate estimates."""
    # Use the same load-description grammar consumed by the production load map.
    entry = {
        "load_desc": (
            "Magnet: B400A_slot_5; DMM_Q3; "
            "Resistance: 0.064 Ohm; Inductance: 16.9 mH"
        )
    }
    # Parse the textual nameplate and confirm both SI-unit conversions are exact.
    nameplate = diagnostics.parse_nameplate(entry)
    assert abs(nameplate.resistance_ohm - 0.064) < 1e-12
    assert abs(nameplate.inductance_h - 0.0169) < 1e-12

    # Check steady-state resistance from V/I at the 300 A reference point.
    assert abs(diagnostics.measured_resistance(19.2, 300.0) - 0.064) < 1e-12

    # Check dI/dt and the rearranged V = RI + L dI/dt inductance estimate.
    didt_a_per_s = diagnostics.estimate_didt(0.0, 100.0, 0.1, 200.0)
    assert abs(didt_a_per_s - 1000.0) < 1e-9
    inductance_h = diagnostics.estimated_inductance(30.0, 200.0, 1000.0, 0.064)
    assert abs(inductance_h - 0.0172) < 1e-12

    # Verify absolute, percentage, and ppm deviation use the same reference.
    delta, percent, ppm = diagnostics.deviation(0.066, 0.064)
    assert abs(delta - 0.002) < 1e-12
    assert abs(percent - 3.125) < 1e-9
    assert abs(ppm - 31250.0) < 1e-6

    # Verify the rated-current IR drop, resistive power, and positive slew headroom.
    voltage_v, power_w = diagnostics.extrapolate_at_current(0.064, 300.0)
    assert abs(voltage_v - 19.2) < 1e-12
    assert abs(power_w - 5760.0) < 1e-9
    slew_a_per_s = diagnostics.max_slew_rate(45.0, 300.0, 0.064, 0.0169)
    assert abs(slew_a_per_s - 1526.6272189349114) < 1e-6
