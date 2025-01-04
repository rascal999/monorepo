#!/usr/bin/env bash

# Function to display usage
usage() {
    echo "Usage: $0 DISTRO"
    echo
    echo "Drop into a shell of specified Linux distribution"
    echo
    echo "Available distributions:"
    echo "  ubuntu      - Latest Ubuntu"
    echo "  ubuntu22    - Ubuntu 22.04"
    echo "  ubuntu20    - Ubuntu 20.04"
    echo "  debian      - Latest Debian"
    echo "  debian11    - Debian 11"
    echo "  debian10    - Debian 10"
    echo "  centos7     - CentOS 7"
    echo "  rocky       - Latest Rocky Linux"
    echo "  rocky9      - Rocky Linux 9"
    echo "  rocky8      - Rocky Linux 8"
    echo "  fedora      - Latest Fedora"
    echo "  alpine      - Latest Alpine"
    echo "  alpine3.18  - Alpine 3.18"
    echo "  alpine3.17  - Alpine 3.17"
    echo "  arch        - Latest Arch Linux"
    echo "  nixos       - Latest NixOS"
    echo "  opensuse    - Latest openSUSE Leap"
    echo "  tumbleweed  - openSUSE Tumbleweed"
    echo "  kali        - Latest Kali Linux"
    echo "  amazonlinux - Amazon Linux 2"
    echo "  oracle      - Latest Oracle Linux"
    echo "  void        - Latest Void Linux"
    echo
    exit 1
}

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: docker is required but not installed"
    exit 1
fi

# Check if argument is provided
if [ $# -ne 1 ]; then
    usage
fi

# Map distro names to docker images
case "$1" in
    "ubuntu"|"ubuntu22")
        image="ubuntu:22.04"
        shell="/bin/bash"
        ;;
    "ubuntu20")
        image="ubuntu:20.04"
        shell="/bin/bash"
        ;;
    "debian"|"debian11")
        image="debian:11"
        shell="/bin/bash"
        ;;
    "debian10")
        image="debian:10"
        shell="/bin/bash"
        ;;
    "centos7")
        image="centos:7"
        shell="/bin/bash"
        ;;
    "rocky"|"rocky9")
        image="rockylinux:9"
        shell="/bin/bash"
        ;;
    "rocky8")
        image="rockylinux:8"
        shell="/bin/bash"
        ;;
    "fedora")
        image="fedora:latest"
        shell="/bin/bash"
        ;;
    "alpine"|"alpine3.18")
        image="alpine:3.18"
        shell="/bin/sh"
        ;;
    "alpine3.17")
        image="alpine:3.17"
        shell="/bin/sh"
        ;;
    "arch")
        image="archlinux:latest"
        shell="/bin/bash"
        ;;
    "nixos")
        image="nixos/nix:latest"
        shell="/bin/bash"
        ;;
    "opensuse")
        image="opensuse/leap:latest"
        shell="/bin/bash"
        ;;
    "tumbleweed")
        image="opensuse/tumbleweed:latest"
        shell="/bin/bash"
        ;;
    "kali")
        image="kalilinux/kali-rolling:latest"
        shell="/bin/bash"
        ;;
    "amazonlinux")
        image="amazonlinux:2"
        shell="/bin/bash"
        ;;
    "oracle")
        image="oraclelinux:9"
        shell="/bin/bash"
        ;;
    "void")
        image="ghcr.io/void-linux/void-linux:latest"
        shell="/bin/bash"
        ;;
    *)
        echo "Error: Unknown distribution '$1'"
        usage
        ;;
esac

# Run the container
echo "Starting $1 container..."
docker run --rm -it "$image" "$shell"
