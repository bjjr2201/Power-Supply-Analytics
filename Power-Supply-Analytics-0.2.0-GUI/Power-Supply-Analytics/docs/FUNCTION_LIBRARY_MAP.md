# Function / Library Dependency Map

This file is generated from the current Python source by `tools/generate_function_map.py`.
It is a change-impact aid: it shows module libraries, statically visible project calls, and direct project callers so an engineer can identify likely affected code before modifying a calculation or interface.

> Dynamic dispatch, callbacks, subprocess boundaries, and runtime imports may not appear as direct calls. Use this map together with regression tests and code review.

## `cdcu_dcbus_fft.py`

**Project-module dependencies:** `cdcu_ripple_bands`, `cdcu_ripple_psd`, `cdcu_scope_fft`

**Python / third-party libraries:** `argparse`, `math`, `numpy`, `pandas`, `pathlib`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_normalize_columns` | Map common CDCU/EPICS names to the two canonical DCBus columns. | — | `cdcu_dcbus_fft.py:validate_dcbus_capture` | `ALIASES.items`, `df.rename` |
| `validate_dcbus_capture` | Validate and normalize an exact 100,001-sample / 10 kHz DCBus capture. | `_normalize_columns` | `cdcu_dcbus_fft.py:analyze_dcbus_dataframe` | `df.copy`, `np.all`, `np.any`, `np.arange`, `np.diff`, `np.isfinite`, `np.mean`, `np.std`, `out.insert`, `pd.to_numeric` |
| `analyze_dcbus_dataframe` | Run strict 10 kHz DCBus FFT/PSD plus 10-second record stability. | `analyze_scope_dataframe`, `validate_dcbus_capture` | `cdcu_dcbus_fft.py:analyze_dcbus_csv` | — |
| `analyze_dcbus_csv` | Load a DCBus hardware capture CSV and analyze both input channels. | `analyze_dcbus_dataframe` | `cdcu_dcbus_fft.py:_main` | `kwargs.pop`, `path.is_file`, `pd.read_csv` |
| `acquire_dcbus_native_10khz` | Reserved native-acquisition hook. | — | — | — |
| `_main` | Parse command-line arguments, run the requested analysis workflow, and return a process exit code. | `analyze_dcbus_csv` | — | `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args` |

## `cdcu_diagnostics.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `collections`, `math`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_is_bad` | Return True when a diagnostic value is missing, non-numeric, or not finite. | — | `cdcu_diagnostics.py:bus_current_percent_error`, `cdcu_diagnostics.py:caen_efficiency_compliance`, `cdcu_diagnostics.py:calculate_efficiency_percent`, `cdcu_diagnostics.py:calculate_load_fraction`, `cdcu_diagnostics.py:calculate_power`, `cdcu_diagnostics.py:efficiency_health`, `cdcu_diagnostics.py:eta_reference_details`, `cdcu_diagnostics.py:expected_input_current`, `cdcu_diagnostics.py:percent_point_delta_to_abs_ppm`, `cdcu_diagnostics.py:percent_to_ppm`, `…` | `math.isfinite` |
| `percent_to_ppm` | Convert percent to ppm: 1% = 10,000 ppm. | `_is_bad` | — | — |
| `percent_point_delta_to_abs_ppm` | Convert a percentage-point difference to absolute fractional ppm. | `_is_bad` | — | — |
| `relative_percent_difference_ppm` | Return relative ppm difference of one percentage value from another. | `_is_bad` | — | — |
| `get_model_spec` | Return the engineering specification dictionary for a recognized CDCU model, or None when the model is unknown. | — | `cdcu_diagnostics.py:caen_efficiency_compliance`, `cdcu_diagnostics.py:calculate_load_fraction`, `cdcu_diagnostics.py:eta_reference_details`, `cdcu_diagnostics.py:investigate_threshold_for_model`, `cdcu_monitor.py:_analyze_pmm_immediately`, `cdcu_pmm_fft.py:_ppm_reference` | `MODEL_EFFICIENCY_REFERENCE.get` |
| `eta_reference_for_model` | Expected efficiency baseline with provenance handled by eta_reference_details(). | `eta_reference_details` | — | — |
| `eta_reference_details` | Resolve the efficiency reference and provenance used by downstream power-balance diagnostics. | `_is_bad`, `get_model_spec` | `cdcu_diagnostics.py:eta_reference_for_model` | `MODEL_EMPIRICAL_ETA_REFERENCE.get` |
| `investigate_threshold_for_model` | Return the model-specific DCBus-current error threshold used to escalate an investigation. | `get_model_spec` | — | — |
| `calculate_power` | Calculate absolute electrical power from voltage and current telemetry. | `_is_bad` | `cdcu_diagnostics.py:calculate_efficiency_percent`, `cdcu_diagnostics.py:expected_input_current` | — |
| `calculate_efficiency_percent` | Calculate conversion efficiency in percent from output and DCBus input measurements. | `_is_bad`, `calculate_power` | — | — |
| `expected_input_current` | Estimate DCBus input current from output power, DCBus voltage, and an efficiency reference. | `_is_bad`, `calculate_power` | — | — |
| `bus_current_percent_error` | Return absolute and percentage error between measured and expected DCBus input current. | `_is_bad` | — | — |
| `calculate_load_fraction` | Return output power as a fraction of the selected CDCU model rated power. | `_is_bad`, `get_model_spec` | `cdcu_diagnostics.py:substantial_load` | — |
| `substantial_load` | Return True when the output load is high enough for efficiency and power-balance diagnostics to be meaningful. | `_is_bad`, `calculate_load_fraction` | — | — |
| `efficiency_health` | Classify deviation from the selected diagnostic efficiency baseline. | `_is_bad` | — | — |
| `caen_efficiency_compliance` | Evaluate CAEN's efficiency specification only near rated full load. | `_is_bad`, `get_model_spec` | — | — |
| `power_loss` | Return converter power loss in watts and as a percentage of input power. | `_is_bad` | — | — |
| `diagnostic_state` | Combine telemetry validity, operating state, load, and reference availability into a single diagnostic state label. | — | — | — |
| `diagnostic_confidence` | Translate efficiency-reference provenance and diagnostic validity into an operator-facing confidence label. | — | — | — |
| `__init__` | Initialize the object state and store the engineering thresholds required by later methods. | — | — | — |
| `update` | Process one new sample, update internal state, and return the current steady-state decision. | `_is_bad` | `cdcu_scope_fft.py:write_stability_reports` | `self._buf.append`, `self._buf.popleft` |
| `reset` | Clear accumulated state so a new operating interval can be evaluated independently. | — | — | `self._buf.clear` |

## `cdcu_load_map.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `argparse`, `json`, `os`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `__init__` | Initialize the object state and store the engineering thresholds required by later methods. | — | — | `json.load`, `os.path.isfile` |
| `lookup` | Return a fully-resolved metadata dict for (cabinet, ip). | `self._resolve` | `cdcu_load_map.py:_cli`, `cdcu_load_map.py:lookup_soft` | `cab_data.get`, `cab_data.keys`, `self._data.get`, `self._data.keys` |
| `lookup_soft` | Like lookup() but returns None instead of raising KeyError when the | `self.lookup` | `one_liners.py:main`, `one_liners.py:resolve_ips` | — |
| `list_cabinets` | Return all cabinet names in the load map. | — | `cdcu_load_map.py:_cli`, `one_liners.py:main`, `one_liners.py:resolve_ips` | `self._data.keys` |
| `list_ips` | Return all IPs registered under *cabinet*. | — | `cdcu_load_map.py:_cli`, `one_liners.py:main`, `one_liners.py:resolve_ips` | `cab_data.keys`, `self._data.get` |
| `find_by_ip` | Search all cabinets for *ip*.  Returns a list of | `self._resolve` | `cdcu_load_map.py:_cli` | `results.append`, `self._data.items` |
| `all_entries` | Iterate over every (cabinet, ip, resolved_entry) in the map. | `self._resolve` | — | `ips.items`, `out.append`, `self._data.items` |
| `_resolve` | Apply {SECTOR} substitution and numeric coercion to a raw entry. | `_to_float_or_none` | `cdcu_load_map.py:all_entries`, `cdcu_load_map.py:find_by_ip`, `cdcu_load_map.py:lookup` | `raw.items`, `v.replace` |
| `_to_float_or_none` | Return float(s) or None if s is empty / non-numeric. | — | `cdcu_load_map.py:_resolve` | `s.strip` |
| `load_map_from_env_or_default` | Convenience loader used by cdcu_monitor.py. | — | — | `os.environ.get`, `os.path.isfile` |
| `_cli` | Provide the command-line entry point for inspecting and validating the load-map configuration. | `lm.find_by_ip`, `lm.list_cabinets`, `lm.list_ips`, `lm.lookup` | — | `ap.add_argument`, `ap.parse_args`, `ap.print_help`, `argparse.ArgumentParser`, `entry.get`, `entry.items` |

