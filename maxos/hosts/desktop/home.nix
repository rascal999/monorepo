{ config, lib, pkgs, ... }:

{
  imports = [
    ../../modules/tools/i3/desktop.nix
    ../../modules/tools/tmux.nix
    ../../modules/tools/alacritty.nix
    ../../modules/tools/zsh.nix
    ../../modules/tools/rofi/default.nix
  ];

  # Enable home-manager
  programs.home-manager.enable = true;

  # Home Manager needs a bit of information about you and the paths it should manage
  home = {
    username = "user";
    homeDirectory = lib.mkForce "/home/user";
    stateVersion = "23.11";  # Please read the comment below

    # The home.stateVersion option does not have a default and must be set
    # First time users of home-manager should read:
    # https://nix-community.github.io/home-manager/index.html#sec-install-standalone

    packages = with pkgs; [
      # Fonts
      (nerdfonts.override { fonts = [ "JetBrainsMono" "Meslo" ]; })
      
      # Development tools
      git
      gh
      vscode
      neovim
      ripgrep
      fd
      jq
      tree

      # System tools
      htop
      btop
      neofetch
      unzip
      wget
      curl

      libreoffice
      vlc
      gimp
      
      # Communication
      slack
      discord
      
      # File management
      pcmanfm
      ranger
      feh
      
      # System monitoring and management
      pavucontrol
      networkmanagerapplet
      arandr
    ];

    # Environment variables
    sessionVariables = {
      EDITOR = "nvim";
      TERMINAL = "alacritty";
      BROWSER = "firefox";
    };

    # File associations
    file = {
      ".config/mimeapps.list".text = ''
        [Default Applications]
        text/html=firefox.desktop
        x-scheme-handler/http=firefox.desktop
        x-scheme-handler/https=firefox.desktop
        application/pdf=org.pwmt.zathura.desktop
      '';
    };
  };

  # Git configuration
  programs.git = {
    enable = true;
    userName = "Your Name";
    userEmail = "your.email@example.com";
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
      };
    };

    direnv = {
      enable = true;
      nix-direnv.enable = true;
    };

    fzf = {
      enable = true;
      enableBashIntegration = true;
    };

    firefox = {
      enable = true;
      profiles.default = {
        userChrome = builtins.readFile ../../modules/tools/firefox/css/userChrome.css;
        userContent = builtins.readFile ../../modules/tools/firefox/css/userContent.css;
      };
    };
  };

  # Enable services
  services = {
    picom = {
      enable = true;
      vSync = true;
    };

    dunst = {
      enable = true;
      settings = {
        global = {
          font = "JetBrainsMono Nerd Font 10";
          frame_width = 2;
          frame_color = "#4c566a";
        };
      };
    };
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;
}
