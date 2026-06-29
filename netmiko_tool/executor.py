from datetime import datetime
from pathlib import Path
from .connector import connect, disconnect
from .utils import load_devices


def run_commands(
    commands: list[str],
    inventory_path: str = "devices.yaml",
    output_dir: str = "outputs",
) -> dict:
    """Run a list of show commands across all devices in the inventory.

    Args:
        commands: List of CLI commands to execute on each device.
        inventory_path: Path to the YAML inventory file.
        output_dir: Directory where timestamped output files are saved.

    Returns:
        Dictionary mapping device name to command output string,
        or an error message string if the device was unreachable.
    """
    devices = load_devices(inventory_path)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}

    for device in devices:
        name = device.get("name", device.get("host", "unknown"))
        connection = connect(device)

        if connection is None:
            results[name] = "ERROR: could not connect"
            continue

        device_output_lines = []

        for command in commands:
            output = connection.send_command(command)
            device_output_lines.append(f"### {command}\n{output}")

        disconnect(connection, name=name)

        full_output = "\n\n".join(device_output_lines)
        results[name] = full_output

        filename = f"{timestamp}-{name}.txt"
        file_path = output_path / filename
        with open(file_path, "w") as f:
            f.write(f"Device: {name}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Commands: {', '.join(commands)}\n")
            f.write("-" * 60 + "\n\n")
            f.write(full_output)

        print(f"[+] Output saved to {file_path}")

    return results