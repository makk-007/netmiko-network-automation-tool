#!/usr/bin/env python3
"""Netmiko Network Automation Tool

A command-line tool for automating network operations across multiple
devices using Netmiko. Supports command execution, config pushing,
and configuration backups via a YAML device inventory.

Usage:
    python tool.py run --commands "/system identity print" "/ip address print"
    python tool.py push --config configs/example-config.txt
    python tool.py backup
"""

import argparse
import sys
from netmiko_tool import run_commands, push_config, backup_configs


def handle_run(args):
    """Handle the 'run' subcommand."""
    print(f"[*] Running {len(args.commands)} command(s) on all devices...\n")
    results = run_commands(
        commands=args.commands,
        inventory_path=args.inventory,
        output_dir=args.output_dir,
    )
    for device, output in results.items():
        print(f"\n{'='*60}")
        print(f"Device: {device}")
        print(output)


def handle_push(args):
    """Handle the 'push' subcommand."""
    print(f"[*] Pushing config from {args.config} to all devices...\n")
    results = push_config(
        config_file=args.config,
        inventory_path=args.inventory,
    )
    for device, output in results.items():
        print(f"\n{'='*60}")
        print(f"Device: {device}")
        print(output)


def handle_backup(args):
    """Handle the 'backup' subcommand."""
    print("[*] Backing up running configs from all devices...\n")
    results = backup_configs(
        inventory_path=args.inventory,
        backup_dir=args.backup_dir,
    )
    print("\n[*] Backup summary:")
    for device, path in results.items():
        print(f"    {device}: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tool.py",
        description="Netmiko Network Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python tool.py run --commands "/system identity print" "/ip address print"
  python tool.py push --config configs/example-config.txt
  python tool.py backup
  python tool.py backup --inventory devices.yaml --backup-dir backups/
        """,
    )

    parser.add_argument(
        "--inventory",
        default="devices.yaml",
        help="Path to the YAML device inventory file (default: devices.yaml)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run show commands across all devices",
    )
    run_parser.add_argument(
        "--commands",
        nargs="+",
        required=True,
        metavar="CMD",
        help="One or more commands to run on each device",
    )
    run_parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory to save command output files (default: outputs)",
    )
    run_parser.set_defaults(func=handle_run)

    # push subcommand
    push_parser = subparsers.add_parser(
        "push",
        help="Push a config file to all devices",
    )
    push_parser.add_argument(
        "--config",
        required=True,
        metavar="FILE",
        help="Path to the config file to push",
    )
    push_parser.set_defaults(func=handle_push)

    # backup subcommand
    backup_parser = subparsers.add_parser(
        "backup",
        help="Pull and save running configs from all devices",
    )
    backup_parser.add_argument(
        "--backup-dir",
        default="backups",
        help="Directory to save backup files (default: backups)",
    )
    backup_parser.set_defaults(func=handle_backup)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
