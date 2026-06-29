# Day 5 -- CLI Entry Point

**Date:** Monday, June 29, 2026
**Phase:** 4 -- Netmiko Network Automation Tool
**Repository:** `netmiko-network-automation-tool`

---

## Objective

Build the main CLI entry point (`tool.py`) using argparse, tying all four core modules together into a single runnable script. This was originally scoped for Week 3 but was pulled forward given that all core modules were completed on Day 1.

---

## What Was Built

### `tool.py`

`tool.py` is the top-level entry point for the tool. It defines three subcommands -- `run`, `push`, and `backup` -- each mapping directly to one of the core modules built in Days 2 through 4.

**Parser structure:**

A root parser handles the global `--inventory` flag, which defaults to `devices.yaml` but can be overridden to point at any inventory file. This flag is available to all three subcommands without needing to be redefined on each one.

Each subcommand is registered via `add_subparsers()` and bound to a handler function via `set_defaults(func=...)`. The `main()` function simply parses arguments and calls `args.func(args)`, keeping the dispatch logic minimal.

**Subcommands:**

- `run --commands CMD [CMD ...]` -- accepts one or more commands via `nargs="+"` and passes them to `run_commands()`. The `--output-dir` flag allows overriding the default `outputs/` directory.
- `push --config FILE` -- accepts a path to a config file and passes it to `push_config()`.
- `backup` -- calls `backup_configs()` with an optional `--backup-dir` override and prints a summary of saved file paths on completion.

The module docstring includes usage examples that also appear in the `--help` epilog, so the tool is self-documenting from the command line.

---

## Smoke Test

All three subcommands were exercised from the CLI. Commands were invoked using `python3` rather than `python`, which is the correct convention on Ubuntu 24.04 where the `python` symlink is not guaranteed to exist.

```bash
python3 tool.py run --commands "/system identity print" "/ip address print"
python3 tool.py push --config configs/example-config.txt
python3 tool.py backup
```

All three ran cleanly against both routers with output consistent with previous days. The `--help` output was also verified:

```bash
python3 tool.py --help
python3 tool.py run --help
```

No deviations beyond the `python3` invocation.

---

## Screenshots

- `screenshots/07-cli-run.png` -- CLI output from `python3 tool.py run`
- `screenshots/08-cli-push.png` -- CLI output from `python3 tool.py push`
- `screenshots/09-cli-backup.png` -- CLI output from `python3 tool.py backup`
- `screenshots/10-cli-help.png` -- `--help` output showing subcommands and usage

---

## Files Changed

| File | Status |
|---|---|
| `tool.py` | Written |

---

## Commit

```
feat: add argparse CLI entry point with run, push, and backup subcommands
```