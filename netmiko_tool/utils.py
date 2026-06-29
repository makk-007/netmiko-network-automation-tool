import yaml
import textfsm
from pathlib import Path
from io import StringIO


def load_devices(inventory_path: str = "devices.yaml") -> list[dict]:
    """Load device inventory from a YAML file.

    Args:
        inventory_path: Path to the YAML inventory file.

    Returns:
        List of device dictionaries.

    Raises:
        FileNotFoundError: If the inventory file does not exist.
        KeyError: If the YAML file is missing the 'devices' key.
    """
    path = Path(inventory_path)
    if not path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if "devices" not in data:
        raise KeyError(f"'devices' key missing in {inventory_path}")

    return data["devices"]


def parse_output(command: str, raw_output: str, template_dir: str = "templates") -> list[dict] | None:
    """Parse raw command output using a TextFSM template.

    Template files are looked up by converting the command to a filename:
    spaces and slashes are replaced with underscores, leading underscores
    stripped, and '.textfsm' appended.

    For example:
        '/ip address print' -> 'mikrotik_ip_address_print.textfsm'

    Args:
        command: The CLI command whose output is being parsed.
        raw_output: The raw string output returned by the device.
        template_dir: Directory containing TextFSM template files.

    Returns:
        List of dictionaries, one per matched row, or None if no
        matching template exists.
    """
    slug = command.strip().lstrip("/").replace("/", "_").replace(" ", "_")
    template_path = Path(template_dir) / f"mikrotik_{slug}.textfsm"

    if not template_path.exists():
        return None

    with open(template_path) as f:
        fsm = textfsm.TextFSM(f)

    parsed = fsm.ParseText(raw_output)
    headers = fsm.header

    return [dict(zip(headers, row)) for row in parsed]