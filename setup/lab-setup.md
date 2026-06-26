# Lab Setup: GNS3 + MikroTik CHR Virtual Network

This document describes the full setup of the virtual network lab used for the Netmiko Network Automation Tool project. It covers GNS3 installation, GNS3 VM configuration, MikroTik CHR appliance import, topology build, TAP interface bridging, and Python environment setup. All deviations from the standard setup path are documented.

---

## Environment

| Component | Details |
|---|---|
| Host OS | Ubuntu 24.04 LTS |
| Machine | ASUS ROG Zephyrus G15 (AMD Ryzen 6900HS, 16GB RAM, Nvidia RTX 3060) |
| Username | makk007 |
| Hostname | Mawuse-ROG-Zephyrus-G15 |
| Virtualisation | VirtualBox (GNS3 VM) |
| GNS3 Version | 2.2.59 |
| GNS3 VM Version | 2.2.59 (VM version 0.19.0) |
| Router Appliance | MikroTik Cloud Hosted Router (CHR) 7.22.1 |
| Python | 3.x (system) |
| Netmiko | 4.7.0 |

---

## Lab Topology

```
[Ubuntu Host]
  10.10.10.1 (tap0)
       |
  [Cloud1 - tap0]
       |
      R1 (MikroTik CHR)
        ether1: 10.10.10.10/24  <-- faces Ubuntu host via tap0
        ether2: 10.0.0.1/30     <-- faces R2
       |
      R2 (MikroTik CHR)
        ether1: 10.0.0.2/30     <-- faces R1
```

| Device | Interface | IP Address | Purpose |
|---|---|---|---|
| Ubuntu Host | tap0 | 10.10.10.1/24 | GNS3 lab bridge |
| R1 | ether1 | 10.10.10.10/24 | Facing Ubuntu host |
| R1 | ether2 | 10.0.0.1/30 | Facing R2 |
| R2 | ether1 | 10.0.0.2/30 | Facing R1 |

---

## Step 1: Install GNS3

Added the official GNS3 PPA and installed GNS3 GUI and server:

```bash
sudo add-apt-repository ppa:gns3/ppa
sudo apt update
sudo apt install gns3-gui gns3-server
```

During installation, selected **Yes** when prompted to allow non-root users to capture packets and use `ubridge`. This adds the user to the `wireshark` and `ubridge` groups.

Logged out and back in for group membership to take effect.

---

## Step 2: Import the GNS3 VM into VirtualBox

Downloaded the GNS3 VM OVA for VirtualBox version 2.2.59 from:

```
https://github.com/GNS3/gns3-gui/releases/tag/v2.2.59
```

Imported into VirtualBox:

```
File > Import Appliance > select GNS3.VM.VirtualBox.2.2.59.ova
```

VM resource allocation after import:

| Resource | Allocated |
|---|---|
| RAM | 6144 MB |
| CPUs | 4 |

### Deviation 1: KVM/AMD-V conflict

The AMD Ryzen 6900HS requires `kvm_amd` to be unloaded before VirtualBox can claim AMD-V exclusively. This must be run before every VirtualBox session after reboot:

```bash
sudo modprobe -r kvm_amd
```

This is included in the lab startup script (see Step 6).

---

## Step 3: Configure GNS3 to Connect to the GNS3 VM

### Deviation 2: Local server binding mismatch

On first launch, GNS3 threw the following error:

```
The GNS3 VM (IP=192.168.56.101, NETWORK=192.168.56.0/24) is not on the same
network as the local server (IP=127.0.0.1, NETWORK=127.0.0.0/8)
```

**Fix:** Changed the local server host binding in GNS3 preferences:

**Edit > Preferences > Server > Local Server > Host binding**

Changed from `localhost` to `192.168.56.1` (the VirtualBox host-only adapter address). Applied and restarted GNS3.

After this change, both the local server and GNS3 VM showed green in the Servers Summary panel.

---

## Step 4: Import the MikroTik CHR Appliance

### Why MikroTik CHR

Cisco IOS images require a Cisco licence and cannot be legally redistributed. MikroTik Cloud Hosted Router (CHR) is freely available from mikrotik.com, supports SSH, and is natively supported by Netmiko (`device_type: mikrotik_routeros`). It was selected as the router appliance for this lab.

### Import process

Downloaded the official GNS3 appliance template:

```
https://github.com/GNS3/gns3-registry/blob/master/appliances/mikrotik-chr.gns3a
```

Downloaded the CHR 7.22.1 raw disk image from MikroTik's official server:

```
https://download.mikrotik.com/routeros/7.22.1/chr-7.22.1.img.zip
```

Extracted the zip to obtain `chr-7.22.1.img` and placed it in the GNS3 images directory:

```bash
mkdir -p ~/GNS3/images/QEMU
mv ~/Downloads/chr-7.22.1.img ~/GNS3/images/QEMU/
```

Imported the appliance in GNS3:

**File > Import appliance > select mikrotik-chr.gns3a**

Selected QEMU binary: `/usr/bin/qemu-system-x86_64 (v10.2.1)`

