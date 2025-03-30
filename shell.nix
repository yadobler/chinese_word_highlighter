{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
    nodejs_23
    npm-check-updates
    vue-language-server
  ];

  NODE_OPTIONS = "--no-deprecation";
}
