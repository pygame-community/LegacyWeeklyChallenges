{
  description = "Web and pygame python env";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
  in
  with nixpkgs.legacyPackages.${system};
  let
    pythonEnv = python38.withPackages(ps: with ps; [
      pygame
    ]);
  in
  {
    devShell.${system} = mkShell {
      buildInputs = [
        pythonEnv
      ];
    };
  };
}
