from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


def connect(device: dict):
    """Establish an SSH connection to a network device via Netmiko.

    Args:
        device: Dictionary containing connection parameters. Must include
                'name', 'host', 'device_type', 'username', 'password'.
                'port' is optional (defaults to 22).

    Returns:
        An active Netmiko ConnectHandler instance, or None on failure.
    """
    name = device.get("name", device.get("host", "unknown"))
    params = {
        "host": device["host"],
        "device_type": device["device_type"],
        "username": device["username"],
        "password": device["password"],
        "port": device.get("port", 22),
    }

    try:
        print(f"[+] Connecting to {name} ({params['host']})...")
        connection = ConnectHandler(**params)
        print(f"[+] Connected to {name}.")
        return connection

    except NetmikoTimeoutException:
        print(f"[-] Timeout: could not reach {name} ({params['host']}).")
        return None

    except NetmikoAuthenticationException:
        print(f"[-] Authentication failed for {name} ({params['host']}).")
        return None

    except Exception as e:
        print(f"[-] Unexpected error connecting to {name}: {e}")
        return None


def disconnect(connection, name: str = "device") -> None:
    """Gracefully disconnect from a network device.

    Args:
        connection: An active Netmiko ConnectHandler instance.
        name: Human-readable device name for logging.
    """
    if connection:
        connection.disconnect()
        print(f"[+] Disconnected from {name}.")