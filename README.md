# Netmiko Network Automation Tool

A Python command-line tool for automating network operations across multiple devices using [Netmiko](https://github.com/ktbyers/netmiko). Supports running show commands, pushing configuration blocks, backing up running configs, and generating structured HTML reports -- all driven by a YAML device inventory.

---

## Features

- **Command executor** -- run one or more show commands across all devices and save timestamped output files
- **Config pusher** -- push a configuration block from a plain text file to all devices using `send_config_set()`
- **Backup tool** -- pull the full running configuration from each device and save timestamped backup files
- **HTML report generation** -- run commands and render a self-contained HTML report with structured tables where TextFSM templates exist, falling back to raw output otherwise
- **TextFSM parsing** -- structured output extraction for supported commands via template files in `templates/`
- **Graceful error handling** -- unreachable or unauthenticated devices are logged and skipped without aborting the run

---

## Lab Environment

This tool was developed and tested against a GNS3 virtual lab running two MikroTik CHR 7.22.1 routers connected via a TAP interface on Ubuntu 24.04 LTS. MikroTik CHR was chosen because Cisco IOS images require a licence and cannot be legally redistributed; Netmiko supports MikroTik natively via `device_type: mikrotik_routeros`.

Network topology:

```
[Ubuntu Host]
  10.10.10.1 (tap0)
       |
  [Cloud1 - tap0]
       |
      R1 (MikroTik CHR)
        ether1: 10.10.10.10/24
        ether2: 10.0.0.1/30
             |
            R2 (MikroTik CHR)
              ether1: 10.0.0.2/30
```

For full lab setup instructions including GNS3 configuration, TAP interface setup, VirtualBox quirks, and the lab startup sequence, see [`setup/lab-setup.md`](setup/lab-setup.md).

---

## Requirements

- Python 3.10+
- Netmiko 4.7.0
- TextFSM
- PyYAML

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

Copy the example inventory file and edit it to match your environment:

```bash
cp devices.yaml.example devices.yaml
nvim devices.yaml
```

`devices.yaml` is git-ignored and never committed. The example file documents the expected structure:

```yaml
devices:
  - name: R1
    host: 192.168.1.1
    device_type: mikrotik_routeros
    username: admin
    password: yourpassword
    port: 22
```

`device_type` should match the Netmiko driver for your platform. See the [Netmiko supported platforms list](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md) for all available options.

---

## Usage

Activate the virtual environment before running the tool:

```bash
source .venv/bin/activate
```

### Run show commands

Run one or more commands across all devices and save timestamped output to `outputs/`:

```bash
python3 tool.py run --commands "/ip address print" "/ip route print"
```

Override the output directory:

```bash
python3 tool.py run --commands "/system identity print" --output-dir my-outputs/
```

### Push a config

Push a configuration block from a text file to all devices:

```bash
python3 tool.py push --config configs/example-config.txt
```

The config file should contain one command per line. Blank lines and lines starting with `#` are ignored.

### Backup running configs

Pull the full running configuration from each device and save to `backups/`:

```bash
python3 tool.py backup
```

Override the backup directory:

```bash
python3 tool.py backup --backup-dir my-backups/
```

### Generate an HTML report

Run commands and generate a self-contained HTML report in `outputs/`:

```bash
python3 tool.py report --commands "/ip address print" "/ip route print" "/system identity print"
```

Open the report in a browser:

```bash
xdg-open outputs/<timestamp>-report.html
```

Commands with a matching TextFSM template in `templates/` are rendered as structured tables. Commands with no template fall back to a raw `<pre>` block.

### Global options

All subcommands accept an `--inventory` flag to override the default `devices.yaml` path:

```bash
python3 tool.py --inventory staging-devices.yaml backup
```

---

## Project Structure

```
netmiko-network-automation-tool/
├── tool.py                   # CLI entry point
├── requirements.txt
├── devices.yaml.example      # Inventory template (copy to devices.yaml)
├── netmiko_tool/
│   ├── __init__.py
│   ├── connector.py          # SSH connection handler
│   ├── executor.py           # Command executor
│   ├── config_pusher.py      # Config push via send_config_set()
│   ├── backup.py             # Running config backup
│   ├── reporter.py           # HTML report generation
│   └── utils.py              # Inventory loader and TextFSM parser
├── templates/                # TextFSM templates for structured parsing
├── configs/
│   └── example-config.txt    # Example config block
├── outputs/                  # Timestamped command output and reports (git-ignored)
├── backups/                  # Timestamped config backups (git-ignored)
├── screenshots/              # Lab and tool screenshots
├── setup/
│   └── lab-setup.md          # Full GNS3 lab setup documentation
└── write-up/                 # Day-by-day project write-ups
```

---

## TextFSM Templates

Templates live in `templates/` and are looked up by command name. The naming convention is:

```
mikrotik_<command_slug>.textfsm
```

Where the command slug is the command with the leading slash stripped, remaining slashes and spaces replaced with underscores. For example:

| Command | Template |
|---|---|
| `/ip address print` | `mikrotik_ip_address_print.textfsm` |
| `/ip route print` | `mikrotik_ip_route_print.textfsm` |

To add parsing support for a new command, add a `.textfsm` file to `templates/` following the same naming convention.