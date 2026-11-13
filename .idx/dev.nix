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
    ALEPH_MCP_HTTP_URL = "http://127.0.0.1:8765/mcp";
  };
  idx = {
    workspace = {
      onCreate = {
        setup-antigravity = "python3 aleph_cli.py antigravity-always-on --no-daemon";
        verify-kernel = "python3 aleph_cli.py test";
      };
      onStart = {
        start-aleph-mcp-daemon = "python3 aleph_mcp_client.py start --host 127.0.0.1 --port 8765";
      };
    };
  };
}
