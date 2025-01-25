#!/usr/bin/env bash

# Exit on error
set -e

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo for network setup"
    exit 1
fi

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORK_DIR="/tmp/ubuntu-vm-setup"
DEFAULT_ISO_URL="https://releases.ubuntu.com/24.04.1/ubuntu-24.04.1-desktop-amd64.iso"
VM_NAME="ubuntu-desktop"
VM_RAM="8192"
VM_VCPUS="4"
VM_DISK_SIZE="50"

# Parse command line arguments
ISO_PATH=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --iso)
            ISO_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--iso path/to/ubuntu.iso]"
            exit 1
            ;;
    esac
done

# Check required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is required but not installed."
        case "$1" in
            docker)
                echo "Install Docker from https://docs.docker.com/engine/install/"
                ;;
            virt-install)
                echo "Install with: sudo apt-get install virtinst"
                ;;
            wget)
                echo "Install with: sudo apt-get install wget"
                ;;
            virsh)
                echo "Install with: sudo apt-get install libvirt-clients"
                ;;
        esac
        exit 1
    fi
}

check_command docker
check_command virt-install
check_command wget
check_command virsh

# Check for existing VM
if virsh dominfo "$VM_NAME" >/dev/null 2>&1; then
    read -p "VM '$VM_NAME' already exists. Remove it? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing VM..."
        virsh destroy "$VM_NAME" >/dev/null 2>&1 || true
        virsh undefine "$VM_NAME" >/dev/null 2>&1 || true
    else
        echo "Exiting..."
        exit 1
    fi
fi

# Setup network
echo "Setting up network..."
systemctl start libvirtd
virsh net-undefine default >/dev/null 2>&1 || true
virsh net-destroy default >/dev/null 2>&1 || true

cat > /tmp/default-network.xml << EOF
<network>
  <name>default</name>
  <forward mode='nat'/>
  <bridge name='virbr0' stp='on' delay='0'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254'/>
    </dhcp>
  </ip>
</network>
EOF

virsh net-define /tmp/default-network.xml
virsh net-start default
virsh net-autostart default
rm /tmp/default-network.xml

# Pull genisoimage Docker image
echo "Pulling genisoimage Docker image..."
docker pull building5/genisoimage:latest

# Create work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Handle ISO
if [ -z "$ISO_PATH" ]; then
    ISO_PATH="$WORK_DIR/ubuntu-desktop.iso"
    if [ ! -f "$ISO_PATH" ]; then
        echo "Downloading Ubuntu desktop ISO..."
        wget "$DEFAULT_ISO_URL" -O "$ISO_PATH"
    fi
else
    if [ ! -f "$ISO_PATH" ]; then
        echo "Error: ISO file not found at $ISO_PATH"
        exit 1
    fi
    echo "Using existing ISO: $ISO_PATH"
fi

# Create ISO with cloud-init files using Docker
mkdir -p "$WORK_DIR/cidata"
cp "$SCRIPT_DIR/cloud-init/user-data" "$WORK_DIR/cidata/"
cp "$SCRIPT_DIR/cloud-init/meta-data" "$WORK_DIR/cidata/"

echo "Creating cloud-init ISO..."
CIDATA_PATH="$WORK_DIR/cidata.iso"
docker run --rm \
    -v "$WORK_DIR/cidata:/data" \
    -v "$WORK_DIR:/output" \
    building5/genisoimage \
    -output /output/cidata.iso -volid cidata -joliet -rock /data/user-data /data/meta-data

# Create VM using virt-install
virt-install \
  --name="$VM_NAME" \
  --memory="$VM_RAM" \
  --vcpus="$VM_VCPUS" \
  --disk path="$ISO_PATH",device=cdrom,bus=sata \
  --disk path="$CIDATA_PATH",device=cdrom,bus=sata \
  --disk size="$VM_DISK_SIZE",bus=virtio \
  --os-variant=ubuntu24.04 \
  --network network=default \
  --graphics vnc,listen=0.0.0.0 \
  --video virtio \
  --boot cdrom,hd

# Cleanup
rm -rf "$WORK_DIR"