Selected version **7.22.1** and pointed to `chr-7.22.1.img`. Template `MikroTik CHR 7.22.1` was successfully created.

---

## Step 5: Build the Topology and Configure Routers

### Create the project

**File > New blank project**, named `netmiko-lab`.

Dragged two MikroTik CHR 7.22.1 nodes onto the canvas, named them R1 and R2. Added a Cloud node (Cloud1).

### Deviation 3: Cloud node server context

GNS3 QEMU appliances run on the GNS3 VM, while the Cloud node must run on the local server to access the Ubuntu host's network interfaces. When Cloud1 was initially placed, it ran on the GNS3 VM and only showed `eth0` and `eth1` (the GNS3 VM's internal interfaces).

**Fix:** Right-clicked Cloud1 > **Change server > Local**. After switching to local server, ticked **Show special Ethernet interfaces** in the Cloud1 configuration to reveal `vboxnet0`.

### Deviation 4: TAP interface required for bridging

Direct use of `vboxnet0` in Cloud1 did not pass traffic between the Ubuntu host and the CHR routers running on the GNS3 VM. A TAP interface was required to bridge traffic between the two execution contexts.

### Deviation 5: TAP subnet conflicted with WiFi

The initial TAP subnet `192.168.100.0/24` conflicted with the Ubuntu host's WiFi interface (`wlp4s0`), which was also assigned `192.168.100.x` via DHCP. This caused the default gateway to be overridden, dropping internet connectivity when the TAP interface came up.

**Fix:** Changed the lab subnet to `10.10.10.0/24`, which does not conflict with any existing interface.

### R1 configuration

```
/ip address add address=10.10.10.10/24 interface=ether1
/ip address add address=10.0.0.1/30 interface=ether2
/ip route add dst-address=0.0.0.0/0 gateway=10.10.10.1
/ip service enable ssh
/system identity set name=R1
/user set admin password=admin123
```

### R2 configuration

```
/ip address add address=10.0.0.2/30 interface=ether1
/ip route add dst-address=0.0.0.0/0 gateway=10.0.0.1
/ip service enable ssh
/system identity set name=R2
/user set admin password=admin123
```

### Ubuntu host routes

```bash
sudo ip route add 10.0.0.0/30 via 10.10.10.10
```

---

## Step 6: Lab Startup Script

Because the TAP interface does not persist across reboots, a startup script was created at `~/setup-gns3-lab.sh` to recreate it each session:

```bash
#!/bin/bash
# GNS3 Lab Startup Script

# Remove kvm_amd to avoid VirtualBox conflict
sudo modprobe -r kvm_amd

# Create TAP interface if it doesn't exist
if ! ip link show tap0 &>/dev/null; then
    sudo ip tuntap add tap0 mode tap user makk007
fi

# Remove old address if present
sudo ip addr flush dev tap0 2>/dev/null

# Assign IP and bring up with scoped route
sudo ip addr add 10.10.10.1/24 dev tap0
sudo ip link set tap0 up
sudo ip route add 10.10.10.0/24 dev tap0 2>/dev/null

echo "tap0 is up at 10.10.10.1"
echo "GNS3 lab ready."
```

```bash
chmod +x ~/setup-gns3-lab.sh
```

### Session startup sequence

Every GNS3 lab session must follow this order:

1. Run `sudo modprobe -r kvm_amd`
2. Open VirtualBox and start the GNS3 VM; wait for the green console screen showing `IP: 192.168.56.101`
3. Launch GNS3 and wait for both servers to show green in the Servers Summary panel
4. Open the `netmiko-lab` project and start all nodes
5. Run `~/setup-gns3-lab.sh`
6. Add route to R2: `sudo ip route add 10.0.0.0/30 via 10.10.10.10`
7. Verify: `ping -c 3 10.10.10.10 && ping -c 3 10.0.0.2`

---

## Step 7: Python Virtual Environment Setup

```bash
cd ~/netmiko-network-automation-tool
python3 -m venv .venv
source .venv/bin/activate
pip install netmiko
pip freeze > requirements.txt
```

Verified installation:

```bash
python3 -c "import netmiko; print(netmiko.__version__)"
# Output: 4.7.0
```

### End-to-end connectivity test

```python
from netmiko import ConnectHandler

r1 = {
    "device_type": "mikrotik_routeros",
    "host": "10.10.10.10",
    "username": "admin",
    "password": "admin123",
}

connection = ConnectHandler(**r1)
output = connection.send_command("/system identity print")
print(output)  # name: R1
connection.disconnect()
```

Netmiko successfully connected to R1, executed a command, and returned the expected output.

---

## Connectivity Summary

| Source | Destination | Method | Result |
|---|---|---|---|
| Ubuntu Host | R1 (10.10.10.10) | ping | Success |
| Ubuntu Host | R1 (10.10.10.10) | SSH | Success |
| Ubuntu Host | R2 (10.0.0.2) | ping | Success |
| Ubuntu Host | R2 (10.0.0.2) | SSH | Success |
| R1 | R2 (10.0.0.2) | ping | Success |
| Netmiko | R1 (10.10.10.10) | SSH | Success |