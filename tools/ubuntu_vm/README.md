# Ubuntu VM Setup

Automated setup for Ubuntu 24.04 desktop VM with i3 window manager.

## Features

- Ubuntu 24.04.1 Desktop base
- Unattended installation with automatic partitioning
- i3 window manager with configuration from maxos
- Preconfigured keyboard shortcuts matching maxos/i3
- VNC display for reliable graphics
- Virtio drivers for better performance

## Prerequisites

Required packages:
```bash
# Install required packages
sudo apt-get install \
  qemu-kvm \
  libvirt-daemon-system \
  virtinst \
  libvirt-clients \
  wget
```

Docker is required for genisoimage:
```bash
# Install Docker from https://docs.docker.com/engine/install/
```

Ensure your user is in the required groups:
```bash
sudo usermod -aG libvirt,kvm,docker $USER
```

## Usage

Basic usage (downloads Ubuntu ISO):
```bash
sudo ./setup.sh
```

Use existing ISO:
```bash
sudo ./setup.sh --iso path/to/ubuntu.iso
```

If a VM named 'ubuntu-desktop' already exists, you'll be prompted to remove it.

The script will:
1. Set up libvirt network
2. Use existing ISO or download Ubuntu 24.04.1 Desktop ISO (~4GB)
3. Create a cloud-init configuration ISO
4. Set up a VM with:
   - 8GB RAM
   - 4 vCPUs
   - 50GB virtio disk
   - VNC display (connect with virt-viewer)
   - NAT networking
   - Automatic installation and reboot

The installation is fully automated:
- Automatic partitioning
- No user prompts
- Auto-ejects installation media
- Reboots when complete

Default user credentials:
- Username: user
- Password: password

## Connecting to VM

Use virt-viewer to connect:
```bash
virt-viewer ubuntu-desktop
```

Or any VNC client:
```bash
# Get VM's VNC port
virsh vncdisplay ubuntu-desktop
```

## Files

- `setup.sh` - Main setup script
- `i3-config.template` - i3 window manager configuration
- `cloud-init/` - Cloud-init configuration files
  - `user-data` - System setup and package installation
  - `meta-data` - Instance metadata

## Troubleshooting

If the script fails:
```bash
# Reset network
sudo virsh net-destroy default
sudo virsh net-undefine default
sudo systemctl restart libvirtd
sudo ./setup.sh
```

For disk space:
- Ensure you have at least 60GB free space:
  * ~4GB for Ubuntu ISO
  * 50GB for VM disk
  * Additional space for temporary files