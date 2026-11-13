#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Suite de Pruebas Formales: El Aleph v4.0 Super-Swarm 1,000+ DAG-BFT Engine
Ruta: .aleph/tests/test_v4_super_swarm_bft.py
Doctrina: EL DEMIURGO - 100% Tests Verificados y Cero Margen de Error
=============================================================================
"""

import sys
import math
from pathlib import Path
try:
    import pytest
    _raises = pytest.raises
except ImportError:
    import unittest as _unittest
    _tc = _unittest.TestCase()

    def _raises(exc_type, match=None):  # type: ignore[misc]
        return _tc.assertRaisesRegex(exc_type, match) if match else _tc.assertRaises(exc_type)

# Asegurar path portable a .aleph
ALEPH_ROOT = Path(__file__).resolve().parent.parent
if str(ALEPH_ROOT) not in sys.path:
    sys.path.insert(0, str(ALEPH_ROOT))

from v4_engine.super_swarm_bft import (
    UslSample,
    UslParameters,
    UslEngine,
    TaskBid,
    AllocationResult,
    VcgAuctionEngine,
    GasMetrics,
    MultidimensionalGasPrice,
    GasControllerConfig,
    DynamicGasController,
    AgentReputationState,
    ReputationManager,
    NarwhalVertex,
    NarwhalCertificate,
    BullsharkDagEngine,
    PlumtreeNode,
    GossipData,
    IHaveMsg,
    GraftMsg,
    PruneMsg,
    SuperSwarmOrchestrator,
)


class TestUslTelemetryEngine:
    """Verificación formal de la Ley Universal de Escalabilidad (Gunther USL)."""

    def test_gunther_model_equations_and_critical_concurrency(self):
        # Parámetros objetivo de El Aleph según el plan maestro
        params = UslParameters(alpha=1.45e-5, beta=1.92e-8)

        # 1. Punto crítico N* = sqrt((1 - alpha) / beta)
        n_star = params.critical_concurrency()
        assert n_star is not None
        assert 7100.0 < n_star < 7300.0

        # 2. Linealidad a N = 1,000 agentes (> 96.6%)
        c_1000 = params.evaluate_throughput(1000.0)
        assert c_1000 > 960.0
        linearity = params.linearity_percentage_at(1000.0)
        assert linearity > 96.0

        # 3. Límites en casos extremos
        assert params.evaluate_throughput(0.0) == 0.0
        assert params.evaluate_throughput(1.0) == 1.0

        # Caso sin coherencia (beta = 0 -> Amdahl)
        params_amdahl = UslParameters(alpha=0.05, beta=0.0)
        assert params_amdahl.critical_concurrency() is None

    def test_usl_parameter_fitting_least_squares(self):
        engine = UslEngine()
        true_alpha = 0.002
        true_beta = 0.0001
        synthetic_params = UslParameters(alpha=true_alpha, beta=true_beta)

        # Generar muestras sintéticas limpias
        concurrencies = [10.0, 50.0, 100.0, 200.0, 500.0]
        for n in concurrencies:
            c = synthetic_params.evaluate_throughput(n)
            engine.record_sample(n, c)

        fitted = engine.fit_parameters()
        assert abs(fitted.alpha - true_alpha) < 1e-4
        assert abs(fitted.beta - true_beta) < 1e-5

    def test_usl_insufficient_samples_raises_error(self):
        engine = UslEngine()
        engine.record_sample(10.0, 9.5)
        engine.record_sample(20.0, 18.2)
        with _raises(ValueError, match="al menos 3 muestras"):
            engine.fit_parameters()


class TestVcgAuctionEngine:
    """Verificación de Subastas Combinatorias VCG y Compatibilidad de Incentivos (DSIC)."""

    def test_vcg_single_task_second_price_equivalence(self):
        task_id = 42
        true_cost_a = 500
        true_cost_b = 750

        bids = [
            TaskBid(bidder="agent_A", task_ids=(task_id,), claimed_cost=true_cost_a),
            TaskBid(bidder="agent_B", task_ids=(task_id,), claimed_cost=true_cost_b),
        ]

        results = VcgAuctionEngine.clear_auction([task_id], bids)
        assert len(results) == 1
        alloc = results[0]
        assert alloc.winner == "agent_A"
        # En subasta de ítem único, Clarke Pivot equivale al costo del segundo mejor (750)
        assert alloc.clarke_payment == 750

        # Utilidad neta del agente A: Pago - Costo real = 750 - 500 = 250
        utility = alloc.clarke_payment - true_cost_a
        assert utility == 250

    def test_vcg_truthfulness_property_dsic(self):
        """Demuestra que mentir (sobre-pujar o sub-pujar) no puede mejorar la utilidad."""
        task_id = 101
        true_cost = 500
        rival_cost = 750

        # Estrategia 1: Decir la verdad (b_i = 500)
        honest_bids = [
            TaskBid(bidder="agent_honest", task_ids=(task_id,), claimed_cost=true_cost),
            TaskBid(bidder="agent_rival", task_ids=(task_id,), claimed_cost=rival_cost),
        ]
        honest_res = VcgAuctionEngine.clear_auction([task_id], honest_bids)
        assert honest_res[0].winner == "agent_honest"
        utility_honest = honest_res[0].clarke_payment - true_cost
        assert utility_honest == 250

        # Estrategia 2: Sobre-pujar por encima del rival (b_i = 800)
        lie_high_bids = [
            TaskBid(bidder="agent_honest", task_ids=(task_id,), claimed_cost=800),
            TaskBid(bidder="agent_rival", task_ids=(task_id,), claimed_cost=rival_cost),
        ]
        lie_high_res = VcgAuctionEngine.clear_auction([task_id], lie_high_bids)
        # Pierde la subasta, utilidad = 0 (peor que 250)
        assert lie_high_res[0].winner == "agent_rival"

        # Estrategia 3: Sub-pujar cuando el costo real era alto (c_i = 800, pero puja 700)
        real_high_cost = 800
        lie_low_bids = [
            TaskBid(bidder="agent_honest", task_ids=(task_id,), claimed_cost=700),
            TaskBid(bidder="agent_rival", task_ids=(task_id,), claimed_cost=rival_cost),
        ]
        lie_low_res = VcgAuctionEngine.clear_auction([task_id], lie_low_bids)
        assert lie_low_res[0].winner == "agent_honest"
        # Pago es 750, pero costo real fue 800 -> Pérdida neta de -50
        utility_loss = lie_low_res[0].clarke_payment - real_high_cost
        assert utility_loss == -50

    def test_vcg_combinatorial_bundle_allocation(self):
        tasks = [1, 2, 3]
        bids = [
            # Agente 1 puja por bundle {1, 2} a costo 600
            TaskBid(bidder="agent_1", task_ids=(1, 2), claimed_cost=600),
            # Agente 2 puja por {3} a costo 300
            TaskBid(bidder="agent_2", task_ids=(3,), claimed_cost=300),
            # Agente 3 puja por {1, 2, 3} a costo 1100
            TaskBid(bidder="agent_3", task_ids=(1, 2, 3), claimed_cost=1100),
        ]

        results = VcgAuctionEngine.clear_auction(tasks, bids)
        assert len(results) == 3

        winners = {r.task_id: r.winner for r in results}
        assert winners[1] == "agent_1"
        assert winners[2] == "agent_1"
        assert winners[3] == "agent_2"


class TestDynamicGasController:
    """Verificación de Tarificación Multidimensional EIP-1559 con Quema Deflacionaria."""

    def test_gas_price_adjustment_and_elasticity_bound(self):
        target = GasMetrics(
            cpu_cycles=1000,
            memory_byte_seconds=1000,
            io_ops=1000,
            zk_air_constraints=1000,
        )
        config = GasControllerConfig(target_capacity=target, elasticity_delta=0.125)
        controller = DynamicGasController(config)

        # 1. Ronda con 100% sobre-utilización (2000 unidades en CPU)
        over_usage = GasMetrics(2000, 1000, 1000, 1000)
        new_prices = controller.update_prices_for_next_round(over_usage)

        # Precio de CPU debe subir exactamente 12.5% (de 1.0 a 1.125)
        assert abs(new_prices.price_cpu - 1.125) < 1e-4
        # El resto permanece inalterado
        assert abs(new_prices.price_mem - 0.5) < 1e-4

        # 2. Ronda con 50% sub-utilización (500 unidades en CPU)
        under_usage = GasMetrics(500, 1000, 1000, 1000)
        new_prices_2 = controller.update_prices_for_next_round(under_usage)
        assert new_prices_2.price_cpu < 1.125

    def test_gas_fee_calculation_and_deflationary_burn(self):
        target = GasMetrics(1000, 1000, 1000, 1000)
        controller = DynamicGasController(GasControllerConfig(target))
        usage = GasMetrics(cpu_cycles=100, memory_byte_seconds=200, io_ops=10, zk_air_constraints=5)

        burned, total = controller.calculate_and_burn_fee(usage, priority_tip=50)
        assert burned > 0
        assert total == burned + 50
        assert controller.total_gas_burned == burned


class TestBetaBinomialReputation:
    """Verificación de Reputación Bayesiana, Aging y Slashing Criptográfico."""

    def test_bayesian_reputation_prior_and_updates(self):
        mgr = ReputationManager(aging_factor_lambda=0.985, min_stake_required=10_000)
        agent_id = "agent_omega"
        mgr.register_agent(agent_id, 10_000)

        # Prior no informativo: alpha=1, beta=1 -> E[R] = (1+1)/(1+1+2) = 0.5
        assert mgr.get_reputation(agent_id) == 0.5

        # Registrar 10 éxitos consecutivos
        for _ in range(10):
            mgr.record_success(agent_id, weight=1.0)

        # alpha = 11, beta = 1 -> E[R] = 12 / 14 ~ 0.857
        rep = mgr.get_reputation(agent_id)
        assert rep > 0.85

    def test_operational_failure_and_quadratic_slashing(self):
        mgr = ReputationManager(aging_factor_lambda=0.985, min_stake_required=10_000)
        agent_id = "agent_faulty"
        mgr.register_agent(agent_id, 10_000)

        # Registrar fallos operativos
        slashed = mgr.record_failure(agent_id, weight=5.0)
        assert slashed > 0
        assert mgr.agents[agent_id].staked_collateral < 10_000
        assert mgr.insurance_treasury == slashed

    def test_byzantine_equivocation_total_slashing(self):
        mgr = ReputationManager(aging_factor_lambda=0.985, min_stake_required=10_000)
        agent_id = "agent_byzantine"
        mgr.register_agent(agent_id, 50_000)

        burned = mgr.slash_byzantine_equivocation(agent_id)
        assert burned == 50_000
        state = mgr.agents[agent_id]
        assert state.staked_collateral == 0
        assert state.is_slashed_byzantine is True
        assert mgr.get_reputation(agent_id) == 0.0

    def test_temporal_aging_anti_whitewashing(self):
        mgr = ReputationManager(aging_factor_lambda=0.90, min_stake_required=10_000)
        agent_id = "agent_aging"
        mgr.register_agent(agent_id, 10_000)
        mgr.record_success(agent_id, weight=10.0)

        alpha_pre = mgr.agents[agent_id].alpha_successes
        mgr.apply_epoch_aging()
        alpha_post = mgr.agents[agent_id].alpha_successes
        assert abs(alpha_post - (alpha_pre * 0.90)) < 1e-5


class TestNarwhalBullsharkConsensus:
    """Verificación del Consenso DAG-BFT Asíncrono de Narwhal-Bullshark."""

    def test_quorum_threshold_formal_bounds(self):
        # N = 4  -> f = 1 -> Quorum = 3
        # N = 10 -> f = 3 -> Quorum = 7
        # N = 1000 -> f = 333 -> Quorum = 667
        engine_4 = BullsharkDagEngine(4)
        assert engine_4.f == 1
        assert engine_4.quorum_threshold == 3

        engine_1000 = BullsharkDagEngine(1000)
        assert engine_1000.f == 333
        assert engine_1000.quorum_threshold == 667

    def test_dag_round_advancement_and_bullshark_leader_commit(self):
        # Configurar clúster de N=4 nodos (tolerancia f=1, quórum=3)
        total_nodes = 4
        engine = BullsharkDagEngine(total_nodes)
        quorum = engine.quorum_threshold

        # --- Ronda 1 (Ronda impar: Líder L_1 elegido deterministamente) ---
        r1_certs = []
        for node in range(total_nodes):
            v = NarwhalVertex(origin=node, round=1, batch_digest=f"b1_{node}", previous_certs=())
            c = NarwhalCertificate(vertex=v, signatures=tuple(range(quorum)))
            engine.insert_certificate(c)
            r1_certs.append(c)

        leader_1 = engine.elect_leader_for_round(1)
        leader_1_cert = next(c for c in r1_certs if c.vertex.origin == leader_1)

        # En ronda 1 sola, el líder aún no se compromete (necesita votos en r=2)
        assert leader_1_cert.digest not in engine.committed_digests

        # --- Ronda 2 (Ronda par: votación sobre ronda 1) ---
        r1_digests = tuple(c.digest for c in r1_certs)
        # Asegurar que los certificados de r2 referencien causalmente al líder
        for node in range(total_nodes):
            v = NarwhalVertex(origin=node, round=2, batch_digest=f"b2_{node}", previous_certs=r1_digests)
            c = NarwhalCertificate(vertex=v, signatures=tuple(range(quorum)))
            engine.insert_certificate(c)

        # Ahora el líder de la ronda 1 y sus ancestros causales deben estar linealizados
        assert leader_1_cert.digest in engine.committed_digests
        assert len(engine.linearized_sequence) >= 1

    def test_rejection_of_corrupted_quorum_certificates(self):
        engine = BullsharkDagEngine(4)
        # Ronda 2 sin quórum causal previo
        corrupted_v = NarwhalVertex(origin=0, round=2, batch_digest="bad", previous_certs=("only_one",))
        corrupted_c = NarwhalCertificate(vertex=corrupted_v, signatures=(0, 1, 2))

        with _raises(ValueError, match="Quórum causal insuficiente"):
            engine.insert_certificate(corrupted_c)


class TestPlumtreeMeshProtocol:
    """Verificación de Difusión Epidémica Estructurada Plumtree."""

    def test_eager_push_and_cycle_pruning(self):
        node_a = PlumtreeNode("A")
        node_b = PlumtreeNode("B")

        # Conectar A y B como pares eager
        node_a.add_peer("B", as_eager=True)
        node_b.add_peer("A", as_eager=True)

        msg = GossipData(message_id="msg_001", payload=b"tx_payload", hops=0)

        # 1. B recibe msg por primera vez desde A -> Lo acepta y retransmite
        actions_first = node_b.on_receive_gossip("A", msg)
        assert "msg_001" in node_b.received_messages

        # 2. B recibe el mismo mensaje de nuevo -> Detecta ciclo, demueve a lazy y envía PRUNE
        actions_dup = node_b.on_receive_gossip("A", msg)
        assert len(actions_dup) == 1
        target, prune_action = actions_dup[0]
        assert target == "A"
        assert isinstance(prune_action, PruneMsg)
        assert "A" in node_b.lazy_peers
        assert "A" not in node_b.eager_peers

    def test_lazy_ihave_timeout_and_graft(self):
        node = PlumtreeNode("C", graft_timeout_ms=1.0)
        node.add_peer("D", as_eager=False)

        # C recibe anuncio IHAVE de D
        ihave = IHaveMsg(message_ids=("msg_missing",))
        node.on_receive_ihave("D", ihave)
        assert "msg_missing" in node.missing_messages

        # Simular paso del tiempo para expirar el temporizador
        import time
        time.sleep(0.005)

        grafts = node.check_timeouts_and_graft()
        assert len(grafts) == 1
        peer, graft_msg = grafts[0]
        assert peer == "D"
        assert graft_msg.message_id == "msg_missing"
        # Enlace debe haber sido promovido a eager
        assert "D" in node.eager_peers
        assert "D" not in node.lazy_peers


class TestSuperSwarmOrchestratorScale:
    """Simulación de Escala y Resiliencia con Super-Enjambre de 1,000 Agentes."""

    def test_super_swarm_end_to_end_orchestration(self):
        # Crear orquestador con N=1,000 agentes
        orchestrator = SuperSwarmOrchestrator(total_agents=1000, initial_stake_per_agent=10_000)
        assert len(orchestrator.reputation_manager.agents) == 1000
        assert orchestrator.dag_engine.f == 333
        assert orchestrator.dag_engine.quorum_threshold == 667

        # 1. Ejecutar ronda de subasta VCG en el enjambre
        tasks = [101, 102]
        bids = [
            TaskBid(bidder="agent_0001", task_ids=(101,), claimed_cost=400),
            TaskBid(bidder="agent_0002", task_ids=(101,), claimed_cost=600),
            TaskBid(bidder="agent_0003", task_ids=(102,), claimed_cost=350),
            TaskBid(bidder="agent_0004", task_ids=(102,), claimed_cost=500),
        ]
        allocs = orchestrator.run_auction_round(tasks, bids)
        assert len(allocs) == 2
        assert allocs[0].winner == "agent_0001"
        assert allocs[0].clarke_payment == 600
        assert allocs[1].winner == "agent_0003"
        assert allocs[1].clarke_payment == 500

        # 2. Ejecutar Ronda 1 del DAG con quórum estricto (667 honestos)
        res_r1 = orchestrator.execute_dag_round(round_num=1, honest_count=667)
        assert res_r1["certificates_count"] == 667

        # 3. Ejecutar Ronda 2 del DAG con detección y slashing de nodos bizantinos
        res_r2 = orchestrator.execute_dag_round(
            round_num=2,
            honest_count=667,
            byzantine_count=333,
            byzantine_equivocators=[800, 801, 802],
        )
        assert res_r2["certificates_count"] == 667
        assert len(res_r2["slashed_byzantines"]) == 3
        # Los nodos equivocadores deben haber perdido 100% de su colateral
        for agent_id, burned in res_r2["slashed_byzantines"]:
            assert burned == 10_000
            assert orchestrator.reputation_manager.get_reputation(agent_id) == 0.0

        # 4. Verificar avance de commits de Bullshark
        assert res_r2["total_commits"] > 0

        # 5. Difusión Plumtree
        delivered_count = orchestrator.broadcast_plumtree("agent_0000", b"AST_MUTATION_CRDT_BATCH")
        assert delivered_count > 1
