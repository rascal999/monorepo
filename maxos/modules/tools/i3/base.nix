{ config, lib, pkgs, ... }:

{
  programs.home-manager.enable = true;
  
  home.packages = with pkgs; [
    i3status
    i3lock
    dmenu
  ];

  xsession.windowManager.i3 = {
    enable = true;
    config = {
      modifier = "Mod1";  # Use Alt key as modifier

      # Basic keybindings
      keybindings = {
        # Terminal
        "Mod1+t" = "exec ${pkgs.alacritty}/bin/alacritty -e ${pkgs.tmux}/bin/tmux";
        
        # Program launcher
        "Mod1+d" = "exec ${pkgs.dmenu}/bin/dmenu_run";
        
        # Window management
        "Mod1+u" = "fullscreen toggle";
        "Mod1+f" = "fullscreen toggle";
        "Mod1+Shift+space" = "floating toggle";
        
        # Layout management
        "Mod1+s" = "layout stacking";
        "Mod1+w" = "layout tabbed";
        "Mod1+e" = "layout toggle split";
        "Mod1+h" = "split h";
        "Mod1+v" = "split v";
        
        # Focus
        "Mod1+Left" = "focus left";
        "Mod1+Down" = "focus down";
        "Mod1+Up" = "focus up";
        "Mod1+Right" = "focus right";
        
        # Moving windows
        "Mod1+Shift+Left" = "move left";
        "Mod1+Shift+Down" = "move down";
        "Mod1+Shift+Up" = "move up";
        "Mod1+Shift+Right" = "move right";
        
        # Restart/reload i3
        "Mod1+Shift+c" = "kill";
        "Mod1+Shift+r" = "restart";

        # Screenshot bindings
        "Print" = "exec ${pkgs.flameshot}/bin/flameshot gui";
        "Shift+Print" = "exec ${pkgs.flameshot}/bin/flameshot full";

        # Media controls
        "XF86AudioRaiseVolume" = "exec --no-startup-id pactl set-sink-volume @DEFAULT_SINK@ +5%";
        "XF86AudioLowerVolume" = "exec --no-startup-id pactl set-sink-volume @DEFAULT_SINK@ -5%";
        "XF86AudioMute" = "exec --no-startup-id pactl set-sink-mute @DEFAULT_SINK@ toggle";
        
        # Brightness controls
        "XF86MonBrightnessUp" = "exec ${pkgs.light}/bin/light -A 5";
        "XF86MonBrightnessDown" = "exec ${pkgs.light}/bin/light -U 5";
        
        # Quick launch frequently used applications
        "${config.xsession.windowManager.i3.config.modifier}+b" = "exec ${pkgs.firefox}/bin/firefox";
        "${config.xsession.windowManager.i3.config.modifier}+n" = "exec ${pkgs.pcmanfm}/bin/pcmanfm";
        "${config.xsession.windowManager.i3.config.modifier}+l" = "exec ${pkgs.i3lock}/bin/i3lock -c 000000";
        "${config.xsession.windowManager.i3.config.modifier}+Return" = "exec $HOME/.local/bin/rofi-launcher";
      };

      # Workspace configuration
      workspaceOutputAssign = [
        { workspace = "1: term"; output = "primary"; }
        { workspace = "2: web"; output = "primary"; }
        { workspace = "3: code"; output = "primary"; }
        { workspace = "4: files"; output = "primary"; }
        { workspace = "5: media"; output = "primary"; }
      ];

      # Basic appearance settings
      bars = [{
        position = "bottom";
        statusCommand = "${pkgs.i3status}/bin/i3status";
        colors = {
          background = "#2e3440";
          statusline = "#eceff4";
          separator = "#4c566a";
        };
      }];

      # Window appearance
      gaps = {
        inner = 0;
        outer = 0;
        smartGaps = true;
      };
    };
  };
}
