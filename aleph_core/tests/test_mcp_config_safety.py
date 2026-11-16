"""Custodia de la configuración MCP: nada de auto-aprobar todo, y toda referencia a tools debe existir."""
import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import aleph_cli  # noqa: E402
from aleph_core.engine import AlephUniversalMCPServer  # noqa: E402

TOOL_NAMES = {t["name"] for t in AlephUniversalMCPServer().get_tools_manifest()}


def _servers(path: Path) -> dict:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["mcpServers"]


class TestMCPConfigSafety(unittest.TestCase):
    CONFIGS = [ROOT / ".mcp.json", ROOT / ".antigravity" / "mcp_config.json", ROOT / ".gemini" / "settings.json"]

    def test_ningun_servidor_es_trust_ni_auto_aprueba_todo(self):
        for cfg in self.CONFIGS:
            for name, entry in _servers(cfg).items():
                self.assertFalse(entry.get("trust"), f"{cfg.name}:{name} trust debe ser false")
                self.assertNotIn("autoApprove", entry, f"{cfg.name}:{name} no debe tener autoApprove")
                self.assertNotIn("*", entry.get("alwaysAllow", []), f"{cfg.name}:{name} alwaysAllow '*'")
                self.assertFalse(entry.get("autoStart"), f"{cfg.name}:{name} no debe autoarrancar")

    def test_allow_list_coincide_con_la_constante_y_existe_en_el_manifiesto(self):
        safe = set(aleph_cli.SAFE_AUTO_APPROVE_TOOLS)
        self.assertTrue(safe <= TOOL_NAMES, f"tools inexistentes en la allow-list: {safe - TOOL_NAMES}")
        for cfg in self.CONFIGS[:2]:
            for entry in _servers(cfg).values():
                self.assertEqual(set(entry.get("alwaysAllow", [])), safe)

    def test_tools_mutantes_no_estan_auto_aprobados(self):
        for mut in ("aleph_apply_semantic_patch", "aleph_bitacora_learn_experiential_rule",
                    "aleph_omega_dgm_alphaevolve_self_improve"):
            self.assertNotIn(mut, aleph_cli.SAFE_AUTO_APPROVE_TOOLS)

    def test_settings_antigravity(self):
        st = json.loads((ROOT / ".antigravity" / "settings.json").read_text(encoding="utf-8"))
        self.assertFalse(st["antigravity.agent.autoApproveTools"])
        for f in st["antigravity.agent.rulesFiles"]:
            self.assertTrue((ROOT / f).exists(), f"rulesFiles apunta a un archivo inexistente: {f}")
        for k in ("preWriteGate", "uiGate", "dbGate"):
            self.assertIn(st[f"antigravity.verification.{k}"], TOOL_NAMES)
        self.assertIn(st["antigravity.agent.preTurnMcpTool"], TOOL_NAMES)

    def test_toda_referencia_a_tools_en_reglas_existe(self):
        for rel in (".antigravity/rules.md", "GEMINI.md", ".antigravity/settings.json"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            for ref in set(re.findall(r"`(aleph_[a-z0-9_]+)`", text)) | set(re.findall(r'"(aleph_[a-z0-9_]+)"', text)):
                if ref in ("aleph_cli", "aleph_core"):
                    continue
                self.assertIn(ref, TOOL_NAMES, f"{rel} referencia un tool inexistente: {ref}")

    def test_instalador_no_toca_el_home_por_defecto(self):
        with tempfile.TemporaryDirectory() as home, mock.patch.dict(os.environ, {"HOME": home, "USERPROFILE": home}):
            with contextlib.redirect_stdout(io.StringIO()):
                aleph_cli.cmd_antigravity_always_on()
            self.assertEqual(list(Path(home).rglob("*.json")), [], "no debe escribir en el home sin --install-user-home")

    def test_instalador_con_opt_in_escribe_config_segura(self):
        with tempfile.TemporaryDirectory() as home, mock.patch.dict(os.environ, {"HOME": home, "USERPROFILE": home}):
            with contextlib.redirect_stdout(io.StringIO()):
                aleph_cli.cmd_antigravity_always_on(install_user_home=True)
            written = list(Path(home).rglob("*.json"))
            self.assertTrue(written)
            for f in written:
                entry = json.loads(f.read_text(encoding="utf-8"))["mcpServers"]["el-aleph-sovereign"]
                self.assertFalse(entry["trust"])
                self.assertNotIn("*", entry["alwaysAllow"])
                self.assertNotIn("autoApprove", entry)


if __name__ == "__main__":
    unittest.main()
