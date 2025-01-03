{ config, lib, pkgs, ... }:

{
  imports = [
    ../../modules/tools/i3/server.nix
    ../../modules/tools/tmux.nix
    ../../modules/tools/alacritty.nix
  ];

  # Enable home-manager
  programs.home-manager.enable = true;

  # Home Manager needs a bit of information about you and the paths it should manage
  home = {
    username = "user";
    homeDirectory = "/home/user";
    stateVersion = "23.11";

    packages = with pkgs; [
      # System administration
      htop
      btop
      iotop
      iftop
      nethogs
      nmap
      tcpdump
      mtr
      
      # Terminal utilities
      neovim
      ripgrep
      fd
      jq
      tree
      wget
      curl
      unzip
      tmux
      
      # Monitoring and logging
      prometheus
      grafana
      lnav
      
      # Development tools
      git
      gh
      
      # Security tools
      fail2ban
      ufw
      
      # System tools
      smartmontools
      lm_sensors
      ethtool
      pciutils
      usbutils
      
      # Backup tools
      restic
      rclone
    ];

    # Environment variables
    sessionVariables = {
      EDITOR = "nvim";
      TERMINAL = "alacritty";
    };
  };

  # Git configuration
  programs.git = {
    enable = true;
    userName = "Server Admin";
    userEmail = "admin@example.com";
    extraConfig = {
      init.defaultBranch = "main";
      pull.rebase = true;
      core.editor = "nvim";
    };
  };

  # Additional program configurations
  programs = {
    bash = {
      enable = true;
      shellAliases = {
        ll = "ls -la";
        ".." = "cd ..";
        "..." = "cd ../..";
        update = "sudo nixos-rebuild switch";
        gs = "git status";
        gc = "git commit";
        gp = "git push";
        
        # Server-specific aliases
        ports = "netstat -tulanp";
        mem = "free -h";
        disk = "df -h";
        ps = "ps auxf";
        myip = "curl http://ipecho.net/plain; echo";
        logs = "journalctl -f";
      };
      
      # Additional shell configuration
      initExtra = ''
        # Set a simple prompt for server
        export PS1="\[\033[1;32m\][\u@\h:\w]\\$\[\033[0m\] "
        
        # Add safety nets
        alias rm='rm -i'
        alias cp='cp -i'
        alias mv='mv -i'
        
        # Quick log viewing
        function logtail() {
          if [ -z "$1" ]; then
            echo "Usage: logtail <service-name>"
          else
            journalctl -u "$1" -f
          fi
        }
      '';
    };

    direnv = {
      enable = true;
      nix-direnv.enable = true;
    };

    fzf = {
      enable = true;
      enableBashIntegration = true;
    };
  };

  # Minimal services for server
  services = {
    gpg-agent = {
      enable = true;
      enableSshSupport = true;
    };
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;
}
