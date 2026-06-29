# Day 3 -- Config Pusher

**Date:** Monday, June 29, 2026
**Phase:** 4 -- Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Build the config pusher module (`config_pusher.py`). This module reads a block of configuration commands from a plain text file and pushes them to every device in the inventory using Netmiko's `send_config_set()`.

---

## What Was Built

### `configs/example-config.txt`

The example config file was updated with two safe, non-destructive MikroTik commands suitable for lab testing:

```
/ip dns set servers=8.8.8.8,8.8.4.4
/system ntp client set enabled=yes servers=pool.ntp.org
```

These set the DNS resolvers to Google's public servers and enable NTP syncing against `pool.ntp.org`. Both are easy to verify after the push and easy to revert, making them appropriate for a smoke test against a live lab.

---

### `netmiko_tool/config_pusher.py`

`push_config()` accepts a path to a config file and an optional inventory path. Before attempting any connections, it reads and validates the config file: blank lines and comment lines (starting with `#`) are stripped out, and a `ValueError` is raised if nothing remains. This prevents a silent no-op where the tool connects to every device and sends nothing.

The cleaned command list is passed directly to `send_config_set()`, which handles the RouterOS session context and sends each command in sequence. The device's response is captured and returned in a dictionary keyed by device name, consistent with the pattern established in `executor.py`.

Connection failures follow the same pattern as the rest of the package: `None` returned by `connect()` results in an error string entry in the results dictionary, and the loop moves on to the next device without aborting.

---

## Smoke Test

### Config Push

`push_config("configs/example-config.txt")` was run against both routers. Both connected successfully and accepted the config block without error.

### Verification

A follow-up `run_commands()` call checked that the settings had actually landed:

```
/ip dns print
/system ntp client print
```

Both routers returned `8.8.8.8` and `8.8.4.4` as their DNS servers and confirmed NTP was enabled with `pool.ntp.org` as the server. The config push worked as expected on the first attempt with no deviations.

---

## Screenshots

- `screenshots/02-config-pusher-logs.png` -- terminal output from the config push showing connection logs and confirmation that config was pushed to R1 and R2
- `screenshots/03-config-pusher-verification-r1.png` -- verification run output for R1 showing DNS and NTP settings
- `screenshots/04-config-pusher-verification-r2.png` -- verification run output for R2 showing DNS and NTP settings

---

## Files Changed

| File | Status |
|---|---|
| `netmiko_tool/config_pusher.py` | Written |
| `netmiko_tool/__init__.py` | Updated |
| `configs/example-config.txt` | Updated |

---

## Commit

```
feat: add config pusher using send_config_set
```