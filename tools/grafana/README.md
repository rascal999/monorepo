# Grafana Enterprise Docker Configuration

This directory contains the Docker configuration for Grafana Enterprise with MongoDB plugin support. The NixOS module in `maxos/modules/tools/grafana.nix` has been updated to use this Docker-based approach instead of the native NixOS Grafana service.

## Features

- Uses Grafana Enterprise Docker image
- Pre-installs the MongoDB datasource plugin
- Automatically provisions the MongoDB datasource
- Configurable through NixOS module options
- Persists data in the specified data directory

## Directory Structure

- `docker-compose.yml`: Docker Compose configuration for local development/testing
- `provisioning/`: Contains Grafana provisioning configurations
  - `datasources/`: Datasource configurations
    - `mongodb.yaml`: MongoDB datasource configuration

## NixOS Module Usage

To use the Grafana Docker container in your NixOS configuration:

```nix
# In your configuration.nix or the file that imports this module
{
  modules.tools.grafana = {
    enable = true;
    port = 3100;  # Port to expose Grafana on
    domain = "localhost";  # Domain name for Grafana
    dataDir = "/var/lib/grafana";  # Directory to store Grafana data
    
    # MongoDB configuration (optional)
    mongodb = {
      enable = true;  # Enable MongoDB datasource
      url = "mongodb://localhost:27017";  # MongoDB connection URL
      database = "metrics";  # MongoDB database name
      username = "mongoadmin";  # Optional: MongoDB username
      password = "mongopassword";  # Optional: MongoDB password
    };
  };
}
```

## How It Works

The NixOS module:

1. Enables Docker on the system
2. Creates necessary directories for Grafana data
3. Copies and configures provisioning files
4. Creates a systemd service to manage the Grafana Docker container
5. Configures the container with the appropriate environment variables
6. Mounts volumes for data persistence

## MongoDB Integration

When MongoDB integration is enabled:

1. The MongoDB datasource plugin is pre-installed
2. The MongoDB datasource is automatically provisioned
3. Connection details are configured based on the module options

## Manual Testing with Docker Compose

For local development or testing, you can use the provided Docker Compose file:

```bash
cd /path/to/monorepo/tools/grafana
docker-compose up -d
```

This will start Grafana on port 3100 with the MongoDB plugin pre-installed.

## Troubleshooting

- **Container not starting**: Check the systemd service logs with `journalctl -u grafana-docker`
- **Plugin not loading**: Verify the plugin is correctly specified in the environment variables
- **MongoDB connection issues**: Check the MongoDB connection URL and credentials
- **Provisioning errors**: Examine the Grafana logs with `docker logs grafana`

## Accessing Grafana

After applying your NixOS configuration with `nixos-rebuild switch`, Grafana will be available at:

- URL: http://localhost:3100
- Default credentials:
  - Username: `admin`
  - Password: `admin`

You should change the default password after the first login for security reasons.