# DME (Docker Managed Environments)

A simple tool to quickly drop into a shell of any supported Linux distribution using Docker containers.

## Features

- Quick access to various Linux distribution shells
- Auto-cleanup after exit (--rm)
- Interactive terminal support (-it)
- Wide range of supported distributions

## Requirements

- Docker installed and running
- Bash shell

## Usage

```bash
./dme.sh DISTRO
```

For example:
```bash
./dme.sh ubuntu    # Latest Ubuntu
./dme.sh alpine    # Latest Alpine
./dme.sh arch      # Latest Arch Linux
```

## Supported Distributions

| Distribution | Description | Version(s) |
|-------------|-------------|------------|
| AlmaLinux | Enterprise Linux fork | Latest |
| Alpine Linux | Lightweight container-optimized | Latest, 3.18, 3.17 |
| Amazon Linux | AWS-optimized | 2 |
| Arch Linux | Rolling release | Latest |
| CentOS | Enterprise Linux | 7 |
| Clear Linux | Intel's performance-optimized | Latest |
| Debian | Universal OS | Latest, 11, 10 |
| Fedora | Leading edge | Latest |
| Gentoo | Source-based | Latest |
| Kali Linux | Security testing | Latest |
| NixOS | Declarative Linux | Latest |
| OpenMandriva | Community-driven | Latest |
| openSUSE | Enterprise-grade | Leap (Latest), Tumbleweed |
| Oracle Linux | Enterprise Linux | 9 |
| Rocky Linux | Enterprise Linux fork | Latest, 9, 8 |
| Slackware | Classic Linux | Latest |
| Ubuntu | User-friendly | Latest, 22.04, 20.04 |
| Void Linux | Independent | Latest |

## How It Works

The script:
1. Checks if Docker is installed
2. Maps the requested distribution to its Docker image
3. Runs the container with an interactive shell
4. Automatically removes the container on exit

## Examples

Drop into different shells:
```bash
./dme.sh debian     # Latest Debian
./dme.sh debian11   # Debian 11
./dme.sh debian10   # Debian 10

./dme.sh alpine     # Latest Alpine
./dme.sh alpine3.18 # Alpine 3.18
./dme.sh alpine3.17 # Alpine 3.17

./dme.sh kali       # Kali Linux for security testing
./dme.sh gentoo     # Gentoo Linux for source-based builds
./dme.sh nixos      # NixOS for declarative configuration
