"""PySide6 desktop launcher for Power Supply Analytics engineering workflows.

The GUI is intentionally a thin orchestration layer.  It validates operator
selections, builds transparent command lines, and starts the existing analysis
modules through ``QProcess``.  No power-supply equations, FFT calculations,
fault decoding, or calibration logic are duplicated here.

Install the GUI dependency with::

    python -m pip install -e ".[gui]"

Then launch with either::

    python power_supply_analytics_gui.py

or the installed console entry point::

    power-supply-analytics
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Sequence

from psa_gui_config import (
    GuiConfig,
    TargetSelection,
    build_live_monitor_command,
    format_command,
    load_gui_config,
    validate_ip_selection,
    validate_target,
)

try:
    from PySide6.QtCore import QProcess, QProcessEnvironment, Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFileDialog,
        QFormLayout,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QDoubleSpinBox,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError as exc:  # pragma: no cover - exercised only without GUI extra.
    if exc.name != "PySide6":
        raise
    QProcess = None  # type: ignore[assignment]


PROJECT_ROOT = Path(__file__).resolve().parent


class PowerSupplyAnalyticsWindow(QMainWindow):
    """Provide an operator-facing launcher for the existing analysis modules.

    The first GUI release focuses on the live CDCU monitor because that workflow
    uses location/sector/cabinet/IP selections directly.  The Analysis selector
    also exposes the three file-driven spectral workflows and presents their
    required inputs without changing those modules' engineering calculations.
    """

    ANALYSES = (
        "Live Monitor",
        "PMM FFT / PSD",
        "DCBus FFT / PSD / Stability",
        "External Scope FFT / PSD / Stability",
    )

    def __init__(self, config: GuiConfig) -> None:
        """Build the main window from a validated repository configuration."""
        super().__init__()
        self.config = config
        self.process: QProcess | None = None
        self._ip_checks: dict[str, QCheckBox] = {}

        self.setWindowTitle("Power Supply Analytics")
        self.resize(1180, 820)

        root = QWidget(self)
        self.setCentralWidget(root)
        page = QVBoxLayout(root)
        page.addWidget(self._build_target_group())
        page.addWidget(self._build_ip_group())
        page.addWidget(self._build_analysis_group())
        page.addWidget(self._build_command_group())
        page.addWidget(self._build_console_group(), 1)

        self._apply_defaults()
        self._refresh_target_mode()
        self._refresh_station_choices()
        self._refresh_analysis_panel()
        self._refresh_command_preview()

    def _build_target_group(self) -> QGroupBox:
        """Create Storage Ring and test-stand target selectors."""
        group = QGroupBox("Target")
        layout = QVBoxLayout(group)

        top = QHBoxLayout()
        top.addWidget(QLabel("Target mode:"))
        self.target_mode = QComboBox()
        self.target_mode.addItems(("Storage Ring", "Test Stand"))
        self.target_mode.currentTextChanged.connect(self._refresh_target_mode)
        top.addWidget(self.target_mode)
        top.addStretch(1)
        layout.addLayout(top)

        self.target_stack = QStackedWidget()

        ring_page = QWidget()
        ring_form = QFormLayout(ring_page)
        self.sector = QComboBox()
        self.sector.addItems(self.config.sectors)
        self.sector.currentTextChanged.connect(self._refresh_command_preview)
        self.cabinet = QComboBox()
        self.cabinet.addItems(self.config.cabinets)
        self.cabinet.currentTextChanged.connect(self._refresh_command_preview)
        ring_form.addRow("Sector:", self.sector)
        ring_form.addRow("Cabinet:", self.cabinet)
        self.target_stack.addWidget(ring_page)

        test_page = QWidget()
        test_form = QFormLayout(test_page)
        self.location = QComboBox()
        self.location.addItems(tuple(self.config.locations))
        self.location.currentTextChanged.connect(self._refresh_station_choices)
        self.station = QComboBox()
        self.station.currentTextChanged.connect(self._refresh_command_preview)
        test_form.addRow("Location:", self.location)
        test_form.addRow("Station:", self.station)
        self.target_stack.addWidget(test_page)

        layout.addWidget(self.target_stack)
        return group

    def _build_ip_group(self) -> QGroupBox:
        """Create the eight-port CDCU IP selector with select/clear controls."""
        group = QGroupBox("Power Supply IP Addresses")
        layout = QVBoxLayout(group)

        grid = QGridLayout()
        for index, ip in enumerate(self.config.ip_addresses):
            check = QCheckBox(ip)
            check.stateChanged.connect(self._refresh_command_preview)
            self._ip_checks[ip] = check
            grid.addWidget(check, index // 4, index % 4)
        layout.addLayout(grid)

        buttons = QHBoxLayout()
        select_all = QPushButton("Select All")
        select_all.clicked.connect(lambda: self._set_all_ips(True))
        clear_all = QPushButton("Clear All")
        clear_all.clicked.connect(lambda: self._set_all_ips(False))
        buttons.addWidget(select_all)
        buttons.addWidget(clear_all)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        return group

    def _build_analysis_group(self) -> QGroupBox:
        """Create workflow selection and workflow-specific input controls."""
        group = QGroupBox("Analysis")
        layout = QVBoxLayout(group)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Workflow:"))
        self.analysis = QComboBox()
        self.analysis.addItems(self.ANALYSES)
        self.analysis.currentTextChanged.connect(self._refresh_analysis_panel)
        selector_row.addWidget(self.analysis)
        selector_row.addStretch(1)
        layout.addLayout(selector_row)

        self.analysis_stack = QStackedWidget()
        self.analysis_stack.addWidget(self._build_live_panel())
        self.analysis_stack.addWidget(self._build_pmm_panel())
        self.analysis_stack.addWidget(self._build_dcbus_panel())
        self.analysis_stack.addWidget(self._build_scope_panel())
        layout.addWidget(self.analysis_stack)
        return group

    def _build_live_panel(self) -> QWidget:
        """Create live-monitor duration, polling, output, and plotting controls."""
        panel = QWidget()
        form = QFormLayout(panel)

        self.duration = QDoubleSpinBox()
        self.duration.setRange(1.0, 86400.0)
        self.duration.setDecimals(1)
        self.duration.setSuffix(" s")
        self.duration.valueChanged.connect(self._refresh_command_preview)

        self.interval = QDoubleSpinBox()
        self.interval.setRange(0.001, 60.0)
        self.interval.setDecimals(4)
        self.interval.setSuffix(" s")
        self.interval.valueChanged.connect(self._refresh_command_preview)

        self.no_analysis = QCheckBox("Skip optional post-run report assembly")
        self.no_analysis.stateChanged.connect(self._refresh_command_preview)
        self.individual_plots = QCheckBox("Use one live plot window per supply")
        self.individual_plots.stateChanged.connect(self._refresh_command_preview)

        self.outdir = QLineEdit(str(PROJECT_ROOT / "output"))
        self.outdir.textChanged.connect(self._refresh_command_preview)
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_outdir)
        out_row = QHBoxLayout()
        out_row.addWidget(self.outdir, 1)
        out_row.addWidget(browse)
        out_wrapper = QWidget()
        out_wrapper.setLayout(out_row)

        form.addRow("Live duration:", self.duration)
        form.addRow("Polling interval:", self.interval)
        form.addRow("Output directory:", out_wrapper)
        form.addRow("", self.no_analysis)
        form.addRow("", self.individual_plots)
        return panel

    def _build_file_row(self, line_edit: QLineEdit, callback) -> QWidget:
        """Return a reusable line-edit plus Browse button row for CSV workflows."""
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(line_edit, 1)
        button = QPushButton("Browse…")
        button.clicked.connect(callback)
        row.addWidget(button)
        return wrapper

    def _build_pmm_panel(self) -> QWidget:
        """Create PMM CSV spectral-analysis controls."""
        panel = QWidget()
        form = QFormLayout(panel)
        self.pmm_csv = QLineEdit()
        self.pmm_csv.textChanged.connect(self._refresh_command_preview)
        self.pmm_model = QComboBox()
        self.pmm_model.addItems(("", "CDCU-100", "CDCU-200", "CDCU-300"))
        self.pmm_model.currentTextChanged.connect(self._refresh_command_preview)
        self.pmm_fft_y = QComboBox()
        self.pmm_fft_y.addItems(("magnitude", "percent", "ppm"))
        self.pmm_fft_y.currentTextChanged.connect(self._refresh_command_preview)
        self.pmm_load_desc = QLineEdit()
        self.pmm_load_desc.textChanged.connect(self._refresh_command_preview)
        form.addRow("PMM CSV:", self._build_file_row(self.pmm_csv, lambda: self._browse_csv(self.pmm_csv)))
        form.addRow("CDCU model:", self.pmm_model)
        form.addRow("FFT Y-axis:", self.pmm_fft_y)
        form.addRow("Load description:", self.pmm_load_desc)
        return panel

    def _build_dcbus_panel(self) -> QWidget:
        """Create the standardized two-channel external DCBus workflow controls."""
        panel = QWidget()
        form = QFormLayout(panel)
        self.dcbus_csv = QLineEdit()
        self.dcbus_csv.textChanged.connect(self._refresh_command_preview)
        self.dcbus_vref = QLineEdit()
        self.dcbus_vref.setPlaceholderText("optional volts")
        self.dcbus_vref.textChanged.connect(self._refresh_command_preview)
        self.dcbus_iref = QLineEdit()
        self.dcbus_iref.setPlaceholderText("optional amperes")
        self.dcbus_iref.textChanged.connect(self._refresh_command_preview)
        self.dcbus_assume = QCheckBox("Assume exact 10 kHz only when acquisition hardware is known")
        self.dcbus_assume.stateChanged.connect(self._refresh_command_preview)
        form.addRow("DCBus CSV:", self._build_file_row(self.dcbus_csv, lambda: self._browse_csv(self.dcbus_csv)))
        form.addRow("VBus reference:", self.dcbus_vref)
        form.addRow("IBus reference:", self.dcbus_iref)
        form.addRow("", self.dcbus_assume)
        return panel

    def _build_scope_panel(self) -> QWidget:
        """Create generic one-to-four-channel oscilloscope workflow controls."""
        panel = QWidget()
        form = QFormLayout(panel)
        self.scope_csv = QLineEdit()
        self.scope_csv.textChanged.connect(self._refresh_command_preview)
        self.scope_sample_rate = QLineEdit()
        self.scope_sample_rate.setPlaceholderText("optional Hz when CSV has no time column")
        self.scope_sample_rate.textChanged.connect(self._refresh_command_preview)
        self.scope_channels: list[QLineEdit] = []
        form.addRow("Scope CSV:", self._build_file_row(self.scope_csv, lambda: self._browse_csv(self.scope_csv)))
        form.addRow("Sample rate:", self.scope_sample_rate)
        for number in range(1, 5):
            edit = QLineEdit()
            edit.setPlaceholderText(f"CH{number},Label,unit,reference(optional)")
            edit.textChanged.connect(self._refresh_command_preview)
            self.scope_channels.append(edit)
            form.addRow(f"Channel {number}:", edit)
        return panel

    def _build_command_group(self) -> QGroupBox:
        """Create transparent command preview and execution controls."""
        group = QGroupBox("Command Preview")
        layout = QVBoxLayout(group)
        self.command_preview = QPlainTextEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setMaximumBlockCount(200)
        fixed = QFont("Consolas")
        fixed.setStyleHint(QFont.Monospace)
        self.command_preview.setFont(fixed)
        layout.addWidget(self.command_preview)

        controls = QHBoxLayout()
        validate_button = QPushButton("Validate")
        validate_button.clicked.connect(self._validate_dialog)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run_selected)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._stop_process)
        self.stop_button.setEnabled(False)
        controls.addWidget(validate_button)
        controls.addWidget(self.run_button)
        controls.addWidget(self.stop_button)
        controls.addStretch(1)
        self.status_label = QLabel("Ready")
        controls.addWidget(self.status_label)
        layout.addLayout(controls)
        return group

    def _build_console_group(self) -> QGroupBox:
        """Create the live stdout/stderr console used during a launched workflow."""
        group = QGroupBox("Live Console")
        layout = QVBoxLayout(group)
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(10000)
        fixed = QFont("Consolas")
        fixed.setStyleHint(QFont.Monospace)
        self.console.setFont(fixed)
        layout.addWidget(self.console)
        return group

    def _apply_defaults(self) -> None:
        """Apply repository defaults without hard-coding operational selections in widgets."""
        defaults = self.config.defaults
        self.target_mode.setCurrentText(str(defaults.get("target_mode", "Storage Ring")))
        self.sector.setCurrentText(str(defaults.get("sector", self.config.sectors[0])))
        self.cabinet.setCurrentText(str(defaults.get("cabinet", self.config.cabinets[0])))
        self.location.setCurrentText(str(defaults.get("location", next(iter(self.config.locations)))))
        self.duration.setValue(float(defaults.get("duration_s", 120.0)))
        self.interval.setValue(float(defaults.get("interval_s", 0.40)))
        self.analysis.setCurrentText(str(defaults.get("analysis", "Live Monitor")))

    def _refresh_target_mode(self) -> None:
        """Switch between ring and test-stand selectors and refresh the command."""
        self.target_stack.setCurrentIndex(0 if self.target_mode.currentText() == "Storage Ring" else 1)
        self._refresh_command_preview()

    def _refresh_station_choices(self) -> None:
        """Limit station choices to those explicitly defined for the selected location."""
        location = self.location.currentText()
        previous = self.station.currentText()
        self.station.blockSignals(True)
        self.station.clear()
        self.station.addItems(self.config.stations_for(location))
        preferred = str(self.config.defaults.get("station", ""))
        if previous in self.config.stations_for(location):
            self.station.setCurrentText(previous)
        elif preferred in self.config.stations_for(location):
            self.station.setCurrentText(preferred)
        self.station.blockSignals(False)
        self._refresh_command_preview()

    def _refresh_analysis_panel(self) -> None:
        """Show only the inputs required by the selected analysis module."""
        self.analysis_stack.setCurrentIndex(self.ANALYSES.index(self.analysis.currentText()))
        self._refresh_command_preview()

    def _set_all_ips(self, checked: bool) -> None:
        """Set all configured IP checkboxes to the requested state."""
        for check in self._ip_checks.values():
            check.setChecked(checked)
        self._refresh_command_preview()

    def _selected_ips(self) -> tuple[str, ...]:
        """Return selected addresses in configured physical-port order."""
        return tuple(ip for ip in self.config.ip_addresses if self._ip_checks[ip].isChecked())

    def _target(self) -> TargetSelection:
        """Build a typed target object from the currently visible selectors."""
        return TargetSelection(
            mode=self.target_mode.currentText(),
            sector=self.sector.currentText(),
            cabinet=self.cabinet.currentText(),
            location=self.location.currentText(),
            station=self.station.currentText(),
        )

    def _output_directory(self) -> Path:
        """Resolve the operator-entered output directory without creating it."""
        return Path(self.outdir.text().strip() or ".").expanduser()

    def _build_command(self) -> list[str]:
        """Build the selected module command using the module's existing CLI contract."""
        workflow = self.analysis.currentText()
        if workflow == "Live Monitor":
            return build_live_monitor_command(
                self._target(),
                self._selected_ips(),
                duration_s=self.duration.value(),
                interval_s=self.interval.value(),
                outdir=self._output_directory(),
                no_analysis=self.no_analysis.isChecked(),
                individual_plots=self.individual_plots.isChecked(),
                script_path=PROJECT_ROOT / "cdcu_monitor.py",
            )

        if workflow == "PMM FFT / PSD":
            command = [sys.executable, str(PROJECT_ROOT / "cdcu_pmm_fft.py"), "--csv", self.pmm_csv.text().strip()]
            if self.pmm_model.currentText():
                command += ["--model", self.pmm_model.currentText()]
            command += ["--fft-y", self.pmm_fft_y.currentText()]
            if self.pmm_load_desc.text().strip():
                command += ["--load-desc", self.pmm_load_desc.text().strip()]
            return command

        if workflow == "DCBus FFT / PSD / Stability":
            command = [sys.executable, str(PROJECT_ROOT / "cdcu_dcbus_fft.py"), "--csv", self.dcbus_csv.text().strip()]
            if self.dcbus_vref.text().strip():
                command += ["--vbus-ref", self.dcbus_vref.text().strip()]
            if self.dcbus_iref.text().strip():
                command += ["--ibus-ref", self.dcbus_iref.text().strip()]
            if self.dcbus_assume.isChecked():
                command.append("--assume-10khz")
            return command

        command = [sys.executable, str(PROJECT_ROOT / "cdcu_scope_fft.py"), "--csv", self.scope_csv.text().strip()]
        if self.scope_sample_rate.text().strip():
            command += ["--sample-rate", self.scope_sample_rate.text().strip()]
        for edit in self.scope_channels:
            if edit.text().strip():
                command += ["--channel", edit.text().strip()]
        return command

    def _validation_errors(self) -> list[str]:
        """Validate selections and file requirements before starting a subprocess."""
        errors = validate_target(self.config, self._target())
        workflow = self.analysis.currentText()
        if workflow == "Live Monitor":
            errors.extend(validate_ip_selection(self.config, self._selected_ips()))
            if self.duration.value() <= 0:
                errors.append("Live duration must be greater than zero.")
            if self.interval.value() <= 0:
                errors.append("Polling interval must be greater than zero.")
        elif workflow == "PMM FFT / PSD":
            errors.extend(self._validate_csv_path(self.pmm_csv.text(), "PMM CSV"))
        elif workflow == "DCBus FFT / PSD / Stability":
            errors.extend(self._validate_csv_path(self.dcbus_csv.text(), "DCBus CSV"))
            errors.extend(self._validate_optional_float(self.dcbus_vref.text(), "VBus reference"))
            errors.extend(self._validate_optional_float(self.dcbus_iref.text(), "IBus reference"))
        else:
            errors.extend(self._validate_csv_path(self.scope_csv.text(), "Scope CSV"))
            errors.extend(self._validate_optional_float(self.scope_sample_rate.text(), "Sample rate"))
            if not any(edit.text().strip() for edit in self.scope_channels):
                errors.append("Define at least one oscilloscope channel.")
        return errors

    @staticmethod
    def _validate_csv_path(value: str, label: str) -> list[str]:
        """Validate a required CSV path and return a GUI-ready error list."""
        path = Path(value.strip()).expanduser()
        if not value.strip():
            return [f"{label} is required."]
        if not path.is_file():
            return [f"{label} does not exist: {path}"]
        return []

    @staticmethod
    def _validate_optional_float(value: str, label: str) -> list[str]:
        """Validate an optional numeric field without forcing the operator to use it."""
        if not value.strip():
            return []
        try:
            float(value)
        except ValueError:
            return [f"{label} must be numeric when specified."]
        return []

    def _refresh_command_preview(self) -> None:
        """Update the command preview; display incomplete fields without raising dialogs."""
        try:
            self.command_preview.setPlainText(format_command(self._build_command()))
        except Exception as exc:
            self.command_preview.setPlainText(f"Command incomplete: {exc}")

    def _validate_dialog(self) -> None:
        """Present a complete validation result before the operator commits to a run."""
        errors = self._validation_errors()
        if errors:
            QMessageBox.warning(self, "Validation", "Correct the following before running:\n\n• " + "\n• ".join(errors))
            return
        QMessageBox.information(self, "Validation", "Configuration is valid for the selected workflow.")

    def _run_selected(self) -> None:
        """Launch the selected existing Python module and stream its output into the GUI."""
        errors = self._validation_errors()
        if errors:
            QMessageBox.warning(self, "Cannot Run", "Correct the following before running:\n\n• " + "\n• ".join(errors))
            return
        if self.process is not None and self.process.state() != QProcess.NotRunning:
            QMessageBox.information(self, "Run Active", "A Power Supply Analytics workflow is already running.")
            return

        if self.analysis.currentText() == "Live Monitor":
            self._output_directory().mkdir(parents=True, exist_ok=True)

        command = self._build_command()
        self.console.appendPlainText("\n=== RUN ===")
        self.console.appendPlainText(format_command(command))
        self.console.appendPlainText("")

        self.process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONUTF8", "1")
        environment.insert("PYTHONIOENCODING", "utf-8")
        self.process.setProcessEnvironment(environment)
        self.process.setWorkingDirectory(str(PROJECT_ROOT))
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_process_output)
        self.process.started.connect(self._process_started)
        self.process.finished.connect(self._process_finished)
        self.process.errorOccurred.connect(self._process_error)
        self.process.start(command[0], command[1:])

    def _read_process_output(self) -> None:
        """Decode merged subprocess output as UTF-8 and append it to the live console."""
        if self.process is None:
            return
        data = bytes(self.process.readAllStandardOutput())
        if data:
            self.console.appendPlainText(data.decode("utf-8", errors="replace").rstrip("\n"))

    def _process_started(self) -> None:
        """Reflect a successfully launched process in the operator controls."""
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Running")

    def _process_finished(self, exit_code: int, _exit_status) -> None:
        """Restore controls and report the subprocess exit code."""
        self._read_process_output()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Complete" if exit_code == 0 else f"Exit {exit_code}")
        self.console.appendPlainText(f"\n=== PROCESS EXIT {exit_code} ===\n")

    def _process_error(self, _error) -> None:
        """Surface a QProcess launch/runtime error without hiding subprocess diagnostics."""
        if self.process is None:
            return
        self.status_label.setText("Process error")
        self.console.appendPlainText(f"QProcess error: {self.process.errorString()}")

    def _stop_process(self) -> None:
        """Request a clean stop first, then allow Qt to terminate the child process."""
        if self.process is None or self.process.state() == QProcess.NotRunning:
            return
        self.console.appendPlainText("\n=== STOP REQUESTED ===")
        self.process.terminate()

    def _browse_outdir(self) -> None:
        """Open a directory chooser and update the live-monitor output path."""
        selected = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.outdir.text())
        if selected:
            self.outdir.setText(selected)

    def _browse_csv(self, destination: QLineEdit) -> None:
        """Open a CSV chooser and write the selected path into ``destination``."""
        selected, _ = QFileDialog.getOpenFileName(self, "Select CSV", str(PROJECT_ROOT), "CSV files (*.csv);;All files (*)")
        if selected:
            destination.setText(selected)


def main(argv: Sequence[str] | None = None) -> int:
    """Create the Qt application and return its event-loop exit status."""
    if QProcess is None:
        print(
            "PySide6 is required for the Power Supply Analytics GUI.\n"
            "Install it with: python -m pip install -e \".[gui]\"",
            file=sys.stderr,
        )
        return 2

    app = QApplication(list(argv) if argv is not None else sys.argv)
    config = load_gui_config()
    window = PowerSupplyAnalyticsWindow(config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
