from pathlib import Path
from .connector import connect, disconnect
from .utils import load_devices


def push_config(
    config_file: str,
    inventory_path: str = "devices.yaml",
) -> dict:
    """Push a configuration block to all devices in the inventory.

    Reads commands from a plain text file (one command per line, blank
    lines and lines starting with '#' are ignored) and sends them to
    each device using Netmiko's send_config_set().

    Args:
        config_file: Path to the text file containing config commands.
        inventory_path: Path to the YAML inventory file.

    Returns:
        Dictionary mapping device name to the output returned by the
        device after applying the config, or an error string on failure.
    """
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    raw_lines = config_path.read_text().splitlines()
    commands = [
        line for line in raw_lines
        if line.strip() and not line.strip().startswith("#")
    ]

    if not commands:
        raise ValueError(f"No commands found in {config_file}")

    print(f"[*] Loaded {len(commands)} command(s) from {config_file}")

    devices = load_devices(inventory_path)
    results = {}

    for device in devices:
        name = device.get("name", device.get("host", "unknown"))
        connection = connect(device)

        if connection is None:
            results[name] = "ERROR: could not connect"
            continue

        output = connection.send_config_set(commands)
        disconnect(connection, name=name)

        results[name] = output
        print(f"[+] Config pushed to {name}.")

    return results