{
  description = "NixOS configuration with desktop and server variants";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
    home-manager = {
      url = "github:nix-community/home-manager/release-23.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, ... }@inputs: {
    nixosConfigurations = {
      desktop-test-vm = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          {
            nixpkgs.config.allowUnfree = true;
          }
          ./hosts/desktop-test-vm/default.nix
          home-manager.nixosModules.home-manager
          {
            home-manager = {
              useGlobalPkgs = true;
              useUserPackages = true;
              users.user = { pkgs, ... }: {
                imports = [
                  ./hosts/desktop/home.nix
                ];
                home.stateVersion = "23.11";
              };
            };
          }
        ];
      };
    };
  };
}