# Day 6 -- TextFSM Structured Output Parsing

**Date:** Monday, June 29, 2026
**Phase:** 4 -- Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Add structured output parsing to the tool using TextFSM. Rather than storing and displaying raw text from device commands, the tool can now extract structured data -- lists of dictionaries -- from command output when a matching template exists. This lays the groundwork for HTML report generation in Day 7.

---

## What Was Built

### TextFSM Templates (`templates/`)

Two templates were written for the MikroTik commands used throughout the project:

**`templates/mikrotik_ip_address_print.textfsm`** -- extracts the index, address (with prefix), network, and interface name from each row of `/ip address print` output.

**`templates/mikrotik_ip_route_print.textfsm`** -- extracts flags, destination address, gateway, routing table, and distance from each row of `/ip route print` output.

TextFSM templates work by defining named `Value` fields with regex patterns, then specifying state transitions and line-matching rules in a `Start` block. Each line of device output is matched against the rules in order; when a `Record` action fires, the current field values are saved as a row and the fields reset for the next entry.

---

### `parse_output()` in `netmiko_tool/utils.py`

`parse_output()` accepts a command string and the raw output from that command, then attempts to find and apply a matching TextFSM template. The template lookup converts the command to a filename slug: the leading slash is stripped, remaining slashes and spaces are replaced with underscores, and `mikrotik_` is prepended with `.textfsm` appended. So `/ip address print` resolves to `mikrotik_ip_address_print.textfsm`.

If no template file exists for the command, the function returns `None` so the caller can fall back to raw output gracefully. If a template is found, `TextFSM.ParseText()` processes the output and the result is zipped with the template headers to produce a list of dictionaries -- one per matched row.

This design keeps template lookup convention-based rather than requiring a registry or configuration file. Adding support for a new command is as simple as dropping a new `.textfsm` file into the `templates/` directory.

---

## Smoke Test

`run_commands()` was called with `/ip address print` and `/ip route print` against both routers. The raw output blocks were passed through `parse_output()` for each command. Both templates matched and returned structured data:

- `/ip address print` produced one dictionary per interface entry, with keys `INDEX`, `ADDRESS`, `NETWORK`, and `INTERFACE`
- `/ip route print` produced one dictionary per route entry, with keys `FLAGS`, `DST_ADDRESS`, `GATEWAY`, `ROUTING_TABLE`, and `DISTANCE`

Commands with no matching template fell back to raw output as expected. No deviations.

---

## Screenshot

- `screenshots/11-textfsm-parsed-output.png` -- terminal output showing structured dictionaries for both routers across both parsed commands

---

## Files Changed

| File | Status |
|---|---|
| `netmiko_tool/utils.py` | Updated |
| `netmiko_tool/__init__.py` | Updated |
| `templates/mikrotik_ip_address_print.textfsm` | Created |
| `templates/mikrotik_ip_route_print.textfsm` | Created |
| `requirements.txt` | Updated |

---

## Commit

```
feat: add TextFSM structured output parsing with MikroTik templates
```