## `cdcu_monitor.py`

**Project-module dependencies:** `cdcu_dcbus_fft`, `cdcu_diagnostics`, `cdcu_load_map`, `cdcu_pmm`, `cdcu_registers`, `cdcu_ripple_bands`, `cdcu_ripple_io`, `cdcu_ripple_pdf`, `cdcu_ripple_psd`, `magnet_load_diagnostics`

**Python / third-party libraries:** `PIL`, `argparse`, `collections`, `csv`, `datetime`, `json`, `math`, `matplotlib`, `numpy`, `os`, `signal`, `socket`, `statistics`, `subprocess`, `sys`, `threading`, `time`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_format_runtime` | Return elapsed seconds as both numeric seconds and HH:MM:SS.s. | — | `cdcu_monitor.py:_run_parallel_hosts`, `one_liners.py:main` | — |
| `_normalize_hosts` | Return a de-duplicated host list while accepting space- or comma-separated input. | — | `cdcu_monitor.py:_run_parallel_hosts` | `host.strip`, `hosts.append`, `seen.add` |
| `_create_parallel_dashboard` | Create one consolidated 2-column live dashboard for up to eight CDCU supplies. | — | `cdcu_monitor.py:_run_parallel_hosts` | `ax.grid`, `ax.tick_params`, `ax_blank.axis`, `fig.add_gridspec`, `fig.add_subplot`, `fig.canvas.manager.set_window_title`, `fig.subplots_adjust`, `fig.suptitle`, `manager.window.state`, `plt.figure`, `plt.get_current_fig_manager`, `plt.ion`, `…` |
| `_update_parallel_dashboard` | Load atomic child snapshots and refresh the consolidated dashboard. | — | `cdcu_monitor.py:_run_parallel_hosts` | `ax.autoscale_view`, `ax.axvspan`, `ax.relim`, `ax.set_xlim`, `dq.append`, `fig.canvas.draw_idle`, `fig.canvas.flush_events`, `json.load`, `line.set_data`, `os.path.isfile`, `plt.pause`, `snap.get`, `…` |
| `_run_parallel_hosts` | Launch one independent cdcu_monitor.py process per IP address. | `_create_parallel_dashboard`, `_format_runtime`, `_normalize_hosts`, `_update_parallel_dashboard` | — | `_subprocess.Popen`, `_threading.Lock`, `_threading.Thread`, `cmd.append`, `cmd.extend`, `dashboard_fig.savefig`, `datetime.now`, `finish_local.strftime`, `ip.replace`, `log_fh.write`, `os.environ.copy`, `os.makedirs`, `…` |
| `_stream_output` | Mirror one child's terminal output to its log and prefix it in the parent terminal. | — | — | `log_fh.write` |
| `_write_dashboard_snapshot` | Atomically publish a compact live-telemetry snapshot for the multi-IP dashboard. | — | — | `json.dump`, `os.makedirs`, `os.path.abspath`, `os.path.dirname`, `os.replace`, `time.perf_counter` |
| `_parse_cdcu_field` | Strip '#PREFIX:' from a CDCU response; return value after the last ':'. | — | — | `raw.split` |
| `_magnet_name_from_load_desc` | If magnet_id ends with ':' (bare sector prefix, no name), extract the | — | — | `load_desc.split`, `magnet_id.endswith`, `p.strip` |
| `send_command` | Send one CDCU Ethernet command and return the complete ASCII response from the power supply. | — | — | `data.decode`, `sock.recv`, `sock.sendall` |
| `parse_float` | Parse CDCU responses like: | — | — | `text.split` |
| `safe_power` | Compute power magnitude = \|V * I\| when both inputs are valid. | — | — | `math.isnan` |
| `calculate_efficiency_percent` | Measured converter efficiency using power magnitudes: | — | — | `math.isnan` |
| `clip_efficiency_percent` | Clip efficiency only for display purposes while preserving raw efficiency for diagnostics and saved data. | — | — | `math.isnan` |
| `_pct_and_ppm` | Return (percent, ppm) for engineering reporting; 1% = 10,000 ppm. | — | — | `math.isnan` |
| `_analyze_pmm_immediately` | Immediately analyze one PMM capture and persist machine/human-readable summaries. | `_pmm_psd.analyze_series_for_reports`, `_pmm_psd.recommended_welch_nperseg`, `cdcu_diagnostics.get_model_spec`, `clean` | — | `_m.isfinite`, `_os.makedirs`, `_os.path.abspath`, `_os.path.dirname`, `_os.path.join`, `col_map.items`, `fh.write`, `json.dump`, `math.isfinite`, `results.keys`, `v.items` |
| `clean` | Convert optional numeric values to a CSV-safe representation without replacing invalid telemetry with fabricated zeros. | — | `cdcu_monitor.py:_analyze_pmm_immediately` | `math.isfinite`, `v.items` |

## `cdcu_pmm.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `numpy`, `pandas`, `socket`, `time`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_send_recv` | Send a CR-terminated command and read the response byte-by-byte until  | — | `cdcu_pmm.py:arm`, `cdcu_pmm.py:fetch_channel`, `cdcu_pmm.py:force`, `cdcu_pmm.py:get_trigger_position`, `cdcu_pmm.py:is_ready`, `cdcu_pmm.py:set_trigger_position`, `cdcu_pmm.py:timestamp` | `buf.decode`, `sock.recv`, `sock.sendall`, `sock.settimeout` |
| `_parse_nak` | Return the error code string if the response is a NAK, else None. | — | — | `resp.startswith` |
| `__init__` | Initialize the object state and store the engineering thresholds required by later methods. | — | — | — |
| `arm` | Send PMM:RESET to arm (or rearm) the acquisition buffer. | `_send_recv` | `cdcu_pmm.py:acquire_pmm` | `resp.startswith` |
| `force` | Send PMM:FORCE to software-trigger the PMM buffer immediately. | `_send_recv` | — | `resp.startswith` |
| `set_trigger_position` | Set the trigger position (seconds of pre-fault data in the window). | `_send_recv` | `cdcu_pmm.py:acquire_pmm` | `resp.startswith` |
| `get_trigger_position` | Query the current trigger position in seconds. | `_send_recv` | — | `resp.split` |
| `is_ready` | Return True if the acquisition buffer is full and ready to read. | `_send_recv` | `cdcu_pmm.py:wait_ready` | `resp.split` |
| `wait_ready` | Poll PMM:READY:? every poll_interval seconds until READY=1 or timeout. | `self.is_ready` | `cdcu_pmm.py:acquire_pmm` | `time.monotonic`, `time.sleep` |
| `timestamp` | Return the PMM acquisition timestamp string from the unit | `_send_recv` | `cdcu_pmm.py:acquire_pmm` | `resp.split` |
| `fetch_channel` | Fetch one PMM channel and return (samples, col_name, unit, label). | `_send_recv` | `cdcu_pmm.py:fetch_dataframe` | `np.fromstring`, `raw_samples.strip`, `resp.split`, `resp.startswith`, `resp.upper` |
| `fetch_dataframe` | Fetch all (or specified) PMM channels and return a tidy DataFrame. | `self.fetch_channel` | `cdcu_pmm.py:acquire_pmm` | `PMM_CHANNELS.keys`, `channel_scales.get`, `data.items`, `np.arange`, `np.full`, `pd.DataFrame` |
| `acquire_pmm` | High-level convenience: connect (or reuse *sock*), arm, wait, fetch. | `pmm.arm`, `pmm.fetch_dataframe`, `pmm.set_trigger_position`, `pmm.timestamp`, `pmm.wait_ready` | — | `sock.close`, `socket.create_connection` |

## `cdcu_pmm_fft.py`

**Project-module dependencies:** `cdcu_diagnostics`, `cdcu_ripple_bands`, `cdcu_ripple_psd`

**Python / third-party libraries:** `argparse`, `math`, `os`, `pandas`, `pathlib`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_parse_channels` | Convert a comma-separated channel list into validated PMM column names. | — | `cdcu_pmm_fft.py:main` | `item.strip`, `raw.split` |
| `_ppm_reference` | Resolve the ppm denominator and state exactly what it represents. | `cdcu_diagnostics.get_model_spec` | `cdcu_pmm_fft.py:analyze_pmm_csv` | `math.isfinite`, `pd.to_numeric` |
| `analyze_pmm_csv` | Run FFT, PSD, cumulative RMS, and band analysis on a saved PMM capture. | `_ppm_reference`, `cdcu_ripple_psd.analyze_series_for_reports`, `cdcu_ripple_psd.recommended_welch_nperseg` | `cdcu_pmm_fft.py:main`, `cdcu_ripple_analyzer.py:main` | `PMM_CHANNELS.keys`, `_sampling.get`, `channel_dir.mkdir`, `destination.mkdir`, `handle.write`, `logo.is_file`, `pd.read_csv`, `pd.to_numeric`, `refs.get`, `result.get`, `results.items`, `source.is_file`, `…` |
| `main` | Parse command-line options and run standalone PMM spectral analysis. | `_parse_channels`, `analyze_pmm_csv` | — | `argparse.ArgumentParser`, `parser.add_argument`, `parser.parse_args` |

