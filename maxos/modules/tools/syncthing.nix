{ config, lib, pkgs, ... }:

{
  # Backup script for syncthing share directory
  systemd.services.backup-share = {
    description = "Backup syncthing share directory";
    script = ''
      mkdir -p /home/user/backup
      cd /home/user
      tar -czf "backup/share-$(date +%Y%m%d-%H%M).tar.gz" share/
      # Keep only the 20 most recent backups
      ls -t /home/user/backup/share-*.tar.gz | tail -n +21 | xargs -r rm --
    '';
    serviceConfig = {
      Type = "oneshot";
      User = "user";
    };
  };

  # Timer to run backup daily at 16:30
  systemd.timers.backup-share = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnCalendar = "16:30:00";
      Persistent = true;
    };
  };

  services.syncthing = {
    enable = true;
    user = "user";
    dataDir = "/home/user";
    configDir = "/home/user/.config/syncthing";
    overrideDevices = true;     # Overwrite any devices added or deleted through the WebUI
    overrideFolders = true;     # Overwrite any folders added or deleted through the WebUI
    settings = {
      options.urAccepted = -1;  # Opt out of anonymous usage reporting
      devices = {
        "G16" = {
          id = "UVHYVJX-YL2SG2C-NY5PZOH-BRXFS6B-34V5WNF-PIO7MS4-BQY36IR-RQGIRQW";
        };
      };
      folders = {
        "share" = {
          path = "/home/user/share";
          devices = [ "G16" ];
        };
      };
      gui = {
        address = "127.0.0.1:8384";
      };
    };
  };
}