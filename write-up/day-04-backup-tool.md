# Day 4 -- Backup Tool

**Date:** Monday, June 29, 2026
**Phase:** 4 -- Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Build the backup module (`backup.py`). This module connects to every device in the inventory, pulls the full running configuration using MikroTik's `/export` command, and saves a timestamped backup file per device to the `backups/` directory.

---

## What Was Built

### `netmiko_tool/backup.py`

`backup_configs()` accepts an optional inventory path and backup directory. The `backups/` directory is created automatically if it does not exist, consistent with how `executor.py` handles `outputs/`.

For each device, the running config is retrieved with `send_command("/export")`. MikroTik's `/export` command produces a complete, human-readable dump of the device configuration in a format that can be pasted back into a RouterOS terminal to restore the device to that state -- making it a natural choice for backups over alternatives like `/system backup save`, which produces a binary file.

Each backup file is written with a three-line comment header (device name, timestamp, separator) before the raw export output. This makes backup files self-describing when browsed outside of the tool. The filename format `YYYYMMDD-HHMMSS-<name>-backup.txt` keeps them sortable and clearly associated with their source device.

The function returns a dictionary mapping device name to the saved file path, or an error string if the connection failed, consistent with the return pattern used across the rest of the package.

---

## Smoke Test

`backup_configs()` was run against both routers. Both connected successfully and the `/export` command returned the full running configuration for each device. Two backup files were created under `backups/`:

```
backups/<timestamp>-R1-backup.txt
backups/<timestamp>-R2-backup.txt
```

Spot-checking the R1 backup confirmed it contained the complete device state including interface addresses, routing table entries, and the DNS and NTP settings applied during the Day 3 config push -- confirming that `backup_configs()` captures the live state of the device at the time of the run. No deviations from the expected behaviour.

---

## Screenshots

- `screenshots/05-backup-logs.png` -- terminal output showing connection logs and saved backup file paths for both routers
- `screenshots/06-backup-file-contents.png` -- contents of the R1 backup file confirming the full `/export` output including previously pushed DNS and NTP config

---

## Files Changed

| File | Status |
|---|---|
| `netmiko_tool/backup.py` | Written |
| `netmiko_tool/__init__.py` | Updated |

---

## Commit

```
feat: add backup tool to pull and save running configs
```