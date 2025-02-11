# Traefik API Gateway

Auto-discovering API gateway for Docker containers. Routes traffic based on domain patterns like `api.mgp.host` or `test.alm.host`. Works with dnsmasq to handle *.host domain resolution.

## Prerequisites

1. DNS Configuration:
   - The DNS module is included in maxos desktop configuration
   - Uses dnsmasq to resolve all *.host domains to 127.0.0.1
   - After maxos configuration changes:
     ```bash
     sudo nixos-rebuild switch --flake .#rig
     sudo systemctl restart dnsmasq
     ping test.host  # Should resolve to 127.0.0.1
     ```

## Setup

1. Start Traefik:
```bash
cd github/monorepo/docker/traefik
./setup.sh
```

This will:
- Create the traefik-public network
- Start Traefik with host networking
- Start an example service accessible at test.mgp.host

## Adding New Services

Add new services by connecting them to the `traefik-public` network and adding the required labels. Example:

```yaml
version: "3.9"
services:
  api:
    image: your-api-image
    networks:
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.mgp.host`)"
      - "traefik.http.services.api.loadbalancer.server.port=8000"

networks:
  traefik-public:
    external: true
```

## How it Works

1. dnsmasq resolves all *.host domains to 127.0.0.1
2. Traefik runs with host networking to handle these requests
3. When a container is launched with:
   - Connection to `traefik-public` network
   - Label `traefik.enable=true`
   - Host rule label (e.g., `traefik.http.routers.api.rule=Host(\`api.mgp.host\`)`)
   - Port label (e.g., `traefik.http.services.api.loadbalancer.server.port=8000`)
4. Traefik automatically:
   - Creates a route for the specified host
   - Routes traffic to the container
   - Updates routing when containers start/stop

## Accessing Services

Once DNS is configured, you can access your services directly:

- Traefik Dashboard: http://traefik.host
- Example Service: http://test.mgp.host
- Your Services: http://[service].[domain].host (e.g., http://api.mgp.host)

## Troubleshooting

If DNS resolution isn't working:
1. Check dnsmasq service: `systemctl status dnsmasq`
2. View dnsmasq logs: `journalctl -u dnsmasq`
3. Test DNS resolution: `dig @127.0.0.1 test.host`
4. Check DNS settings: `cat /etc/resolv.conf`