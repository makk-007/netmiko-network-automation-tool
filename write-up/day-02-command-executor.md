# Day 2 -- Command Executor

**Date:** Monday, June 29, 2026
**Phase:** 4 -- Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Build the command executor module (`executor.py`). This module takes a list of show commands, runs them against every device in the inventory over SSH, prints the output to the terminal, and saves a timestamped file per device to the `outputs/` directory.

---

## What Was Built

### `netmiko_tool/executor.py`

`run_commands()` is the single public function in this module. It accepts a list of CLI commands and two optional parameters: the path to the inventory file and the output directory. The flow for each device is:

1. Call `connect()` from `connector.py`. If it returns `None`, record an error string for that device and skip to the next one.
2. Iterate over every command, calling `send_command()` and collecting the output.
3. Call `disconnect()`.
4. Write a single timestamped file to `outputs/` containing a header block (device name, timestamp, commands run) followed by each command and its output.
5. Return a dictionary mapping device name to the full output string so callers can also work with the data in memory.

The timestamp format `YYYYMMDD-HHMMSS` is used for all output filenames, which keeps them sortable and unambiguous. The `outputs/` directory is created automatically if it does not exist, so there is nothing to set up manually before running the tool.

Error handling follows the same pattern established in `connector.py`: failures are caught and logged rather than raised, so a single unreachable device does not abort the run for the rest of the inventory.

---

## Smoke Test

Three commands were run against both routers simultaneously:

```
/system identity print
/ip address print
/ip route print
```

Both connections succeeded. Output files were saved:

```
outputs/20260629-110655-R1.txt
outputs/20260629-110655-R2.txt
```

The terminal output confirmed the expected network state of the lab:

**R1** showed two interfaces (`ether1` at `10.10.10.10/24`, `ether2` at `10.0.0.1/30`) and a full routing table including the default route via `10.10.10.1` (the TAP interface on the Ubuntu host) and a static route to `10.0.0.0/30`.

**R2** showed one interface (`ether1` at `10.0.0.2/30`) and only its directly connected route to `10.0.0.0/30`, plus a default route via `10.0.0.1`. R2 has no awareness of the `10.10.10.0/24` TAP subnet, which is expected given the lab topology.

---

## Screenshot

`screenshots/01-executor-output.png` -- terminal output from the smoke test showing connection logs, saved file paths, and full command output for both R1 and R2.

---

## Files Changed

| File | Status |
|---|---|
| `netmiko_tool/executor.py` | Written |
| `netmiko_tool/__init__.py` | Updated |

---

## Commit

```
feat: add command executor with timestamped output saving
```