with import <nixpkgs> {};

with python36.pkgs; let
  pdfkit = buildPythonPackage {
    name = "pdfkit-0.6.1";
    buildInputs = [
    ];
    doCheck = false;
    src = fetchurl {
      url = "https://pypi.python.org/packages/a1/98/6988328f72fe3be4cbfcb6cbfc3066a00bf111ca7821a83dd0ce56e2cf57/pdfkit-0.6.1.tar.gz";
      sha256 = "1lcc1njpjd2zadbljqsnkrvamschl6j099p4giz1jd6mg1ds67gg";
    };
  };


in python36.withPackages (ps: with ps; [ beautifulsoup4 lxml requests pdfkit ])
