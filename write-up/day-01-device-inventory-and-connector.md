# Day 1 -Device Inventory and Connection Handler

**Date:** Monday, June 29, 2026
**Phase:** 4 -Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Begin the core Python modules for the automation tool. Day 1 focused on two foundational pieces: the device inventory loader (`utils.py`) and the SSH connection handler (`connector.py`). Every other module in this project depends on these two, so getting them right first was the priority.

---

## What Was Built

### Device Inventory (`devices.yaml` and `devices.yaml.example`)

The project uses a YAML file as a single source of truth for all target devices. This keeps device details out of the code and makes the tool easy to adapt to any environment by swapping one file.

`devices.yaml` is git-ignored because it contains real credentials. A `devices.yaml.example` file is committed in its place so anyone cloning the repo knows the expected structure without being exposed to live credentials.

The inventory for the lab defines both routers:

- **R1** at `10.10.10.10`, reachable directly over the TAP interface
- **R2** at `10.0.0.2`, reachable via the static route through R1

Both use `device_type: mikrotik_routeros`, which is Netmiko's native support for MikroTik RouterOS.

---

### Inventory Loader (`netmiko_tool/utils.py`)

`load_devices()` reads the YAML file, validates that the `devices` key is present, and returns a list of device dictionaries. It raises explicit, descriptive exceptions rather than letting a raw Python error surface -- `FileNotFoundError` if the inventory file is missing, `KeyError` if the structure is wrong. This makes misconfiguration easy to diagnose.

---

### Connection Handler (`netmiko_tool/connector.py`)

`connect()` wraps Netmiko's `ConnectHandler`. It accepts a device dictionary, attempts the SSH connection, and returns the live connection object on success or `None` on failure. Three failure modes are handled explicitly:

- `NetmikoTimeoutException` -- the device was unreachable (wrong IP, lab not running, routing missing)
- `NetmikoAuthenticationException` -- credentials were rejected
- A bare `Exception` catch for anything unexpected

Returning `None` on failure rather than raising means callers can iterate over a device list and skip unreachable hosts without crashing the whole run.

`disconnect()` is a thin wrapper that calls `.disconnect()` on the connection object and logs the result. Keeping disconnection explicit rather than relying on garbage collection is a good habit in tools that may manage many simultaneous sessions.

---

### Package Exports (`netmiko_tool/__init__.py`)

`connect`, `disconnect`, and `load_devices` are exported from the package root so any module can import them cleanly:

```python
from netmiko_tool import connect, disconnect, load_devices
```

---

## Smoke Test

With the lab running (both routers up, TAP interface live, static route to `10.0.0.0/30` in place), a quick inline script exercised the full connect/disconnect cycle against both devices:

```
[+] Connecting to R1 (10.10.10.10)...
[+] Connected to R1.
[+] Disconnected from R1.
[+] Connecting to R2 (10.0.0.2)...
[+] Connected to R2.
[+] Disconnected from R2.
```

Both connections succeeded on the first attempt.

---

## Pylance False Positive

VSCode's Pylance extension flagged `reportMissingImports` on the Netmiko imports in `connector.py`. This was not a real error -- the smoke test had already confirmed the imports work at runtime. The cause was that Pylance was not pointed at the project's virtual environment interpreter. Selecting `.venv/bin/python` via **Python: Select Interpreter** cleared the warnings immediately.

---

## Files Changed

| File | Status |
|---|---|
| `devices.yaml` | Created (git-ignored) |
| `devices.yaml.example` | Updated with real structure |
| `netmiko_tool/utils.py` | Written |
| `netmiko_tool/connector.py` | Written |
| `netmiko_tool/__init__.py` | Updated |

---

## Commit

```
feat: add device inventory loader and connection handler
```