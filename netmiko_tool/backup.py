from datetime import datetime
from pathlib import Path
from .connector import connect, disconnect
from .utils import load_devices


def backup_configs(
    inventory_path: str = "devices.yaml",
    backup_dir: str = "backups",
) -> dict:
    """Pull the running configuration from all devices and save to disk.

    Args:
        inventory_path: Path to the YAML inventory file.
        backup_dir: Directory where backup files are saved.

    Returns:
        Dictionary mapping device name to the saved backup file path,
        or an error string if the device was unreachable.
    """
    devices = load_devices(inventory_path)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)

    results = {}

    for device in devices:
        name = device.get("name", device.get("host", "unknown"))
        connection = connect(device)

        if connection is None:
            results[name] = "ERROR: could not connect"
            continue

        running_config = connection.send_command("/export")
        disconnect(connection, name=name)

        filename = f"{timestamp}-{name}-backup.txt"
        file_path = backup_path / filename

        with open(file_path, "w") as f:
            f.write(f"# Device: {name}\n")
            f.write(f"# Backup timestamp: {timestamp}\n")
            f.write("#" + "-" * 59 + "\n\n")
            f.write(running_config)

        results[name] = str(file_path)
        print(f"[+] Backup saved to {file_path}")

    return results