"""Configuration and command-building support for the Power Supply Analytics GUI.

This module deliberately contains no Qt code.  The GUI is a presentation and
orchestration layer; the engineering analysis remains in the existing command-
line modules.  Keeping configuration validation and command construction here
allows those rules to be regression-tested without a desktop session.

The design also gives the future AI-facing application a clean boundary.  It
can reuse target metadata and deterministic command/configuration rules without
importing a GUI toolkit.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address
from importlib import resources
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence


CONFIG_FILE = Path(__file__).with_name("power_supply_analytics_config.json")


@dataclass(frozen=True)
class TargetSelection:
    """Represent one operator-selected hardware context.

    ``mode`` selects one of two addressing conventions:

    * ``Storage Ring`` uses ``sector`` (S01...S40) and ``cabinet``
      (Cab_1...Cab_5).
    * ``Test Stand`` uses ``location`` (for example B400A or L1127) and a
      location-qualified ``station`` (for example Test_1 or Test_bench).

    The existing CDCU monitor already accepts the test-stand convention through
    its ``--sector`` and ``--cabinet`` arguments.  ``monitor_sector`` and
    ``monitor_cabinet`` expose that translation explicitly instead of hiding it
    inside the GUI.
    """

    mode: str
    sector: str = ""
    cabinet: str = ""
    location: str = ""
    station: str = ""

    @property
    def monitor_sector(self) -> str:
        """Return the value supplied to ``cdcu_monitor.py --sector``."""
        return self.sector if self.mode == "Storage Ring" else self.location

    @property
    def monitor_cabinet(self) -> str:
        """Return the value supplied to ``cdcu_monitor.py --cabinet``."""
        return self.cabinet if self.mode == "Storage Ring" else self.station

    @property
    def label(self) -> str:
        """Return a concise human-readable target name for logs and previews."""
        if self.mode == "Storage Ring":
            return f"{self.sector} / {self.cabinet}"
        return f"{self.location} / {self.station}"


@dataclass(frozen=True)
class GuiConfig:
    """Hold validated operator choices loaded from the repository JSON file."""

    locations: Mapping[str, tuple[str, ...]]
    sectors: tuple[str, ...]
    cabinets: tuple[str, ...]
    ip_addresses: tuple[str, ...]
    defaults: Mapping[str, Any]

    def stations_for(self, location: str) -> tuple[str, ...]:
        """Return the allowed stations for ``location`` or an empty tuple."""
        return self.locations.get(location, ())


def _inclusive_names(prefix: str, start: int, end: int, *, width: int = 0) -> tuple[str, ...]:
    """Generate an inclusive, consistently formatted engineering identifier list.

    The helper centralizes formatting so selectors and validation always agree.
    A future expansion to additional sectors or cabinets therefore changes the
    JSON bounds rather than multiple GUI widgets.
    """
    if start > end:
        raise ValueError(f"Invalid range: start {start} is greater than end {end}")
    if width:
        return tuple(f"{prefix}{value:0{width}d}" for value in range(start, end + 1))
    return tuple(f"{prefix}{value}" for value in range(start, end + 1))


def load_gui_config(path: str | Path = CONFIG_FILE) -> GuiConfig:
    """Load and validate the GUI configuration file.

    Validation is intentionally performed before a Qt window is created.  A
    malformed station map or duplicate IP address is an engineering
    configuration error, not a widget error, and should fail clearly.

    Source-tree users normally edit ``power_supply_analytics_config.json``.  A
    wheel installation may not have that repository file beside the module, so
    the packaged default is used only when the default path is absent.  An
    explicitly requested missing path still raises ``FileNotFoundError``.
    """
    config_path = Path(path)
    if config_path.is_file():
        with config_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    elif config_path == CONFIG_FILE:
        resource = resources.files("power_supply_analytics_data").joinpath("default_gui_config.json")
        raw = json.loads(resource.read_text(encoding="utf-8"))
    else:
        raise FileNotFoundError(config_path)

    raw_locations = raw.get("locations", {})
    if not isinstance(raw_locations, dict) or not raw_locations:
        raise ValueError("Configuration must define at least one location")

    locations: dict[str, tuple[str, ...]] = {}
    for location, payload in raw_locations.items():
        stations = tuple(payload.get("stations", ()))
        if not stations:
            raise ValueError(f"Location {location!r} must define at least one station")
        if len(stations) != len(set(stations)):
            raise ValueError(f"Location {location!r} contains duplicate station names")
        locations[str(location)] = tuple(str(item) for item in stations)

    ring = raw.get("storage_ring", {})
    sectors = _inclusive_names(
        "S",
        int(ring.get("sector_start", 1)),
        int(ring.get("sector_end", 40)),
        width=2,
    )
    cabinets = _inclusive_names(
        "Cab_",
        int(ring.get("cabinet_start", 1)),
        int(ring.get("cabinet_end", 5)),
    )

    ip_addresses = tuple(str(item) for item in raw.get("ip_addresses", ()))
    if not ip_addresses:
        raise ValueError("Configuration must define at least one IP address")
    if len(ip_addresses) != len(set(ip_addresses)):
        raise ValueError("Configuration contains duplicate IP addresses")
    for address in ip_addresses:
        IPv4Address(address)  # Raises a precise ValueError for malformed addresses.

    return GuiConfig(
        locations=locations,
        sectors=sectors,
        cabinets=cabinets,
        ip_addresses=ip_addresses,
        defaults=dict(raw.get("defaults", {})),
    )


def validate_target(config: GuiConfig, target: TargetSelection) -> list[str]:
    """Return all target-selection validation errors without stopping at the first.

    Returning a complete list is more useful at a test stand than raising on the
    first missing field.  The operator can correct every highlighted selection
    before starting a data-acquisition run.
    """
    errors: list[str] = []
    if target.mode == "Storage Ring":
        if target.sector not in config.sectors:
            errors.append(f"Sector must be one of {config.sectors[0]} through {config.sectors[-1]}.")
        if target.cabinet not in config.cabinets:
            errors.append(f"Cabinet must be one of {config.cabinets[0]} through {config.cabinets[-1]}.")
    elif target.mode == "Test Stand":
        if target.location not in config.locations:
            errors.append(f"Unknown test location: {target.location!r}.")
        elif target.station not in config.stations_for(target.location):
            errors.append(
                f"Station {target.station!r} is not defined for location {target.location!r}."
            )
    else:
        errors.append("Target mode must be 'Storage Ring' or 'Test Stand'.")
    return errors


def validate_ip_selection(config: GuiConfig, selected_ips: Iterable[str]) -> list[str]:
    """Validate a multi-IP selection against the configured test-network pool."""
    ips = tuple(selected_ips)
    errors: list[str] = []
    if not ips:
        errors.append("Select at least one CDCU IP address.")
    unknown = [ip for ip in ips if ip not in config.ip_addresses]
    if unknown:
        errors.append("Unsupported IP address(es): " + ", ".join(unknown))
    if len(ips) != len(set(ips)):
        errors.append("The IP selection contains duplicates.")
    return errors


def build_live_monitor_command(
    target: TargetSelection,
    selected_ips: Sequence[str],
    *,
    duration_s: float,
    interval_s: float,
    outdir: str | Path,
    no_analysis: bool = False,
    individual_plots: bool = False,
    python_executable: str = sys.executable,
    script_path: str | Path = "cdcu_monitor.py",
) -> list[str]:
    """Build the existing multi-IP live-monitor command without duplicating analysis logic.

    The GUI calls the same ``cdcu_monitor.py`` workflow used at the command line.
    That keeps one validated implementation of acquisition, PMM capture,
    diagnostics, CSV output, plotting, and reporting.
    """
    if duration_s <= 0:
        raise ValueError("Live duration must be greater than zero seconds")
    if interval_s <= 0:
        raise ValueError("Polling interval must be greater than zero seconds")
    if not selected_ips:
        raise ValueError("At least one IP address is required")

    command = [
        str(python_executable),
        str(script_path),
        "--hosts",
        *selected_ips,
        "--cabinet",
        target.monitor_cabinet,
        "--sector",
        target.monitor_sector,
        "--duration",
        str(float(duration_s)),
        "--interval",
        str(float(interval_s)),
        "--outdir",
        str(outdir),
    ]
    if no_analysis:
        command.append("--no-analysis")
    if individual_plots:
        command.append("--individual-plots")
    return command


def format_command(command: Sequence[str]) -> str:
    """Return a copy/paste-friendly command preview with safe shell quoting.

    Windows and POSIX shells have different quoting rules.  For the GUI preview
    we use Python's standard-library ``subprocess.list2cmdline`` on Windows and
    ``shlex.join`` elsewhere so the displayed command remains diagnostic rather
    than merely decorative.
    """
    if sys.platform.startswith("win"):
        import subprocess

        return subprocess.list2cmdline(list(command))

    import shlex

    return shlex.join(command)
