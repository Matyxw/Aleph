import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ab_eval.ab_harness import mcnemar_exact_p, run, summarize  # noqa: E402


class TestMcNemar(unittest.TestCase):
    def test_valores_conocidos(self):
        self.assertAlmostEqual(mcnemar_exact_p(3, 0), 0.25)       # 2 * (1/8)
        self.assertAlmostEqual(mcnemar_exact_p(0, 0), 1.0)
        self.assertAlmostEqual(mcnemar_exact_p(5, 5), 1.0)
        self.assertAlmostEqual(mcnemar_exact_p(10, 0), 2 / 1024)  # 0.001953125
        self.assertAlmostEqual(mcnemar_exact_p(0, 10), mcnemar_exact_p(10, 0))


class TestHarnessEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.repo = base / "repo"
        self.repo.mkdir()
        (self.repo / "check.py").write_text(
            "import sys, pathlib\nsys.exit(0 if pathlib.Path('solved.txt').exists() else 1)\n")
        # Agente falso: SOLO resuelve la tarea cuando ALEPH_ARM=with, y reporta tokens.
        self.agent = base / "agent.py"
        self.agent.write_text(textwrap.dedent("""
            import os, json, pathlib
            if os.environ["ALEPH_ARM"] == "with":
                pathlib.Path("solved.txt").write_text("ok")
            print(json.dumps({"tokens": 123}))
        """))
        self.tasks = base / "tasks.jsonl"
        self.tasks.write_text("\n".join(json.dumps(
            {"id": f"t{i}", "prompt": "p", "workdir": str(self.repo), "verify": f"{sys.executable} check.py"})
            for i in range(2)))

    def tearDown(self):
        self.tmp.cleanup()

    def test_el_brazo_with_gana_y_se_reporta_no_concluyente_con_pocos_pares(self):
        out_csv = Path(self.tmp.name) / "out.csv"
        s = run(self.tasks, f"{sys.executable} {self.agent}", reps=3, timeout=60, seed=1, out_csv=out_csv)
        self.assertEqual(s["pairs"], 6)
        self.assertEqual((s["with_only"], s["without_only"], s["both"], s["neither"]), (6, 0, 0, 0))
        self.assertEqual(s["with"]["success_rate"], 1.0)
        self.assertEqual(s["without"]["success_rate"], 0.0)
        self.assertAlmostEqual(s["mcnemar_p"], 2 / 64)
        self.assertEqual(s["with"]["median_tokens"], 123)
        self.assertIn("NO CONCLUYENTE", s["verdict"])  # 6 pares < 20: no se puede afirmar
        self.assertEqual(len(out_csv.read_text().strip().splitlines()), 1 + 12)

    def test_no_contamina_el_directorio_original(self):
        run(self.tasks, f"{sys.executable} {self.agent}", reps=1, timeout=60, seed=0, out_csv=None)
        self.assertFalse((self.repo / "solved.txt").exists())

    def test_veredicto_significativo_con_suficientes_pares(self):
        rows = []
        for i in range(25):
            rows.append({"task": f"t{i}", "rep": 0, "arm": "with", "success": 1, "seconds": 1.0, "tokens": None})
            rows.append({"task": f"t{i}", "rep": 0, "arm": "without", "success": 0, "seconds": 1.0, "tokens": None})
        s = summarize(rows)
        self.assertIn("significativa", s["verdict"])
        self.assertIn("CON reglas", s["verdict"])


if __name__ == "__main__":
    unittest.main()
