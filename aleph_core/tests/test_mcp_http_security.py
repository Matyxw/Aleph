"""El daemon MCP HTTP debe exigir token, validar Host/Origin y no abrir CORS ni OAuth falso."""
import http.client
import json
import threading
import unittest

from aleph_core.engine import AlephUniversalMCPServer

TOKEN = "t" * 40


class TestMCPHTTPSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = AlephUniversalMCPServer().serve_http(port=0, token=TOKEN, _return_server=True)
        cls.port = probe.server_address[1]
        probe.server_close()
        cls.httpd = AlephUniversalMCPServer().serve_http(port=cls.port, token=TOKEN, _return_server=True)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _req(self, method, path, body=None, headers=None, host=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        h = {"Host": host or f"127.0.0.1:{self.port}"}
        h.update(headers or {})
        payload = json.dumps(body) if body is not None else None
        if payload is not None:
            h.setdefault("Content-Type", "application/json")
        conn.request(method, path, body=payload, headers=h)
        r = conn.getresponse()
        data = r.read()
        hdrs = {k.lower(): v for k, v in r.getheaders()}
        conn.close()
        return r.status, hdrs, data

    RPC = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    AUTH = {"Authorization": f"Bearer {TOKEN}"}

    def test_sin_token_es_401(self):
        st, _, _ = self._req("POST", "/mcp", self.RPC)
        self.assertEqual(st, 401)

    def test_token_incorrecto_es_401(self):
        st, _, _ = self._req("POST", "/mcp", self.RPC, {"Authorization": "Bearer nope"})
        self.assertEqual(st, 401)

    def test_con_token_funciona(self):
        st, _, data = self._req("POST", "/mcp", self.RPC, self.AUTH)
        self.assertEqual(st, 200)
        self.assertIn("result", json.loads(data))

    def test_host_ajeno_es_403_anti_dns_rebinding(self):
        st, _, _ = self._req("POST", "/mcp", self.RPC, self.AUTH, host="evil.example.com")
        self.assertEqual(st, 403)

    def test_origin_ajeno_es_403_y_sin_cors_abierto(self):
        st, hdrs, _ = self._req("POST", "/mcp", self.RPC, {**self.AUTH, "Origin": "https://evil.example.com"})
        self.assertEqual(st, 403)
        self.assertNotEqual(hdrs.get("access-control-allow-origin"), "*")

    def test_nunca_hay_cors_wildcard(self):
        _, hdrs, _ = self._req("GET", "/health")
        self.assertNotIn("access-control-allow-origin", hdrs)

    def test_post_a_otra_ruta_es_404(self):
        st, _, _ = self._req("POST", "/cualquier-cosa", self.RPC, self.AUTH)
        self.assertEqual(st, 404)

    def test_oauth_falso_deshabilitado(self):
        for path in ("/oauth/token", "/oauth/register"):
            st, _, _ = self._req("POST", path, {})
            self.assertEqual(st, 501)
        st, _, _ = self._req("GET", "/oauth/authorize?redirect_uri=https://evil.example.com")
        self.assertEqual(st, 501)

    def test_cuerpo_demasiado_grande_es_413(self):
        st, _, _ = self._req("POST", "/mcp", None, {**self.AUTH, "Content-Length": str(5 * 1024 * 1024)})
        self.assertEqual(st, 413)

    def test_health_no_filtra_conteo_de_tools(self):
        st, _, data = self._req("GET", "/health")
        self.assertEqual(st, 200)
        self.assertNotIn("tools_count", json.loads(data))


if __name__ == "__main__":
    unittest.main()
