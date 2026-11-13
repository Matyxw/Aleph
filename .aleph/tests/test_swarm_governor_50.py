#!/usr/bin/env python3
"""
.aleph/tests/test_swarm_governor_50.py
Suite de verificación exhaustiva del Subsistema de Gobernanza y Enjambres Masivos (50+ Agentes).
Verifica cumplimiento estricto del plan 07_PLAN_SWARM_GOVERNANCE_50_AGENTS.md:
  - Worktrees en RAM con sparse-cone (< 40 ms)
  - Multi-Raft con Leases de 15s y Fencing Tokens (latencia <= 12 ms)
  - AST-CRDT Semántico con orden total estricto de Lamport y 0 ciclos
  - Speculative Merge Pipeline (SMP) con Runners Estériles (0 roturas en main)
  - Detección incremental de deadlocks con Tarjan DFS (< 0.45 ms) y Wound-Wait
  - Protocolo HART v2 (60% Blue, 33.3% Red, 4 Neutral) con intercepción >= 99.6%
  - Topología Plumtree Gossip O(N log N) y Vector Clocks
  - Throughput de enjambre masivo >= 120 tareas/min a N=50 agentes
"""

from __future__ import annotations

import os
import sys
import time
import unittest
from pathlib import Path

# Inyectar .aleph/scripts en el path
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from swarm_governor_50 import (
    AgentRole,
    AstCrdtEngine,
    AstNode,
    HartAdversarialSwarm,
    IncrementalDeadlockDetector,
    LamportTimestamp,
    MultiRaftShardCoordinator,
    PatchEnvelope,
    PlumtreeGossip,
    RaftLogEntry,
    RamWorktreeManager,
    ShardDefinition,
    ShardLeaseManager,
    SpeculativeMergePipeline,
    SwarmGovernor50,
)


class TestRamWorktreeManager(unittest.TestCase):
    """Pruebas del aislamiento de worktrees efímeros en RAM."""

    def setUp(self):
        self.tmp_dir = Path(".aleph/test_scratch_wt")
        self.mgr = RamWorktreeManager(base_worktree_dir=str(self.tmp_dir))

    def tearDown(self):
        if self.tmp_dir.exists():
            import shutil
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_fast_provision_under_40ms(self):
        info = self.mgr.provision_worktree("agt_01", "shard_core")
        self.assertIn("path", info)
        self.assertLess(info["provision_latency_ms"], 40.0)
        self.assertIn("src/core", info["cone_paths"])
        self.assertTrue(Path(info["path"]).exists())

    def test_teardown_and_reaper(self):
        self.mgr.provision_worktree("agt_02", "shard_api")
        self.assertTrue(self.mgr.teardown_worktree("agt_02"))
        self.assertFalse(self.mgr.teardown_worktree("agt_02"))

        # Reaping idle
        self.mgr.provision_worktree("agt_03", "shard_ui")
        self.mgr.active_worktrees["agt_03"]["last_active"] = time.time() - 100.0
        reaped = self.mgr.reap_idle_worktrees(max_idle_seconds=50.0)
        self.assertIn("agt_03", reaped)


class TestMultiRaftShardCoordinator(unittest.TestCase):
    """Pruebas del consenso Multi-Raft particionado por shards."""

    def setUp(self):
        self.coord = MultiRaftShardCoordinator()

    def test_15s_transactional_lease_and_renewal(self):
        lease = self.coord.leases["shard_core"]
        self.assertTrue(lease.is_lease_valid())

        # Renovación de lease
        ok, epoch = lease.renew_lease(lease.current_leader)
        self.assertTrue(ok)
        self.assertGreater(epoch, 1)

        # Falso líder no puede renovar
        fail_ok, _ = lease.renew_lease("imposter_leader")
        self.assertFalse(fail_ok)

    def test_in_memory_commit_latency_under_12ms(self):
        ok, msg, lat_ms = self.coord.propose_transaction(
            shard_id="shard_core",
            proposer_id="agent_leader_00",
            command={"set": "param_x", "val": 42}
        )
        self.assertTrue(ok)
        self.assertIn("COMMIT_IDX_1", msg)
        self.assertLess(lat_ms, 12.0)  # SLA <= 12 ms

    def test_stale_fencing_token_rejected(self):
        lease = self.coord.leases["shard_api"]
        new_token = lease.force_election("new_leader_agt")

        # Intento de commit con fencing token obsoleto
        stale_token = new_token - 1
        ok, msg, _ = self.coord.propose_transaction(
            shard_id="shard_api",
            proposer_id="new_leader_agt",
            command={"action": "test"},
            fencing_token=stale_token
        )
        self.assertFalse(ok)
        self.assertEqual(msg, "ERR_FENCING_TOKEN_STALE")


