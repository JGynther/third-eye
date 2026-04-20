{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = {nixpkgs, ...}: let
    forAllSystems = f:
      nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed (
        system:
          f nixpkgs.legacyPackages.${system}
      );
  in {
    devShells =
      forAllSystems
      (pkgs: let
        libs = with pkgs; [
          stdenv.cc.cc.lib
          libGL
          glib
        ];
      in {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python313
            uv
            bun
            sqlite
          ];

          buildInputs = libs;

          shellHook = ''
            export LD_LIBRARY_PATH=/run/opengl-driver/lib:${pkgs.lib.makeLibraryPath libs}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
          '';
        };
      });
  };
}