## `cdcu_registers.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `argparse`, `json`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `decode_mftr` | Decode MFTR hex register string (e.g. '00000010') into a dict: | `_strip_prefix` | `cdcu_registers.py:_cli`, `cdcu_registers.py:fault_summary` | `hex_str.strip` |
| `decode_mstr` | Decode MSTR hex register string (e.g. '00000012') into a dict: | `_strip_prefix` | `cdcu_registers.py:_cli`, `cdcu_registers.py:fault_summary` | `_POWER_STATE.get`, `hex_str.strip` |
| `decode_mwrr` | Decode MWRR hex register string (e.g. '00000001') into a dict: | `_strip_prefix` | `cdcu_registers.py:_cli`, `cdcu_registers.py:fault_summary` | `hex_str.strip` |
| `fault_summary` | Return a compact multi-line summary string for logging / PDF headers. | `decode_mftr`, `decode_mstr`, `decode_mwrr` | `cdcu_registers.py:_cli` | `lines.append` |
| `active_bits` | Return list of set bit positions in a hex register string. | `_strip_prefix` | — | — |
| `_strip_prefix` | Strip a leading '#XXX:' echo prefix if present. | — | `cdcu_registers.py:active_bits`, `cdcu_registers.py:decode_mftr`, `cdcu_registers.py:decode_mstr`, `cdcu_registers.py:decode_mwrr` | `prefix.upper`, `s.split`, `s.startswith`, `s.strip`, `s.upper` |
| `_cli` | Provide the command-line entry point for inspecting and validating the load-map configuration. | `decode_mftr`, `decode_mstr`, `decode_mwrr`, `fault_summary` | — | `ap.add_argument`, `ap.parse_args`, `argparse.ArgumentParser`, `json.dumps` |

## `cdcu_ripple_analyzer.py`

**Project-module dependencies:** `cdcu_pmm_fft`

**Python / third-party libraries:** `argparse`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `main` | Route a saved PMM CSV to the PMM-only FFT/PSD analysis path. | `analyze_pmm_csv` | — | `argparse.ArgumentParser`, `parser.add_argument`, `parser.parse_args` |

## `cdcu_ripple_bands.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |

## `cdcu_ripple_io.py`

**Project-module dependencies:** `cdcu_ripple_bands`

**Python / third-party libraries:** `csv`, `datetime`, `os`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `read_ps_ripple_metadata` | Read '# key = value' metadata lines from the top of a PS_RIPPLE_CSV v1 file. | — | — | `k.strip`, `line.startswith`, `s.split`, `v.strip` |
| `write_ps_ripple_csv` | Write PS_RIPPLE_CSV v1: | — | — | `csv.writer`, `data_cols.items`, `data_cols.keys`, `datetime.now`, `f.write`, `meta.items`, `os.makedirs`, `os.path.dirname`, `row.append`, `w.writerow` |

