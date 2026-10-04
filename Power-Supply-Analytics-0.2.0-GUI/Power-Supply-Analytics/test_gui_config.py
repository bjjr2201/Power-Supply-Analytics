"""Regression tests for GUI configuration and command construction."""

from pathlib import Path

import pytest

from psa_gui_config import (
    TargetSelection,
    build_live_monitor_command,
    load_gui_config,
    validate_ip_selection,
    validate_target,
)


def test_repository_gui_configuration_matches_operating_locations() -> None:
    """Protect the agreed B400A/L1127 station map and eight-address IP pool."""
    config = load_gui_config()
    assert config.stations_for("B400A") == ("Test_1", "Test_2", "Test_bench")
    assert config.stations_for("L1127") == ("Test_bench",)
    assert config.sectors[0] == "S01"
    assert config.sectors[-1] == "S40"
    assert config.cabinets == ("Cab_1", "Cab_2", "Cab_3", "Cab_4", "Cab_5")
    assert config.ip_addresses == tuple(f"192.168.{index}.2" for index in range(1, 9))


def test_test_stand_target_maps_to_existing_monitor_arguments() -> None:
    """Verify GUI location/station values become monitor sector/cabinet arguments."""
    target = TargetSelection(mode="Test Stand", location="B400A", station="Test_2")
    command = build_live_monitor_command(
        target,
        ("192.168.5.2", "192.168.7.2"),
        duration_s=60,
        interval_s=0.4,
        outdir=Path("results"),
        python_executable="python",
        script_path="cdcu_monitor.py",
    )
    assert command == [
        "python",
        "cdcu_monitor.py",
        "--hosts",
        "192.168.5.2",
        "192.168.7.2",
        "--cabinet",
        "Test_2",
        "--sector",
        "B400A",
        "--duration",
        "60.0",
        "--interval",
        "0.4",
        "--outdir",
        "results",
    ]


def test_storage_ring_target_maps_directly_to_monitor_arguments() -> None:
    """Verify ring selectors preserve Sxx/Cab_x naming used by the load map."""
    target = TargetSelection(mode="Storage Ring", sector="S31", cabinet="Cab_4")
    command = build_live_monitor_command(
        target,
        ("192.168.1.2",),
        duration_s=120,
        interval_s=0.2,
        outdir="out",
        python_executable="python",
        script_path="cdcu_monitor.py",
    )
    assert command[command.index("--sector") + 1] == "S31"
    assert command[command.index("--cabinet") + 1] == "Cab_4"


def test_invalid_l1127_station_is_rejected() -> None:
    """Prevent B400A-only stations from being silently accepted at L1127."""
    config = load_gui_config()
    errors = validate_target(
        config,
        TargetSelection(mode="Test Stand", location="L1127", station="Test_1"),
    )
    assert errors


def test_ip_validation_accepts_spare_ports_seven_and_eight() -> None:
    """Keep spare .7.2/.8.2 network-port selections available to the operator."""
    config = load_gui_config()
    assert validate_ip_selection(config, ("192.168.7.2", "192.168.8.2")) == []


def test_live_command_rejects_empty_ip_selection() -> None:
    """A live monitor must never launch without an explicit target supply."""
    target = TargetSelection(mode="Storage Ring", sector="S01", cabinet="Cab_1")
    with pytest.raises(ValueError, match="At least one IP"):
        build_live_monitor_command(
            target,
            (),
            duration_s=60,
            interval_s=0.4,
            outdir="out",
        )
