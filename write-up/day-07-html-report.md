# Day 7 -- HTML Report Generation

**Date:** Monday, June 29, 2026
**Phase:** 4 -- Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Build the HTML report generation module (`reporter.py`) and wire it into the CLI as a `report` subcommand. The reporter takes the structured output from `run_commands()`, applies TextFSM parsing where templates exist, and renders a self-contained HTML report with a dark theme saved to `outputs/`.

---

## What Was Built

### `netmiko_tool/reporter.py`

`generate_report()` accepts the results dictionary from `run_commands()`, the list of commands that were run, and an optional output directory. For each device it iterates over the command output blocks, attempts to parse each one via `parse_output()`, and renders either an HTML table (if a template matched) or a `<pre>` block (if no template exists). This means the report degrades gracefully for commands that have no TextFSM template rather than failing or omitting them.

The HTML output is a single self-contained file with all styles inlined in a `<style>` block -- no external dependencies, no CDN calls, no JavaScript. The report can be opened directly in any browser and shared as a standalone file. The design uses a dark colour scheme consistent with a terminal-native tool: a near-black background (`#0f172a`), device cards in dark slate (`#1e293b`), command titles in purple (`#a78bfa`), and table headers and device names in sky blue (`#38bdf8`).

The filename format `YYYYMMDD-HHMMSS-report.html` places reports alongside timestamped output files in `outputs/`, keeping all tool artefacts in one place.

### `report` subcommand in `tool.py`

A `report` subcommand was added to the CLI. It accepts the same `--commands` and `--output-dir` flags as the `run` subcommand, runs the commands across all devices, passes the results to `generate_report()`, and prints the report path on completion.

---

## Smoke Test

The report subcommand was run with three commands:

```bash
python3 tool.py report --commands "/ip address print" "/ip route print" "/system identity print"
```

The report was generated and opened in the browser with `xdg-open`. The rendered report contained two device cards -- one for R1 and one for R2 -- each with:

- A structured table for `/ip address print` parsed via the TextFSM template
- A structured table for `/ip route print` parsed via the TextFSM template
- A `<pre>` block for `/system identity print`, which has no template, displaying the raw output

No deviations from expected behaviour.

---

## Screenshots

- `screenshots/12-report-cli.png` -- terminal output from `python3 tool.py report` showing connection logs and the saved report path
- `screenshots/13-report-browser-r1.png` -- rendered HTML report open in the browser showing the R1 device card with parsed tables
- `screenshots/14-report-browser-r2.png` -- rendered HTML report showing the R2 device card with parsed tables

---

## Files Changed

| File | Status |
|---|---|
| `netmiko_tool/reporter.py` | Created |
| `netmiko_tool/__init__.py` | Updated |
| `tool.py` | Updated |

---

## Commit

```
feat: add HTML report generation and report subcommand to CLI
```