## `cdcu_ripple_pdf.py`

**Project-module dependencies:** `cdcu_ripple_bands`

**Python / third-party libraries:** `PIL`, `docx`, `os`, `reportlab`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_safe_draw_image` | Draw an image safely while preserving transparency. | — | `cdcu_ripple_pdf.py:_draw_footer`, `cdcu_ripple_pdf.py:build_combined_pdf`, `cdcu_ripple_pdf.py:build_pdf_summary` | `_ImageDraw.Draw`, `_PILImage.open`, `_draw.rectangle`, `c.drawImage`, `os.path.isfile` |
| `_draw_footer` | Draw APS/Argonne branding at the lower-right footer location. | `_safe_draw_image` | `cdcu_ripple_pdf.py:_build_worksheet_pdf`, `cdcu_ripple_pdf.py:build_combined_pdf`, `cdcu_ripple_pdf.py:build_pdf_summary` | `c.drawString`, `c.setFont`, `c.stringWidth` |
| `_draw_header` | Draw the page 1 header block including load map data and serial number. | — | `cdcu_ripple_pdf.py:build_combined_pdf`, `cdcu_ripple_pdf.py:build_pdf_summary` | `c.drawString`, `c.line`, `c.setFont`, `c.setLineWidth`, `load_desc.split`, `loc_parts.append`, `meta.get`, `p.strip`, `v_parts.append` |
| `_draw_load_map_block` | Draw a compact load map identity + Fs advisory box above the Band RMS | — | `cdcu_ripple_pdf.py:build_combined_pdf`, `cdcu_ripple_pdf.py:build_pdf_summary` | `c.drawString`, `c.setFillColor`, `c.setFont`, `id_parts.append`, `load_desc.split`, `loc_parts.append`, `meta.get`, `p.strip` |
| `_draw_band_table` | Draw a compact per-channel band RMS table. | — | `cdcu_ripple_pdf.py:_build_worksheet_pdf`, `cdcu_ripple_pdf.py:build_combined_pdf`, `cdcu_ripple_pdf.py:build_pdf_summary` | `c.drawString`, `c.setFont`, `r.get` |
| `_draw_diagnostics_block` | Draw the power-balance diagnostics summary block (model, eta_reference, | — | `cdcu_ripple_pdf.py:_build_worksheet_pdf`, `cdcu_ripple_pdf.py:build_combined_pdf` | `c.drawString`, `c.setFillColor`, `c.setFont`, `line1_parts.append`, `meta.get`, `verdict.upper` |
| `build_pdf_summary` | Build the branded engineering PDF summary for a completed CDCU analysis run. | `_draw_band_table`, `_draw_footer`, `_draw_header`, `_draw_load_map_block`, `_safe_draw_image` | — | `c.drawString`, `c.save`, `c.setFont`, `c.showPage`, `canvas.Canvas`, `meta.get`, `os.path.basename`, `r.get` |
| `_sig_lines_for_results` | Build concise significant-component text lines from completed spectral-analysis result dictionaries. | — | `cdcu_ripple_pdf.py:_build_worksheet_docx`, `cdcu_ripple_pdf.py:_build_worksheet_pdf` | `lines.append`, `r.get`, `results.items` |
| `build_technical_worksheet` | Create a technical worksheet artifact from the same validated results used by the PDF summary. | `_build_worksheet_docx`, `_build_worksheet_pdf` | — | — |
| `_build_worksheet_docx` | Render the technical worksheet as a DOCX document for engineering review and record keeping. | `_sig_lines_for_results` | `cdcu_ripple_pdf.py:build_technical_worksheet` | `_diag_verdict.upper`, `doc.add_heading`, `doc.add_paragraph`, `doc.save`, `meta.get`, `r.get`, `results.items` |
| `_build_worksheet_pdf` | Render the technical worksheet as a PDF document for controlled distribution or archival. | `_draw_band_table`, `_draw_diagnostics_block`, `_draw_footer`, `_sig_lines_for_results` | `cdcu_ripple_pdf.py:build_technical_worksheet` | `c.drawString`, `c.save`, `c.setFont`, `c.showPage`, `canvas.Canvas`, `meta.get`, `r.get`, `results.items` |
| `build_combined_pdf` | Build a single combined PDF with: | `_draw_band_table`, `_draw_diagnostics_block`, `_draw_footer`, `_draw_header`, `_draw_load_map_block`, `_safe_draw_image` | — | `c.drawString`, `c.line`, `c.save`, `c.setFont`, `c.setLineWidth`, `c.showPage`, `canvas.Canvas`, `load_desc.split`, `loc_parts.append`, `meta.get`, `os.path.basename`, `p.strip`, `…` |

## `cdcu_ripple_psd.py`

**Project-module dependencies:** `cdcu_ripple_bands`

**Python / third-party libraries:** `PIL`, `datetime`, `math`, `matplotlib`, `numpy`, `os`, `pandas`, `scipy`, `textwrap`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `parse_bands` | Parse compact band string '1-10:1-10 Hz,60-120:60-120 Hz,...' | `parse_num` | `cdcu_ripple_psd.py:analyze_series_for_reports` | `bands.split`, `name.strip`, `out.append`, `part.split`, `part.strip`, `rng.split`, `s.endswith`, `s.strip` |
| `parse_num` | Parse a compact frequency token, including k and M suffixes, into hertz. | — | `cdcu_ripple_psd.py:parse_bands` | `s.endswith`, `s.strip` |
| `ppm` | Return x_rms / \|ref\| * 1e6, or None if ref is None/zero. | — | `cdcu_ripple_psd.py:analyze_series_for_reports`, `cdcu_ripple_psd.py:plot_composite_report`, `cdcu_ripple_psd.py:plot_fft_tdk` | — |
| `sampling_uniformity` | Quantify timing uniformity for FFT/PSD suitability. | — | `cdcu_ripple_psd.py:load_trace_from_df` | `np.abs`, `np.asarray`, `np.diff`, `np.isfinite`, `np.max`, `np.mean`, `np.median`, `np.std` |
| `load_trace_from_df` | Load one trace and enforce the uniform-sampling requirement of FFT/Welch. | `sampling_uniformity` | `cdcu_ripple_psd.py:analyze_series_for_reports` | `np.arange`, `np.argsort`, `np.concatenate`, `np.diff`, `np.interp`, `np.isfinite`, `np.mean` |
| `recommended_welch_nperseg` | Choose a practical Welch segment length without exceeding the record. | — | `cdcu_monitor.py:_analyze_pmm_immediately`, `cdcu_pmm_fft.py:analyze_pmm_csv`, `cdcu_scope_fft.py:analyze_scope_dataframe` | — |
| `single_sided_fft_rms` | Compute a coherent-gain-corrected single-sided RMS line spectrum. | — | `cdcu_ripple_psd.py:analyze_series_for_reports` | `A.copy`, `np.abs`, `np.asarray`, `np.fft.rfft`, `np.fft.rfftfreq`, `np.mean`, `np.sqrt`, `np.sum` |
| `welch_psd` | Welch PSD estimate with safe overlap clamping. | — | `cdcu_ripple_psd.py:analyze_series_for_reports` | `np.asarray`, `np.mean` |
| `integrate_psd_rms` | Integrate PSD over [lo, hi] with interpolated band edges. | — | `cdcu_ripple_psd.py:analyze_series_for_reports` | `np.asarray`, `np.concatenate`, `np.interp`, `np.sqrt` |
| `cumulative_integrated_power` | Cumulative integral of PSD -- equivalent to ripple_exec's np.cumsum(Ipower)*df. | — | `cdcu_ripple_psd.py:analyze_series_for_reports` | `np.zeros_like` |
| `_style_axes_tdk` | Apply TDK-style major + minor grid. | — | `cdcu_ripple_psd.py:plot_composite_report`, `cdcu_ripple_psd.py:plot_integrated_power_tdk`, `cdcu_ripple_psd.py:plot_psd_tdk` | `ax.grid`, `ax.minorticks_on` |
| `_auto_freq_limits_from_psd` | Detect meaningful x-axis span from PSD content. | — | `cdcu_ripple_psd.py:analyze_series_for_reports` | `np.any`, `np.argmax`, `np.asarray`, `np.isfinite`, `np.max` |
| `_max_point_in_band` | Return (x, y, idx) of the global maximum within [xmin, xmax], x > 0. | — | `cdcu_ripple_psd.py:plot_composite_report`, `cdcu_ripple_psd.py:plot_psd_tdk` | `np.any`, `np.argmax`, `np.asarray`, `np.isfinite`, `np.where` |
| `_top_n_peaks_in_band` | Return up to *n* (x, y, idx) tuples of the highest y values within | — | `cdcu_ripple_psd.py:_top_peaks_by_callout_band`, `cdcu_ripple_psd.py:plot_fft_tdk` | `np.any`, `np.argsort`, `np.asarray`, `np.isfinite`, `np.where` |
| `_top_peaks_by_callout_band` | Return the strongest components in each configured FFT callout band. | `_top_n_peaks_in_band` | `cdcu_ripple_psd.py:plot_fft_tdk` | `selected.append` |
| `_annotate_bands` | Shade each analysis band with a distinct colour and legend entry. | — | `cdcu_ripple_psd.py:plot_composite_report`, `cdcu_ripple_psd.py:plot_integrated_power_tdk`, `cdcu_ripple_psd.py:plot_psd_tdk` | `ax.axvspan` |
| `_add_figure_footer` | Add generation timestamp (lower-left) and optional logo inset (lower-right). | — | `cdcu_ripple_psd.py:plot_fft_tdk`, `cdcu_ripple_psd.py:plot_integrated_power_tdk`, `cdcu_ripple_psd.py:plot_psd_tdk` | `_PILImage.open`, `ax_logo.axis`, `ax_logo.imshow`, `datetime.now`, `fig.add_axes`, `fig.text`, `os.path.isfile` |
| `_fft_display_scale` | Return FFT magnitude values in the operator-selected engineering display scale. | — | `cdcu_ripple_psd.py:plot_composite_report`, `cdcu_ripple_psd.py:plot_fft_tdk` | `np.asarray`, `np.isfinite`, `np.nanmax` |
| `_dominant_band_summary` | Return the frequency band with the largest integrated RMS contribution. | — | `cdcu_ripple_psd.py:plot_composite_report`, `cdcu_ripple_psd.py:plot_fft_tdk` | `np.isfinite` |
| `plot_fft_tdk` | Draw the primary FFT as a linear, filled spectrum with an engineering summary box. | `_add_figure_footer`, `_dominant_band_summary`, `_fft_display_scale`, `_top_n_peaks_in_band`, `_top_peaks_by_callout_band`, `ppm` | `cdcu_ripple_psd.py:analyze_series_for_reports` | `ax.annotate`, `ax.fill_between`, `ax.grid`, `ax.minorticks_on`, `ax.plot`, `ax.set_title`, `ax.set_xlabel`, `ax.set_xlim`, `ax.set_ylabel`, `ax.set_ylim`, `ax.text`, `band_callout_records.append`, `…` |
| `plot_psd_tdk` | PSD plot (log-log) with single MAX arrowhead callout and optional band shading. | `_add_figure_footer`, `_annotate_bands`, `_max_point_in_band`, `_style_axes_tdk` | `cdcu_ripple_psd.py:analyze_series_for_reports` | `ax.annotate`, `ax.legend`, `ax.loglog`, `ax.set_title`, `ax.set_xlabel`, `ax.set_xlim`, `ax.set_ylabel`, `fig.savefig`, `fig.tight_layout`, `np.maximum`, `plt.close`, `plt.subplots` |
| `plot_integrated_power_tdk` | Cumulative integrated power plot (log-log) with text summary and optional | `_add_figure_footer`, `_annotate_bands`, `_style_axes_tdk` | `cdcu_ripple_psd.py:analyze_series_for_reports` | `ax.legend`, `ax.loglog`, `ax.set_title`, `ax.set_xlabel`, `ax.set_xlim`, `ax.set_ylabel`, `ax.text`, `fig.savefig`, `fig.tight_layout`, `np.maximum`, `plt.close`, `plt.subplots` |
| `plot_composite_report` | Composite 8.5x11 single-page report figure -- matches ripple_exec.py layout: | `_annotate_bands`, `_dominant_band_summary`, `_fft_display_scale`, `_max_point_in_band`, `_style_axes_tdk`, `ppm` | `cdcu_ripple_psd.py:analyze_series_for_reports` | `_PILImage.open`, `ax1.fill_between`, `ax1.grid`, `ax1.minorticks_on`, `ax1.plot`, `ax1.set_title`, `ax1.set_xlabel`, `ax1.set_xlim`, `ax1.set_ylabel`, `ax1.set_ylim`, `ax1.text`, `ax2.annotate`, `…` |
| `analyze_series_for_reports` | Full FFT/PSD analysis for one channel.  Produces three individual PNGs | `_auto_freq_limits_from_psd`, `cumulative_integrated_power`, `integrate_psd_rms`, `load_trace_from_df`, `parse_bands`, `plot_composite_report`, `plot_fft_tdk`, `plot_integrated_power_tdk`, `plot_psd_tdk`, `ppm`, `single_sided_fft_rms`, `welch_psd` | `cdcu_monitor.py:_analyze_pmm_immediately`, `cdcu_pmm_fft.py:analyze_pmm_csv`, `cdcu_scope_fft.py:analyze_scope_dataframe` | `band_rms.append`, `fh.write`, `lines.append`, `np.argsort`, `np.isfinite`, `np.mean`, `np.sqrt`, `os.makedirs`, `os.path.join`, `sampling_info.get`, `sigs.append` |

## `cdcu_scope_fft.py`

**Project-module dependencies:** `cdcu_ripple_bands`, `cdcu_ripple_psd`

**Python / third-party libraries:** `argparse`, `dataclasses`, `math`, `numpy`, `pandas`, `pathlib`, `re`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_safe_stem` | Return a filesystem-safe channel stem. | — | `cdcu_scope_fft.py:analyze_scope_dataframe` | `re.sub`, `text.strip` |
| `_infer_unit_and_label` | Infer a reasonable display label/unit without changing the source data. | — | `cdcu_scope_fft.py:_auto_channels` | `column.lower`, `low.endswith`, `low.startswith` |
| `parse_channel_spec` | Parse COLUMN,LABEL,UNIT[,REFERENCE]. | — | `cdcu_scope_fft.py:_main` | `math.isfinite`, `p.strip`, `spec.split` |
| `_resolve_time_column` | Resolve the oscilloscope time column from an explicit request or supported common column names. | — | `cdcu_scope_fft.py:prepare_scope_dataframe` | — |
| `_auto_channels` | Auto-select up to four numeric-looking measurement columns. | `_infer_unit_and_label` | `cdcu_scope_fft.py:prepare_scope_dataframe` | `channels.append`, `numeric.notna`, `pd.to_numeric` |
| `prepare_scope_dataframe` | Validate a hardware-timed scope record and return a normalized time base. | `_auto_channels`, `_resolve_time_column` | `cdcu_scope_fft.py:analyze_scope_dataframe` | `df.copy`, `math.isfinite`, `np.all`, `np.any`, `np.arange`, `np.diff`, `np.isfinite`, `np.mean`, `np.std`, `pd.to_numeric`, `seen.add`, `work.insert` |
| `stability_metrics` | Calculate time-domain stability metrics for one oscilloscope channel. | `rel_pct`, `rel_ppm` | `cdcu_scope_fft.py:analyze_scope_dataframe` | `math.isfinite`, `np.abs`, `np.asarray`, `np.max`, `np.mean`, `np.median`, `np.min`, `np.polyfit`, `np.sqrt`, `np.std` |
| `rel_ppm` | Return a deviation relative to the selected reference in parts per million. | — | `cdcu_scope_fft.py:stability_metrics` | — |
| `rel_pct` | Return a deviation relative to the selected reference in percent. | — | `cdcu_scope_fft.py:stability_metrics` | — |
| `_fmt` | Format an optional numeric result for stable human-readable CSV and text reporting. | — | `cdcu_scope_fft.py:write_stability_reports` | `math.isfinite` |
| `write_stability_reports` | Write concise human-readable and machine-readable stability summaries. | `_fmt`, `row.update` | `cdcu_scope_fft.py:analyze_scope_dataframe` | `lines.extend`, `pd.DataFrame`, `rows.append`, `txt_path.write_text` |
| `analyze_scope_dataframe` | Analyze up to four scope channels with FFT/PSD and record stability. | `_safe_stem`, `cdcu_ripple_psd.analyze_series_for_reports`, `cdcu_ripple_psd.recommended_welch_nperseg`, `prepare_scope_dataframe`, `stability_metrics`, `write_stability_reports` | `cdcu_dcbus_fft.py:analyze_dcbus_dataframe`, `cdcu_scope_fft.py:analyze_scope_csv` | `ch_dir.mkdir`, `destination.mkdir`, `pd.DataFrame` |
| `analyze_scope_csv` | Load an oscilloscope CSV and analyze 1-4 selected channels. | `analyze_scope_dataframe` | `cdcu_scope_fft.py:_main` | `kwargs.pop`, `path.is_file`, `pd.read_csv` |
| `_main` | Parse command-line arguments, run the requested analysis workflow, and return a process exit code. | `analyze_scope_csv`, `parse_channel_spec` | — | `argparse.ArgumentParser`, `k.startswith`, `p.add_argument`, `p.error`, `p.parse_args` |