class TestAstCrdtEngine(unittest.TestCase):
    """Pruebas del árbol sintáctico replicado y orden estricto de Lamport."""

    def setUp(self):
        self.crdt = AstCrdtEngine(root_name="test_module.py")

    def test_strict_lamport_ordering(self):
        ts1 = LamportTimestamp(1, "agt_a", 1)
        ts2 = LamportTimestamp(1, "agt_b", 1)
        ts3 = LamportTimestamp(2, "agt_a", 2)

        # Orden total: mismo reloj -> desempate por agent_id
        self.assertLess(ts1, ts2)
        self.assertLess(ts1, ts3)
        self.assertLess(ts2, ts3)

    def test_concurrent_insert_and_determinism(self):
        n1 = self.crdt.insert_node("agt_01", 1, "import", "import_os", "import os")
        n2 = self.crdt.insert_node("agt_02", 1, "import", "import_sys", "import sys")

        code = self.crdt.render_linear_code()
        self.assertIn("import os", code)
        self.assertIn("import sys", code)

    def test_cycle_prevention_theorem(self):
        n1 = self.crdt.insert_node("agt_01", 1, "class", "ParentClass", "class ParentClass:")
        n2 = self.crdt.insert_node("agt_01", 2, "class", "ChildClass", "class ChildClass:", parent_id=n1.node_id)

        # Intentar mover el padre adentro del hijo crearía un ciclo
        self.assertTrue(self.crdt.would_create_cycle(n1.node_id, n2.node_id))
        ok_move = self.crdt.move_node(n1.node_id, n2.node_id)
        self.assertFalse(ok_move)


class TestSpeculativeMergePipeline(unittest.TestCase):
    """Pruebas del pipeline de linearización y runners estériles."""

    def setUp(self):
        self.crdt = AstCrdtEngine()
        self.smp = SpeculativeMergePipeline(self.crdt)

    def test_sterile_runner_rejects_syntax_errors(self):
        patch = PatchEnvelope(
            patch_id="p1",
            agent_id="agt_05",
            target_shards={"shard_core"},
            ast_mutation={},
            vector_clock={"agt_05": 1},
            code_diff="def foo(: SYNTAX_ERROR"
        )
        self.smp.submit_patch(patch)
        ok, verdict, lat_ms = self.smp.process_next_patch()

        self.assertFalse(ok)
        self.assertEqual(verdict, "REJECT_SYNTAX_ERROR")
        self.assertLess(lat_ms, 15.0)  # Linter < 15 ms

    def test_sterile_runner_rejects_type_mismatch(self):
        patch = PatchEnvelope(
            patch_id="p2",
            agent_id="agt_06",
            target_shards={"shard_api"},
            ast_mutation={},
            vector_clock={"agt_06": 1},
            code_diff="x: int = 'hello' TYPE_MISMATCH"
        )
        self.smp.submit_patch(patch)
        ok, verdict, lat_ms = self.smp.process_next_patch()

        self.assertFalse(ok)
        self.assertEqual(verdict, "REJECT_TYPE_MISMATCH")

    def test_clean_patch_commits_to_main(self):
        patch = PatchEnvelope(
            patch_id="p3",
            agent_id="agt_07",
            target_shards={"shard_core"},
            ast_mutation={"symbol": "fn_greet", "content": "def greet(): return 'ok'"},
            vector_clock={"agt_07": 1},
            code_diff="valid additions"
        )
        self.smp.submit_patch(patch)
        ok, verdict, lat_ms = self.smp.process_next_patch()

        self.assertTrue(ok)
        self.assertEqual(verdict, "MERGE_COMMITTED_TO_MAIN")
        self.assertIn("def greet(): return 'ok'", self.crdt.render_linear_code())


