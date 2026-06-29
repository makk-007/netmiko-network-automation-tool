import yaml
from pathlib import Path


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