## `magnet_load_diagnostics.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `dataclasses`, `math`, `re`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_finite` | Return True only when *value* can be represented as a finite float. | — | `magnet_load_diagnostics.py:deviation`, `magnet_load_diagnostics.py:estimate_didt`, `magnet_load_diagnostics.py:estimated_inductance`, `magnet_load_diagnostics.py:extrapolate_at_current`, `magnet_load_diagnostics.py:max_slew_rate`, `magnet_load_diagnostics.py:measured_resistance`, `magnet_load_diagnostics.py:parse_nameplate` | `math.isfinite` |
| `parse_nameplate` | Read magnet R/L from explicit load-map fields or the legacy load_desc text. | `_finite` | — | `entry.get`, `match.group`, `re.search` |
| `measured_resistance` | Return the steady-state DC load resistance V/I in ohms. | `_finite` | — | — |
| `estimate_didt` | Estimate dI/dt from two consecutive live-monitor samples. | `_finite` | — | — |
| `estimated_inductance` | Estimate magnet inductance from L=(V-RI)/(dI/dt), returned in henries. | `_finite` | — | — |
| `deviation` | Return measured-reference as absolute value, percent, and ppm of reference. | `_finite` | — | — |
| `extrapolate_at_current` | Return predicted steady-state magnet voltage and I^2R power at target current. | `_finite` | — | — |
| `max_slew_rate` | Estimate positive dI/dt headroom at target current from (Vmax-I*R)/L. | `_finite` | — | — |