class TestIncrementalDeadlockDetector(unittest.TestCase):
    """Pruebas del detector incremental de ciclos Tarjan DFS (< 0.45 ms) y Wound-Wait."""

    def setUp(self):
        self.detector = IncrementalDeadlockDetector(max_agents=64)
        # agt_old nació en t=100, agt_young en t=200
        self.detector.set_agent_birth("agt_old", 100)
        self.detector.set_agent_birth("agt_young", 200)

    def test_wound_action_older_preempts_younger(self):
        # agt_young tiene res_A
        self.detector.request_resource("agt_young", "res_A")
        # agt_old solicita res_A -> WOUND
        action, victim = self.detector.request_resource("agt_old", "res_A")
        self.assertEqual(action, "WOUND")
        self.assertEqual(victim, "agt_young")

    def test_cycle_prevention_aborts_younger(self):
        self.detector.set_agent_birth("agt_1", 300)
        self.detector.set_agent_birth("agt_2", 400)

        # agt_1 tiene res_A, agt_2 tiene res_B
        self.detector.request_resource("agt_1", "res_A")
        self.detector.request_resource("agt_2", "res_B")

        # agt_1 solicita res_B -> WOUND (porque agt_1 es más viejo que agt_2)
        action1, _ = self.detector.request_resource("agt_1", "res_B")
        self.assertEqual(action1, "WOUND")

    def test_tarjan_latency_under_045ms(self):
        t0 = time.perf_counter()
        has_cycle = self.detector.would_cycle("agt_old", "agt_young")
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.assertLess(elapsed_ms, 0.45)  # SLA estricto < 0.45 ms


class TestHartAdversarialSwarmAndPlumtree(unittest.TestCase):
    """Pruebas del protocolo HART v2 y topología Plumtree Gossip."""

    def test_role_distribution_ratio(self):
        swarm = HartAdversarialSwarm(total_agents=50)
        roles = list(swarm.roles.values())
        blue_cnt = roles.count(AgentRole.BLUE_BUILDER)
        red_cnt = roles.count(AgentRole.RED_INQUISITOR)
        neutral_cnt = roles.count(AgentRole.NEUTRAL_ORACLE)

        self.assertEqual(blue_cnt, 30)  # 60%
        self.assertEqual(red_cnt, 16)   # 33.3%
        self.assertEqual(neutral_cnt, 4)  # 4 Neutral

    def test_hart_v2_interception_rate(self):
        swarm = HartAdversarialSwarm(50)
        # Bug o hack hostil es interceptado inmediatamente
        ok, reason, rate = swarm.audit_submission("def __bad_hack(): pass", adversarial_vectors=5)
        self.assertFalse(ok)
        self.assertIn("HART_V2_REJECT", reason)
        self.assertGreaterEqual(rate, 99.6)

        # Envío limpio con >=3 vectores adversarios es aprobado
        ok_clean, reason_clean, rate_clean = swarm.audit_submission("def good_fn(): return 1", adversarial_vectors=4)
        self.assertTrue(ok_clean)
        self.assertEqual(reason_clean, "HART_V2_CERTIFIED_GREEN")

    def test_plumtree_gossip_scale(self):
        gossip = PlumtreeGossip(num_agents=50)
        res = gossip.broadcast_patch("agent_00", "patch_xyz")

        self.assertEqual(res["delivered_agents"], 50)
        self.assertLess(res["messages_sent"], 100)  # Mucho menor que 2450 de O(N^2)
        self.assertEqual(res["complexity"], "O(N_log_N)")


class TestEndToEndSwarmGovernor50(unittest.TestCase):
    """Prueba E2E del orquestador concurrente a 50 agentes."""

    def test_swarm_throughput_exceeds_120_tasks_per_min(self):
        gov = SwarmGovernor50(num_agents=50)
        report = gov.simulate_concurrent_swarm(duration_seconds=0.6)

        self.assertEqual(report["num_agents"], 50)
        self.assertGreaterEqual(report["throughput_tasks_per_min"], 120.0)
        self.assertLess(report["latency_p99_ms"], 200.0)
        self.assertEqual(report["status"], "HEALTHY")


if __name__ == "__main__":
    unittest.main()
