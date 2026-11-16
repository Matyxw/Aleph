# .idx/dev.nix — Google Antigravity / Project IDX Always-On Environment for El Aleph v33.0.0
{ pkgs, ... }: {
  channel = "stable-24.05";
  packages = [
    pkgs.python311
  ];
  env = {
    PYTHONUNBUFFERED = "1";
    ALEPH_ALWAYS_ON = "1";
    ALEPH_KERNEL_VERSION = "33.0.0";
  };
  idx = {
    workspace = {
      onCreate = {
        setup-antigravity = "python3 aleph_cli.py antigravity-always-on";
        verify-kernel = "python3 aleph_cli.py test";
      };
    };
  };
}