## `one_liners.py`

**Project-module dependencies:** `cdcu_load_map`

**Python / third-party libraries:** `argparse`, `datetime`, `os`, `socket`, `subprocess`, `sys`, `time`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `_format_runtime` | Return elapsed time in seconds and HH:MM:SS.s form. | — | `cdcu_monitor.py:_run_parallel_hosts`, `one_liners.py:main` | — |
| `probe_ip` | Return True if a TCP connection to ip:port succeeds within *timeout* s. | — | `one_liners.py:main` | `socket.create_connection` |
| `resolve_ips` | Return a list of (ip, load_entry) tuples for the cabinet. | `lm.list_cabinets`, `lm.list_ips`, `lm.lookup_soft` | `one_liners.py:main` | `os.path.isfile`, `sys.exit` |
| `build_command` | Build the argv list for one cdcu_monitor.py invocation. | — | `one_liners.py:main` | `cmd.append` |
| `main` | Run the module self-test or command-line workflow and return an operating-system process status code. | `_format_runtime`, `build_command`, `lm.list_cabinets`, `lm.list_ips`, `lm.lookup_soft`, `probe_ip`, `resolve_ips` | — | `_proc.poll`, `_program_start_local.strftime`, `ap.add_argument`, `ap.error`, `ap.parse_args`, `argparse.ArgumentParser`, `completion_times.get`, `datetime.now`, `e.get`, `entry.get`, `ip.replace`, `launch_times.get`, `…` |

## `power_supply_analytics_gui.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `PySide6`, `pathlib`, `psa_gui_config`, `sys`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `__init__` | Build the main window from a validated repository configuration. | `self._apply_defaults`, `self._build_analysis_group`, `self._build_command_group`, `self._build_console_group`, `self._build_ip_group`, `self._build_target_group`, `self._refresh_analysis_panel`, `self._refresh_command_preview`, `self._refresh_station_choices`, `self._refresh_target_mode` | — | `page.addWidget`, `self.resize`, `self.setCentralWidget`, `self.setWindowTitle` |
| `_build_target_group` | Create Storage Ring and test-stand target selectors. | — | `power_supply_analytics_gui.py:__init__` | `layout.addLayout`, `layout.addWidget`, `ring_form.addRow`, `self.cabinet.addItems`, `self.cabinet.currentTextChanged.connect`, `self.location.addItems`, `self.location.currentTextChanged.connect`, `self.sector.addItems`, `self.sector.currentTextChanged.connect`, `self.station.currentTextChanged.connect`, `self.target_mode.addItems`, `self.target_mode.currentTextChanged.connect`, `…` |
| `_build_ip_group` | Create the eight-port CDCU IP selector with select/clear controls. | `self._set_all_ips` | `power_supply_analytics_gui.py:__init__` | `buttons.addStretch`, `buttons.addWidget`, `check.stateChanged.connect`, `clear_all.clicked.connect`, `grid.addWidget`, `layout.addLayout`, `select_all.clicked.connect` |
| `_build_analysis_group` | Create workflow selection and workflow-specific input controls. | `self._build_dcbus_panel`, `self._build_live_panel`, `self._build_pmm_panel`, `self._build_scope_panel` | `power_supply_analytics_gui.py:__init__` | `layout.addLayout`, `layout.addWidget`, `selector_row.addStretch`, `selector_row.addWidget`, `self.analysis.addItems`, `self.analysis.currentTextChanged.connect`, `self.analysis_stack.addWidget` |
| `_build_live_panel` | Create live-monitor duration, polling, output, and plotting controls. | — | `power_supply_analytics_gui.py:_build_analysis_group` | `browse.clicked.connect`, `form.addRow`, `out_row.addWidget`, `out_wrapper.setLayout`, `self.duration.setDecimals`, `self.duration.setRange`, `self.duration.setSuffix`, `self.duration.valueChanged.connect`, `self.individual_plots.stateChanged.connect`, `self.interval.setDecimals`, `self.interval.setRange`, `self.interval.setSuffix`, `…` |
| `_build_file_row` | Return a reusable line-edit plus Browse button row for CSV workflows. | — | `power_supply_analytics_gui.py:_build_dcbus_panel`, `power_supply_analytics_gui.py:_build_pmm_panel`, `power_supply_analytics_gui.py:_build_scope_panel` | `button.clicked.connect`, `row.addWidget`, `row.setContentsMargins` |
| `_build_pmm_panel` | Create PMM CSV spectral-analysis controls. | `self._browse_csv`, `self._build_file_row` | `power_supply_analytics_gui.py:_build_analysis_group` | `form.addRow`, `self.pmm_csv.textChanged.connect`, `self.pmm_fft_y.addItems`, `self.pmm_fft_y.currentTextChanged.connect`, `self.pmm_load_desc.textChanged.connect`, `self.pmm_model.addItems`, `self.pmm_model.currentTextChanged.connect` |
| `_build_dcbus_panel` | Create the standardized two-channel external DCBus workflow controls. | `self._browse_csv`, `self._build_file_row` | `power_supply_analytics_gui.py:_build_analysis_group` | `form.addRow`, `self.dcbus_assume.stateChanged.connect`, `self.dcbus_csv.textChanged.connect`, `self.dcbus_iref.setPlaceholderText`, `self.dcbus_iref.textChanged.connect`, `self.dcbus_vref.setPlaceholderText`, `self.dcbus_vref.textChanged.connect` |
| `_build_scope_panel` | Create generic one-to-four-channel oscilloscope workflow controls. | `self._browse_csv`, `self._build_file_row` | `power_supply_analytics_gui.py:_build_analysis_group` | `edit.setPlaceholderText`, `edit.textChanged.connect`, `form.addRow`, `self.scope_channels.append`, `self.scope_csv.textChanged.connect`, `self.scope_sample_rate.setPlaceholderText`, `self.scope_sample_rate.textChanged.connect` |
| `_build_command_group` | Create transparent command preview and execution controls. | — | `power_supply_analytics_gui.py:__init__` | `controls.addStretch`, `controls.addWidget`, `fixed.setStyleHint`, `layout.addLayout`, `layout.addWidget`, `self.command_preview.setFont`, `self.command_preview.setMaximumBlockCount`, `self.command_preview.setReadOnly`, `self.run_button.clicked.connect`, `self.stop_button.clicked.connect`, `self.stop_button.setEnabled`, `validate_button.clicked.connect` |
| `_build_console_group` | Create the live stdout/stderr console used during a launched workflow. | — | `power_supply_analytics_gui.py:__init__` | `fixed.setStyleHint`, `layout.addWidget`, `self.console.setFont`, `self.console.setMaximumBlockCount`, `self.console.setReadOnly` |
| `_apply_defaults` | Apply repository defaults without hard-coding operational selections in widgets. | — | `power_supply_analytics_gui.py:__init__` | `defaults.get`, `self.analysis.setCurrentText`, `self.cabinet.setCurrentText`, `self.duration.setValue`, `self.interval.setValue`, `self.location.setCurrentText`, `self.sector.setCurrentText`, `self.target_mode.setCurrentText` |
| `_refresh_target_mode` | Switch between ring and test-stand selectors and refresh the command. | `self._refresh_command_preview` | `power_supply_analytics_gui.py:__init__` | `self.target_mode.currentText`, `self.target_stack.setCurrentIndex` |
| `_refresh_station_choices` | Limit station choices to those explicitly defined for the selected location. | `self._refresh_command_preview`, `self.config.stations_for` | `power_supply_analytics_gui.py:__init__` | `self.config.defaults.get`, `self.location.currentText`, `self.station.addItems`, `self.station.blockSignals`, `self.station.clear`, `self.station.currentText`, `self.station.setCurrentText` |
| `_refresh_analysis_panel` | Show only the inputs required by the selected analysis module. | `self._refresh_command_preview` | `power_supply_analytics_gui.py:__init__` | `self.ANALYSES.index`, `self.analysis.currentText`, `self.analysis_stack.setCurrentIndex` |
| `_set_all_ips` | Set all configured IP checkboxes to the requested state. | `self._refresh_command_preview` | `power_supply_analytics_gui.py:_build_ip_group` | `check.setChecked`, `self._ip_checks.values` |
| `_selected_ips` | Return selected addresses in configured physical-port order. | — | `power_supply_analytics_gui.py:_build_command`, `power_supply_analytics_gui.py:_validation_errors` | — |
| `_target` | Build a typed target object from the currently visible selectors. | — | `power_supply_analytics_gui.py:_build_command`, `power_supply_analytics_gui.py:_validation_errors` | `self.cabinet.currentText`, `self.location.currentText`, `self.sector.currentText`, `self.station.currentText`, `self.target_mode.currentText` |
| `_output_directory` | Resolve the operator-entered output directory without creating it. | — | `power_supply_analytics_gui.py:_build_command`, `power_supply_analytics_gui.py:_run_selected` | `self.outdir.text` |
| `_build_command` | Build the selected module command using the module's existing CLI contract. | `build_live_monitor_command`, `self._output_directory`, `self._selected_ips`, `self._target` | `power_supply_analytics_gui.py:_refresh_command_preview`, `power_supply_analytics_gui.py:_run_selected` | `command.append`, `edit.text`, `self.analysis.currentText`, `self.dcbus_assume.isChecked`, `self.dcbus_csv.text`, `self.dcbus_iref.text`, `self.dcbus_vref.text`, `self.duration.value`, `self.individual_plots.isChecked`, `self.interval.value`, `self.no_analysis.isChecked`, `self.pmm_csv.text`, `…` |
| `_validation_errors` | Validate selections and file requirements before starting a subprocess. | `self._selected_ips`, `self._target`, `self._validate_csv_path`, `self._validate_optional_float`, `validate_ip_selection`, `validate_target` | `power_supply_analytics_gui.py:_run_selected`, `power_supply_analytics_gui.py:_validate_dialog` | `edit.text`, `errors.append`, `errors.extend`, `self.analysis.currentText`, `self.dcbus_csv.text`, `self.dcbus_iref.text`, `self.dcbus_vref.text`, `self.duration.value`, `self.interval.value`, `self.pmm_csv.text`, `self.scope_csv.text`, `self.scope_sample_rate.text` |
| `_validate_csv_path` | Validate a required CSV path and return a GUI-ready error list. | — | `power_supply_analytics_gui.py:_validation_errors` | `path.is_file`, `value.strip` |
| `_validate_optional_float` | Validate an optional numeric field without forcing the operator to use it. | — | `power_supply_analytics_gui.py:_validation_errors` | `value.strip` |
| `_refresh_command_preview` | Update the command preview; display incomplete fields without raising dialogs. | `format_command`, `self._build_command` | `power_supply_analytics_gui.py:__init__`, `power_supply_analytics_gui.py:_refresh_analysis_panel`, `power_supply_analytics_gui.py:_refresh_station_choices`, `power_supply_analytics_gui.py:_refresh_target_mode`, `power_supply_analytics_gui.py:_set_all_ips` | `self.command_preview.setPlainText` |
| `_validate_dialog` | Present a complete validation result before the operator commits to a run. | `self._validation_errors` | — | `QMessageBox.information`, `QMessageBox.warning` |
| `_run_selected` | Launch the selected existing Python module and stream its output into the GUI. | `format_command`, `self._build_command`, `self._output_directory`, `self._validation_errors` | — | `QMessageBox.information`, `QMessageBox.warning`, `QProcessEnvironment.systemEnvironment`, `environment.insert`, `self.analysis.currentText`, `self.console.appendPlainText`, `self.process.errorOccurred.connect`, `self.process.finished.connect`, `self.process.readyReadStandardOutput.connect`, `self.process.setProcessChannelMode`, `self.process.setProcessEnvironment`, `self.process.setWorkingDirectory`, `…` |
| `_read_process_output` | Decode merged subprocess output as UTF-8 and append it to the live console. | — | `power_supply_analytics_gui.py:_process_finished` | `data.decode`, `self.console.appendPlainText`, `self.process.readAllStandardOutput` |
| `_process_started` | Reflect a successfully launched process in the operator controls. | — | — | `self.run_button.setEnabled`, `self.status_label.setText`, `self.stop_button.setEnabled` |
| `_process_finished` | Restore controls and report the subprocess exit code. | `self._read_process_output` | — | `self.console.appendPlainText`, `self.run_button.setEnabled`, `self.status_label.setText`, `self.stop_button.setEnabled` |
| `_process_error` | Surface a QProcess launch/runtime error without hiding subprocess diagnostics. | — | — | `self.console.appendPlainText`, `self.process.errorString`, `self.status_label.setText` |
| `_stop_process` | Request a clean stop first, then allow Qt to terminate the child process. | — | — | `self.console.appendPlainText`, `self.process.state`, `self.process.terminate` |
| `_browse_outdir` | Open a directory chooser and update the live-monitor output path. | — | — | `QFileDialog.getExistingDirectory`, `self.outdir.setText`, `self.outdir.text` |
| `_browse_csv` | Open a CSV chooser and write the selected path into ``destination``. | — | `power_supply_analytics_gui.py:_build_dcbus_panel`, `power_supply_analytics_gui.py:_build_pmm_panel`, `power_supply_analytics_gui.py:_build_scope_panel` | `QFileDialog.getOpenFileName`, `destination.setText` |
| `main` | Create the Qt application and return its event-loop exit status. | `load_gui_config` | — | `app.exec`, `window.show` |

## `psa_gui_config.py`

**Project-module dependencies:** None

**Python / third-party libraries:** `dataclasses`, `importlib`, `ipaddress`, `json`, `pathlib`, `shlex`, `subprocess`, `sys`, `typing`

| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |
| --- | --- | --- | --- | --- |
| `monitor_sector` | Return the value supplied to ``cdcu_monitor.py --sector``. | — | — | — |
| `monitor_cabinet` | Return the value supplied to ``cdcu_monitor.py --cabinet``. | — | — | — |
| `label` | Return a concise human-readable target name for logs and previews. | — | — | — |
| `stations_for` | Return the allowed stations for ``location`` or an empty tuple. | — | `power_supply_analytics_gui.py:_refresh_station_choices`, `psa_gui_config.py:validate_target` | `self.locations.get` |
| `_inclusive_names` | Generate an inclusive, consistently formatted engineering identifier list. | — | `psa_gui_config.py:load_gui_config` | — |
| `load_gui_config` | Load and validate the GUI configuration file. | `_inclusive_names` | `power_supply_analytics_gui.py:main` | `config_path.is_file`, `config_path.open`, `json.load`, `json.loads`, `payload.get`, `raw.get`, `raw_locations.items`, `resource.read_text`, `resources.files`, `ring.get` |
| `validate_target` | Return all target-selection validation errors without stopping at the first. | `config.stations_for` | `power_supply_analytics_gui.py:_validation_errors` | `errors.append` |
| `validate_ip_selection` | Validate a multi-IP selection against the configured test-network pool. | — | `power_supply_analytics_gui.py:_validation_errors` | `errors.append` |
| `build_live_monitor_command` | Build the existing multi-IP live-monitor command without duplicating analysis logic. | — | `power_supply_analytics_gui.py:_build_command` | `command.append` |
| `format_command` | Return a copy/paste-friendly command preview with safe shell quoting. | — | `power_supply_analytics_gui.py:_refresh_command_preview`, `power_supply_analytics_gui.py:_run_selected` | `shlex.join`, `subprocess.list2cmdline`, `sys.platform.startswith` |

## Change-impact checklist

When a function changes, review its project callees, direct callers, module-level dependencies, and corresponding regression tests. If a result dictionary or CSV schema changes, update the AI data contract and report readers in the same change.
