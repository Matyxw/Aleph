"""
aleph_core/research_archive/cli_archive.py
Comandos CLI históricos diferidos (Cubo B) para aleph_cli.py.
"""
import ast
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, Optional, List

from aleph_core.engine import AlephEngine, AlephUniversalMCPServer


def cmd_durable_replay_bft_wave() -> int:
    from dataclasses import asdict
    from aleph_core.verification.z3_prover import DurableAgentDeterministicReplayEffectJournalAndBFTWaveProver
    rep = DurableAgentDeterministicReplayEffectJournalAndBFTWaveProver.prove_durable_agent_replay_and_bft_wave_orchestration()
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.proven_durable_replay_and_bft_wave_sound else 1


def cmd_master_release_audit(target_path: str) -> int:
    from aleph_core.verification import MasterReleaseIntegratorHigherOrderMutationAndMerklePCCAuditor
    p = Path(target_path)
    modules_map = {}
    if p.is_file():
        modules_map[str(p.name)] = p.read_text(encoding="utf-8")
    elif p.is_dir():
        for pyf in sorted(p.glob("*.py"))[:5]:
            modules_map[str(pyf.name)] = pyf.read_text(encoding="utf-8")
    rep = MasterReleaseIntegratorHigherOrderMutationAndMerklePCCAuditor.audit_and_consolidate_release(
        modules_map=modules_map
    )
    print(json.dumps({
        "release_version": rep.release_version,
        "release_ready": rep.release_ready,
        "cas_lineage_verified": rep.cas_lineage_verified,
        "total_modules_audited": rep.total_modules_audited,
        "total_functions_certified": rep.total_functions_certified,
        "total_mutants_generated": rep.total_mutants_generated,
        "higher_order_mutants_count": rep.higher_order_mutants_count,
        "equivalent_mutants_pruned_count": rep.equivalent_mutants_pruned_count,
        "killed_mutants_count": rep.killed_mutants_count,
        "survived_mutants_count": rep.survived_mutants_count,
        "effective_mutation_score_pct": rep.effective_mutation_score_pct,
        "synthesized_discriminator_tests": rep.synthesized_discriminator_tests,
        "merkle_pcc_root_hash": rep.merkle_pcc_root_hash,
        "merkle_pcc_bundle_seal": rep.merkle_pcc_bundle_seal,
        "inclusion_proofs_count": len(rep.inclusion_proofs),
        "blocking_reasons": rep.blocking_reasons,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.release_ready else 1


def cmd_spec_slsa_audit(prev_path: str, cand_path: str) -> int:
    from aleph_core.verification import SpecificationVacuityMutatorBehavioralSubtypingAndSLSAPCCAuditor
    p_prev = Path(prev_path)
    p_cand = Path(cand_path)
    prev_map = {p_prev.name: p_prev.read_text(encoding="utf-8")} if p_prev.is_file() else {}
    cand_map = {p_cand.name: p_cand.read_text(encoding="utf-8")} if p_cand.is_file() else {}
    rep = SpecificationVacuityMutatorBehavioralSubtypingAndSLSAPCCAuditor.audit_release_specifications_subtyping_and_slsa(
        candidate_modules_map=cand_map,
        previous_modules_map=prev_map
    )
    print(json.dumps({
        "release_version": rep.release_version,
        "proven_sound_and_compatible": rep.proven_sound_and_compatible,
        "vacuity_violations": rep.vacuity_violations,
        "spec_mutation_findings": rep.spec_mutation_findings,
        "liskov_subtyping_violations": rep.liskov_subtyping_violations,
        "spec_tightness_score_pct": rep.spec_tightness_score_pct,
        "signed_tree_head_sha256": rep.signed_tree_head_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.proven_sound_and_compatible else 1


def cmd_ast_merge_repro(base_f: str, branch_a_f: str, branch_b_f: str) -> int:
    from aleph_core.verification import CrossShardThreeWayASTMergerAndReproduciblePCCProver
    b0 = Path(base_f).read_text(encoding="utf-8")
    ba = Path(branch_a_f).read_text(encoding="utf-8")
    bb = Path(branch_b_f).read_text(encoding="utf-8")
    rep = CrossShardThreeWayASTMergerAndReproduciblePCCProver.merge_three_way_ast_and_prove_reproducible_pcc(b0, ba, bb)
    print(json.dumps({
        "release_version": rep.release_version,
        "merge_clean_and_conflict_free": rep.merge_clean_and_conflict_free,
        "reproducible_build_proven": rep.reproducible_build_proven,
        "branch_a_added_symbols": rep.branch_a_added_symbols,
        "branch_b_added_symbols": rep.branch_b_added_symbols,
        "merged_symbols_count": rep.merged_symbols_count,
        "delta_mutation_score_pct": rep.delta_mutation_score_pct,
        "multi_parent_merkle_dag_root": rep.multi_parent_merkle_dag_root,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if (rep.merge_clean_and_conflict_free and rep.reproducible_build_proven) else 1


def cmd_hermetic_sbom_audit(target_f: str, test_f: str = "", prop: str = "MONOTONICITY") -> int:
    from aleph_core.verification import HermeticFlakinessMetamorphicMutationAndSBOMPCCAuditor
    t_src = Path(target_f).read_text(encoding="utf-8")
    tst_src = Path(test_f).read_text(encoding="utf-8") if test_f and Path(test_f).is_file() else ""
    rep = HermeticFlakinessMetamorphicMutationAndSBOMPCCAuditor.audit_hermetic_metamorphic_and_sbom(
        target_source_code=t_src,
        test_suite_source_code=tst_src,
        metamorphic_property=prop
    )
    print(json.dumps({
        "release_version": rep.release_version,
        "proven_hermetic_and_metamorphic": rep.proven_hermetic_and_metamorphic,
        "permutation_order_independence_verified": rep.permutation_order_independence_verified,
        "metamorphic_relations_verified": rep.metamorphic_relations_verified,
        "metamorphic_mutation_kill_rate_pct": rep.metamorphic_mutation_kill_rate_pct,
        "zero_external_broken_dependencies_proven": rep.zero_external_broken_dependencies_proven,
        "sbom_pcc_seal_sha256": rep.sbom_pcc_seal_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.proven_hermetic_and_metamorphic else 1


def cmd_awwwards_ui(file_path: str, strategic_objective: str = "awwwards_editorial_scrollytelling") -> int:
    from aleph_core.verification import AwwwardsStrategicDesignAndPerceptualChoreographyEngine
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsStrategicDesignAndPerceptualChoreographyEngine.audit_and_synthesize_awwwards_ui(
        source_code=src,
        strategic_objective=strategic_objective
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "strategic_objective": rep.strategic_objective,
        "proven_awwwards_and_wcag_compliant": rep.proven_awwwards_and_wcag_compliant,
        "overall_awwwards_score": rep.overall_awwwards_score,
        "sotd_threshold_met": rep.sotd_threshold_met,
        "awwwards_jury_scores": rep.awwwards_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_diff_fuzz_intoto(ref_f: str, cand_f: str = "", parent_sha: str = "") -> int:
    from aleph_core.verification import DifferentialCoverageGuidedFuzzerAndInTotoAttestationProver
    r_src = Path(ref_f).read_text(encoding="utf-8")
    c_src = Path(cand_f).read_text(encoding="utf-8") if cand_f and Path(cand_f).is_file() else ""
    rep = DifferentialCoverageGuidedFuzzerAndInTotoAttestationProver.fuzz_branches_and_attest_intoto(
        reference_source_code=r_src,
        candidate_source_code=c_src,
        parent_bundle_sha256=parent_sha,
        release_version="7.8.0"
    )
    print(json.dumps({
        "release_version": rep.release_version,
        "proven_branch_complete_and_differentially_sound": rep.proven_branch_complete_and_differentially_sound,
        "branch_coverage_pct": rep.branch_coverage_pct,
        "intoto_pcc_seal_sha256": rep.intoto_pcc_seal_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.proven_branch_complete_and_differentially_sound else 1


def cmd_awwwards_choreography(file_path: str, component_name: str = "SovereignAwwwardsSotYCanvas") -> int:
    from aleph_core.verification import AwwwardsViewTransitionWebGLDisposableAndScrollTimelineProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsViewTransitionWebGLDisposableAndScrollTimelineProver.prove_and_synthesize_soty_choreography(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_soty_choreography_and_gpu_safe": rep.proven_soty_choreography_and_gpu_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_wcag22_cq(file_path: str, component_name: str = "SovereignAwwwardsIntrinsicBento") -> int:
    from aleph_core.verification import AwwwardsWCAG22TargetFocusContainerQueryAndVariableFontProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsWCAG22TargetFocusContainerQueryAndVariableFontProver.prove_and_synthesize_wcag22_intrinsic_soty(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_wcag22_and_intrinsic_soty_safe": rep.proven_wcag22_and_intrinsic_soty_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_inp_toplayer(file_path: str, component_name: str = "SovereignAwwwardsINPTopLayerHero") -> int:
    from aleph_core.verification import AwwwardsINPSchedulerYieldStartingStyleTopLayerAndLCPProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsINPSchedulerYieldStartingStyleTopLayerAndLCPProver.prove_and_synthesize_inp_toplayer_lcp_soty(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_inp_toplayer_and_lcp_soty_safe": rep.proven_inp_toplayer_and_lcp_soty_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_dtcg_cv_actions(file_path: str, component_name: str = "SovereignAwwwardsDTCGActionSurface") -> int:
    from aleph_core.verification import AwwwardsDTCG2025RelativeOKLCHContentVisibilityAndReact19ActionProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsDTCG2025RelativeOKLCHContentVisibilityAndReact19ActionProver.prove_and_synthesize_dtcg_relative_oklch_cv_and_actions(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_dtcg_relative_oklch_cv_and_actions_safe": rep.proven_dtcg_relative_oklch_cv_and_actions_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_speculation_rsc(file_path: str, component_name: str = "SovereignAwwwardsSpeculativeRSCShell") -> int:
    from aleph_core.verification import AwwwardsSpeculationRulesTextWrapRSCWaterfallAndForcedColorsProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsSpeculationRulesTextWrapRSCWaterfallAndForcedColorsProver.prove_and_synthesize_speculation_textwrap_rsc_and_forced_colors(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_speculation_textwrap_rsc_and_forced_colors_safe": rep.proven_speculation_textwrap_rsc_and_forced_colors_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_intrinsic_webgpu(file_path: str, component_name: str = "SovereignAwwwardsWebGPUIntrinsicStudio") -> int:
    from aleph_core.verification import AwwwardsInterpolateSizeFieldSizingRovingTabindexAndWebGPUProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsInterpolateSizeFieldSizingRovingTabindexAndWebGPUProver.prove_and_synthesize_intrinsic_sizing_roving_and_webgpu(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_intrinsic_sizing_roving_and_webgpu_safe": rep.proven_intrinsic_sizing_roving_and_webgpu_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_houdini_wcag_svg(file_path: str, component_name: str = "SovereignAwwwardsHoudiniShaderCard") -> int:
    from aleph_core.verification import AwwwardsCSSPropertyHoudiniWCAGRedundantEntryAndSVGFilterBoundsProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsCSSPropertyHoudiniWCAGRedundantEntryAndSVGFilterBoundsProver.prove_and_synthesize_houdini_wcag_useid_and_svg(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_houdini_wcag_useid_and_svg_bounds_safe": rep.proven_houdini_wcag_useid_and_svg_bounds_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_positiontry_p3_inert(file_path: str, component_name: str = "SovereignAwwwardsP3AnchoredStage") -> int:
    from aleph_core.verification import AwwwardsPositionTryWideGamutP3React19PreloadAndInertProver
    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AwwwardsPositionTryWideGamutP3React19PreloadAndInertProver.prove_and_synthesize_position_try_p3_preload_and_inert(
        source_code=src,
        component_name=component_name
    )
    print(json.dumps({
        "component_name": rep.component_name,
        "proven_position_try_p3_preload_and_inert_safe": rep.proven_position_try_p3_preload_and_inert_safe,
        "overall_soty_score": rep.overall_soty_score,
        "soty_threshold_met": rep.soty_threshold_met,
        "soty_jury_scores": rep.soty_jury_scores,
        "findings": rep.findings,
        "pcc_certificate_sha256": rep.pcc_certificate_sha256,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_awwwards_carousel_vt_wcag1413(path_or_code: str, component_name: str = "CarouselAndTooltipShowcase.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSCarouselScrollMarkerCrossDocViewTransitionAndWCAG1413Prover
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSCarouselScrollMarkerCrossDocViewTransitionAndWCAG1413Prover.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_shape_readingflow_activity(path_or_code: str, component_name: str = "AwwwardsBentoStage.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSShapeReadingFlowReact19ActivityAndAudioGuardProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSShapeReadingFlowReact19ActivityAndAudioGuardProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_css_function_scrollstate(path_or_code: str, component_name: str = "AwwwardsStickyHeaderAndOptimisticAction.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSFunctionScrollStateConsistentHelpAndOptimisticProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSFunctionScrollStateConsistentHelpAndOptimisticProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_css_if_attr_invoker(path_or_code: str, component_name: str = "AwwwardsInvokerStageV9.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSInlineIfTypedAttrInvokerCommandsAndFocusNotObscuredProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSInlineIfTypedAttrInvokerCommandsAndFocusNotObscuredProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_base_select_sibling_trim(path_or_code: str, component_name: str = "AwwwardsCustomizableSelectAndKanban.tsx") -> int:
    from aleph_core.verification import AwwwardsCustomizableSelectSiblingIndexTextBoxTrimAndWCAGDraggingProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCustomizableSelectSiblingIndexTextBoxTrimAndWCAGDraggingProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_popover_hint_effect_event(path_or_code: str, component_name: str = "AwwwardsPopoverHintAndEffectEventForm.tsx") -> int:
    from aleph_core.verification import AwwwardsPopoverHintContrastColorReact19EffectEventAndWCAGErrorProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsPopoverHintContrastColorReact19EffectEventAndWCAGErrorProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_stretch_gap_cachesignal(path_or_code: str, component_name: str = "AwwwardsBentoGapAndCacheSignalRSC.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSStretchSizingGapDecorationsCacheSignalAndWCAGTargetOffsetProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSStretchSizingGapDecorationsCacheSignalAndWCAGTargetOffsetProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_closedby_cornershape_vtclass(path_or_code: str, component_name: str = "AwwwardsSquircleDialogAndAuthModal.tsx") -> int:
    from aleph_core.verification import AwwwardsDialogClosedByCSSCornerShapeViewTransitionClassAndWCAGAutocompleteProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsDialogClosedByCSSCornerShapeViewTransitionClassAndWCAGAutocompleteProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_interest_masonry_reflow(path_or_code: str, component_name: str = "AwwwardsInterestMasonryAndActionForm.tsx") -> int:
    from aleph_core.verification import AwwwardsInterestInvokerCSSMasonryActionStateAndWCAGReflowProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsInterestInvokerCSSMasonryActionStateAndWCAGReflowProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_details_highlight_textspacing(path_or_code: str, component_name: str = "AwwwardsExclusiveAccordionAndHighlightSearch.tsx") -> int:
    from aleph_core.verification import AwwwardsExclusiveAccordionDetailsContentHighlightAPIAndWCAGTextSpacingProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsExclusiveAccordionDetailsContentHighlightAPIAndWCAGTextSpacingProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_lightdark_fontsizeadjust_pausestophide(path_or_code: str, component_name: str = "AwwwardsLightDarkAndAccessibleMarqueeStage.tsx") -> int:
    from aleph_core.verification import AwwwardsLightDarkThemeFontSizeAdjustReducedTransparencyAndWCAGPauseStopHideProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsLightDarkThemeFontSizeAdjustReducedTransparencyAndWCAGPauseStopHideProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_colormix_shapeoutside_wcag1411(path_or_code: str, component_name: str = "AwwwardsEditorialShapeAndHiDPICanvasStage.tsx") -> int:
    from aleph_core.verification import AwwwardsColorMixOKLCHShapeOutsideDevicePixelObserverAndWCAGNonTextContrastProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsColorMixOKLCHShapeOutsideDevicePixelObserverAndWCAGNonTextContrastProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_subgrid_userinvalid_wcag333(path_or_code: str, component_name: str = "AwwwardsSubgridAndWCAG333FormStage.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSSubgridRelationalHasUserInvalidAccentColorAndWCAGErrorSuggestionProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSSubgridRelationalHasUserInvalidAccentColorAndWCAGErrorSuggestionProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_linearspring_scrollbargutter_wcag334(path_or_code: str, component_name: str = "AwwwardsLinearSpringAndWCAG334TransactionDrawer.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSLinearSpringScrollbarGutterLogicalPropsAndWCAGErrorPreventionProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSLinearSpringScrollbarGutterLogicalPropsAndWCAGErrorPreventionProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_startingstyle_textboxtrim_wcag221(path_or_code: str, component_name: str = "AwwwardsTextBoxTrimAndWCAG221TimingStage.tsx") -> int:
    from aleph_core.verification import AwwwardsStartingStyleRuleOrderTextBoxTrimLogicalOverscrollAndWCAGTimingAdjustableProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsStartingStyleRuleOrderTextBoxTrimLogicalOverscrollAndWCAGTimingAdjustableProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_contrastcolor_reduceddata_wcag143(path_or_code: str, component_name: str = "AwwwardsContrastColorAndAdaptiveBandwidthStage.tsx") -> int:
    from aleph_core.verification import AwwwardsContrastColorRelativeOKLCHReducedDataPrefersContrastAndWCAG143Prover
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsContrastColorRelativeOKLCHReducedDataPrefersContrastAndWCAG143Prover.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_animationrange_oklab_wcag233(path_or_code: str, component_name: str = "AwwwardsAnimationRangeOKLabAndF95Stage.tsx") -> int:
    from aleph_core.verification import AwwwardsAnimationRangeOKLabGradientLogicalBoxSizeAndWCAG233F95Prover
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsAnimationRangeOKLabGradientLogicalBoxSizeAndWCAG233F95Prover.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_insetinline_systemcolor_wcag331(path_or_code: str, component_name: str = "AwwwardsInsetInlineSystemColorAndWCAG331Stage.tsx") -> int:
    from aleph_core.verification import AwwwardsInsetInlinePositioningSystemColorForgivingIsNotAndWCAGInputAssistanceProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsInsetInlinePositioningSystemColorForgivingIsNotAndWCAGInputAssistanceProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_colorfn_textsizeadjust_wcagstatus(path_or_code: str, component_name: str = "AwwwardsColorFnTextSizeAdjustAndPoliteOutputStage.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSColorFunctionTextSizeAdjustSmoothScrollGuardAndWCAGStatusOutputProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSColorFunctionTextSizeAdjustSmoothScrollGuardAndWCAGStatusOutputProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_lightdarkimage_inset_wcag1413(path_or_code: str, component_name: str = "AwwwardsLightDarkImageInsetAndWCAG1413Stage.tsx") -> int:
    from aleph_core.verification import AwwwardsLightDarkImageFormVariableFontWeightInsetCenteringAndWCAG1413PersistenceProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsLightDarkImageFormVariableFontWeightInsetCenteringAndWCAG1413PersistenceProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_centennial_level100_wcag22(path_or_code: str, component_name: str = "AwwwardsCentennialLevel100MasterStage.tsx") -> int:
    from aleph_core.verification import AwwwardsCentennialLevel100CompositorTransitionRemMediaAndWCAG22MasterProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCentennialLevel100CompositorTransitionRemMediaAndWCAG22MasterProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_awwwards_scrollbars_where_wcag33(path_or_code: str, component_name: str = "AwwwardsScrollbarsWhereAndWCAG33Stage.tsx") -> int:
    from aleph_core.verification import AwwwardsCSSScrollbarsStylingPseudoElementsWhereFocusWithinAndWCAGLabelProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = AwwwardsCSSScrollbarsStylingPseudoElementsWhereFocusWithinAndWCAGLabelProver.verify_and_synthesize(
        code_or_css=source,
        target_path=component_name,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_dot_aleph_audit(path_or_code: str, target_path: str = ".aleph/UNIFIED_GOVERNANCE_MANIFEST.json") -> int:
    from aleph_core.verification import DotAlephSovereignWorldDesignerAndGovernanceGateProver
    p = Path(path_or_code)
    source = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else path_or_code
    rep = DotAlephSovereignWorldDesignerAndGovernanceGateProver.verify_and_synthesize(
        code_or_manifest=source,
        target_path=target_path,
    )
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_aead_cswsh_graphql_audit(filepath: str) -> int:
    from aleph_core.verification import AEADKeyCommitmentNonceReuseCSWSHAndGraphQLComplexityProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = AEADKeyCommitmentNonceReuseCSWSHAndGraphQLComplexityProver.audit_aead_cswsh_graphql_security(src)
    print(json.dumps({
        "formal_aead_cswsh_graphql_safe": rep.formal_aead_cswsh_graphql_safe,
        "aead_nonce_and_commitment_clean": rep.aead_nonce_and_commitment_clean,
        "websocket_cswsh_origin_clean": rep.websocket_cswsh_origin_clean,
        "graphql_depth_and_alias_clean": rep.graphql_depth_and_alias_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_aead_cswsh_graphql_safe else 1


def cmd_ecdsa_ssti_ipv6_ssrf_audit(filepath: str) -> int:
    from aleph_core.verification import ECDSARFC6979InvalidCurveSSTISandboxAndIPv6MappedSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = ECDSARFC6979InvalidCurveSSTISandboxAndIPv6MappedSSRFProver.audit_ecdsa_ssti_and_ipv6_ssrf_security(src)
    print(json.dumps({
        "formal_ecdsa_ssti_ipv6_ssrf_safe": rep.formal_ecdsa_ssti_ipv6_ssrf_safe,
        "ecdsa_rfc6979_and_ecdh_curve_clean": rep.ecdsa_rfc6979_and_ecdh_curve_clean,
        "ssti_sandboxed_template_clean": rep.ssti_sandboxed_template_clean,
        "ipv6_mapped_and_encoded_ssrf_clean": rep.ipv6_mapped_and_encoded_ssrf_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_ecdsa_ssti_ipv6_ssrf_safe else 1


def cmd_jwk_rsaoaep_sri_audit(filepath: str) -> int:
    from aleph_core.verification import JWKHeaderInjectionAlgorithmConfusionRSAOAEPAndSRICrossOriginProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = JWKHeaderInjectionAlgorithmConfusionRSAOAEPAndSRICrossOriginProver.audit_jwk_rsaoaep_and_sri_security(src)
    print(json.dumps({
        "formal_jwk_rsaoaep_sri_safe": rep.formal_jwk_rsaoaep_sri_safe,
        "jwt_rfc8725_header_and_alg_clean": rep.jwt_rfc8725_header_and_alg_clean,
        "rsa_oaep_sha256_anti_marvin_clean": rep.rsa_oaep_sha256_anti_marvin_clean,
        "sri_and_cross_origin_isolation_clean": rep.sri_and_cross_origin_isolation_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_jwk_rsaoaep_sri_safe else 1


def cmd_webauthn_nosql_archive_audit(filepath: str) -> int:
    from aleph_core.verification import WebAuthnPasskeyOriginBindingNoSQLLDAPAndArchiveSlipProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = WebAuthnPasskeyOriginBindingNoSQLLDAPAndArchiveSlipProver.audit_webauthn_nosql_and_archive_security(src)
    print(json.dumps({
        "formal_webauthn_nosql_archive_safe": rep.formal_webauthn_nosql_archive_safe,
        "webauthn_fido2_origin_and_counter_clean": rep.webauthn_fido2_origin_and_counter_clean,
        "nosql_and_ldap_filter_taint_clean": rep.nosql_and_ldap_filter_taint_clean,
        "archive_zip_tar_slip_clean": rep.archive_zip_tar_slip_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_webauthn_nosql_archive_safe else 1


def cmd_argon2id_host_grpc_audit(filepath: str) -> int:
    from aleph_core.verification import Argon2idHKDFKeyDerivationHostHeaderInjectionAndgRPCFramingProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = Argon2idHKDFKeyDerivationHostHeaderInjectionAndgRPCFramingProver.audit_argon2id_hkdf_host_and_grpc_security(src)
    print(json.dumps({
        "formal_argon2id_hkdf_host_grpc_safe": rep.formal_argon2id_hkdf_host_grpc_safe,
        "argon2id_rfc9106_and_hkdf_clean": rep.argon2id_rfc9106_and_hkdf_clean,
        "host_header_and_sni_binding_clean": rep.host_header_and_sni_binding_clean,
        "grpc_protobuf_framing_and_reflection_clean": rep.grpc_protobuf_framing_and_reflection_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_argon2id_hkdf_host_grpc_safe else 1


def cmd_trojan_x509_webhook_audit(filepath: str) -> int:
    from aleph_core.verification import TrojanSourceUnicodePromptExfilX509mTLSAndWebhookReplayProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = TrojanSourceUnicodePromptExfilX509mTLSAndWebhookReplayProver.audit_trojan_x509_and_webhook_security(src)
    print(json.dumps({
        "formal_trojan_x509_webhook_safe": rep.formal_trojan_x509_webhook_safe,
        "unicode_bidi_and_markdown_exfil_clean": rep.unicode_bidi_and_markdown_exfil_clean,
        "x509_mtls_san_and_context_clean": rep.x509_mtls_san_and_context_clean,
        "webhook_hmac_timestamp_replay_clean": rep.webhook_hmac_timestamp_replay_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_trojan_x509_webhook_safe else 1


def cmd_opaque_framesrc_torchserve_audit(filepath: str) -> int:
    from aleph_core.verification import OPAQUEAsymmetricPAKECSPFrameSrcAndTorchServeTritonSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = OPAQUEAsymmetricPAKECSPFrameSrcAndTorchServeTritonSSRFProver.audit_opaque_pake_csp_frame_src_and_torchserve_triton_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_opaque_framesrc_torchserve_safe else 1


def cmd_rfc9496_objectsrc_kafkaconnect_audit(filepath: str) -> int:
    from aleph_core.verification import Ristretto255RFC9496CSPObjectSrcAndKafkaConnectSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = Ristretto255RFC9496CSPObjectSrcAndKafkaConnectSSRFProver.audit_rfc9496_ristretto255_csp_object_src_and_kafka_connect_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rfc9496_objectsrc_kafkaconnect_safe else 1


def cmd_rats_stylesrc_vectordb_audit(filepath: str) -> int:
    from aleph_core.verification import RATSEATRFC9334CSPStyleSrcExfilAndVectorDBQdrantWeaviateSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = RATSEATRFC9334CSPStyleSrcExfilAndVectorDBQdrantWeaviateSSRFProver.audit_rats_eat_rfc9334_csp_style_src_and_vectordb_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rats_stylesrc_vectordb_safe else 1


def cmd_rfc9258_scriptattr_airflow_audit(filepath: str) -> int:
    from aleph_core.verification import TLS13EPSKRFC9258CSPScriptSrcAttrAndAirflowPrefectSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = TLS13EPSKRFC9258CSPScriptSrcAttrAndAirflowPrefectSSRFProver.audit_rfc9258_epsk_csp_script_attr_and_airflow_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rfc9258_scriptattr_airflow_safe else 1


def cmd_rfc9580_reporting_nomad_audit(filepath: str) -> int:
    from aleph_core.verification import OpenPGPRFC9580SEIPDv2ReportingEndpointsAndNomadSupervisordSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = OpenPGPRFC9580SEIPDv2ReportingEndpointsAndNomadSupervisordSSRFProver.audit_rfc9580_openpgp_reporting_endpoints_and_nomad_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rfc9580_reporting_nomad_safe else 1


def cmd_rfc9530_frameancestors_spark_audit(filepath: str) -> int:
    from aleph_core.verification import DigestFieldsRFC9530CSPFrameAncestorsAndSparkFlinkClusterSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = DigestFieldsRFC9530CSPFrameAncestorsAndSparkFlinkClusterSSRFProver.audit_rfc9530_digest_frame_ancestors_and_spark_flink_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rfc9530_frameancestors_spark_safe else 1


def cmd_ecvrf_formaction_prometheus_audit(filepath: str) -> int:
    from aleph_core.verification import ECVRFRFC9381CSPFormActionAndPrometheusGrafanaSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = ECVRFRFC9381CSPFormActionAndPrometheusGrafanaSSRFProver.audit_ecvrf_csp_form_action_and_prometheus_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ecvrf_formaction_prometheus_safe else 1


def cmd_blindrsa_permissions_kubelet_audit(filepath: str) -> int:
    from aleph_core.verification import BlindRSARFC9474PermissionsPolicyAndKubeletCRISSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = BlindRSARFC9474PermissionsPolicyAndKubeletCRISSRFProver.audit_blindrsa_permissions_policy_and_kubelet_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_blindrsa_permissions_kubelet_safe else 1


def cmd_spake2plus_speculation_cdp_audit(filepath: str) -> int:
    from aleph_core.verification import SPAKE2PlusRFC9383SpeculationRulesAndCDPInspectorSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = SPAKE2PlusRFC9383SpeculationRulesAndCDPInspectorSSRFProver.audit_spake2plus_speculation_rules_and_cdp_ssrf(source_code=src, target_path=filepath)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_spake2plus_speculation_cdp_safe else 1


def cmd_rfc9380_docisolation_ray_audit(filepath: str) -> int:
    from aleph_core.verification import HashToCurveRFC9380DocIsolationAndRayOllamaClusterSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = HashToCurveRFC9380DocIsolationAndRayOllamaClusterSSRFProver.audit_rfc9380_doc_isolation_and_ray_ollama_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rfc9380_docisolation_ray_safe else 1


def cmd_frost_referrer_vault_audit(filepath: str) -> int:
    from aleph_core.verification import FROSTRFC9591ReferrerPolicyAndVaultWireserverSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = FROSTRFC9591ReferrerPolicyAndVaultWireserverSSRFProver.audit_frost_referrer_policy_and_vault_wireserver_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_frost_referrer_vault_safe else 1


def cmd_mls_importmap_cilium_audit(filepath: str) -> int:
    from aleph_core.verification import MLSRFC9420ImportMapCSPAndCiliumHubbleCNISSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = MLSRFC9420ImportMapCSPAndCiliumHubbleCNISSRFProver.audit_mls_importmap_csp_and_cilium_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_mls_importmap_cilium_safe else 1


def cmd_oprf_trustedtypes_fcgi_audit(filepath: str) -> int:
    from aleph_core.verification import OPRFRFC9497TrustedTypesDOMAndFastCGIRedisSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = OPRFRFC9497TrustedTypesDOMAndFastCGIRedisSSRFProver.audit_oprf_trusted_types_and_fastcgi_redis_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_oprf_trustedtypes_fastcgi_safe else 1


def cmd_dpop_fencedframe_h2c_audit(filepath: str) -> int:
    from aleph_core.verification import DPoPRFC9449CSPFencedFrameAndH2CgRPCReflectionSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = DPoPRFC9449CSPFencedFrameAndH2CgRPCReflectionSSRFProver.audit_dpop_fenced_frame_and_h2c_grpc_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_dpop_fencedframe_h2c_safe else 1


def cmd_uuidv7_sandbox_altsvc_audit(filepath: str) -> int:
    from aleph_core.verification import UUIDv7RFC9562CSPSandboxIframeAndAltSvcSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = UUIDv7RFC9562CSPSandboxIframeAndAltSvcSSRFProver.audit_uuidv7_csp_sandbox_and_altsvc_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_uuidv7_sandbox_altsvc_safe else 1


def cmd_rfc9421_clearsitedata_etcd_audit(filepath: str) -> int:
    from aleph_core.verification import HTTPMessageSigRFC9421ClearSiteDataAndConsulEtcdSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = HTTPMessageSigRFC9421ClearSiteDataAndConsulEtcdSSRFProver.audit_rfc9421_clear_site_data_and_etcd_consul_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_rfc9421_clearsite_consul_safe else 1


def cmd_cose_fetchmeta_connect_audit(filepath: str) -> int:
    from aleph_core.verification import COSERFC9052FetchMetadataAndHTTPConnectTunnelSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = COSERFC9052FetchMetadataAndHTTPConnectTunnelSSRFProver.audit_cose_fetch_metadata_and_connect_tunnel_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_cose_fetchmeta_connect_safe else 1


def cmd_sdjwt_worker_uds_audit(filepath: str) -> int:
    from aleph_core.verification import SDJWTRFC9901CSPWorkerSrcAndUnixSocketDockerSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = SDJWTRFC9901CSPWorkerSrcAndUnixSocketDockerSSRFProver.audit_sdjwt_csp_worker_and_unix_socket_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_sdjwt_worker_uds_safe else 1


def cmd_jwe_csp_baseuri_envoy_audit(filepath: str) -> int:
    from aleph_core.verification import JWERFC8725bisECDHESCSPBaseURIAndEnvoyMeshSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = JWERFC8725bisECDHESCSPBaseURIAndEnvoyMeshSSRFProver.audit_jwe_csp_baseuri_and_envoy_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_jwe_csp_baseuri_envoy_safe else 1


def cmd_tls13_xsleaks_urlparser_audit(filepath: str) -> int:
    from aleph_core.verification import TLS13ZeroRTTXSLeaksCOOPCORPAndURLParserSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = TLS13ZeroRTTXSLeaksCOOPCORPAndURLParserSSRFProver.audit_tls13_xsleaks_and_urlparser_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_tls13_xsleaks_urlparser_safe else 1


def cmd_hpke_oauth_headless_turn_audit(filepath: str) -> int:
    from aleph_core.verification import HPKERFC9180OAuthRFC9700MixUpAndHeadlessTURNSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = HPKERFC9180OAuthRFC9700MixUpAndHeadlessTURNSSRFProver.audit_hpke_oauth_rfc9700_and_headless_turn_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_hpke_oauth_headless_turn_safe else 1


def cmd_slhdsa_postmessage_imdsv2_audit(filepath: str) -> int:
    from aleph_core.verification import SLHDSAFIPS205PostMessageDOMClobberingAndIMDSv2ProxySSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = SLHDSAFIPS205PostMessageDOMClobberingAndIMDSv2ProxySSRFProver.audit_slhdsa_postmessage_and_imdsv2_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_slhdsa_postmessage_imdsv2_safe else 1


def cmd_mldsa_saml_redirect_audit(filepath: str) -> int:
    from aleph_core.verification import MLDSAFIPS204SAMLCanonicalizationAndHTTPRedirectSSRFProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = MLDSAFIPS204SAMLCanonicalizationAndHTTPRedirectSSRFProver.audit_mldsa_saml_and_redirect_ssrf(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_mldsa_saml_redirect_safe else 1


def cmd_pqc_cookie_dns_rebind_audit(filepath: str) -> int:
    from aleph_core.verification import PQCKyberSlashCookiePrefixCRLFAndDNSRebindingTOCTOUProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = PQCKyberSlashCookiePrefixCRLFAndDNSRebindingTOCTOUProver.audit_pqc_cookie_crlf_and_dns_rebinding(source_code=src)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.formal_pqc_cookie_dns_rebinding_safe else 1


def cmd_cors_mass_assign_svg_audit(filepath: str) -> int:
    from aleph_core.verification import CORSNullOriginWildcardCredentialsCSPReflectedXSSAndMassAssignmentProver
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    rep = CORSNullOriginWildcardCredentialsCSPReflectedXSSAndMassAssignmentProver.audit_cors_mass_assign_and_svg_security(src)
    print(json.dumps({
        "formal_cors_mass_assign_svg_safe": rep.formal_cors_mass_assign_svg_safe,
        "cors_origin_and_credentials_clean": rep.cors_origin_and_credentials_clean,
        "bopla_mass_assignment_clean": rep.bopla_mass_assignment_clean,
        "svg_polyglot_upload_and_nosniff_clean": rep.svg_polyglot_upload_and_nosniff_clean,
        "violations": [v.__dict__ for v in rep.violations],
        "remediation_patches": rep.remediation_patches,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_cors_mass_assign_svg_safe else 1


def cmd_ocsp_permissions_sonicwall_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import OCSPRFC6960RevocationNoncePermissionsPolicyAndSonicWallPlunkAVideoSSRFProver
    prover = OCSPRFC6960RevocationNoncePermissionsPolicyAndSonicWallPlunkAVideoSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ocsp_permissions_sonicwall_plunk_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ocsp_permissions_sonicwall_plunk_safe else 1


def cmd_ct_rfc9162_coop_craft_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import CertTransparencyRFC9162SCTCOOPOriginAgentClusterAndCraftDirectusSSRFProver
    prover = CertTransparencyRFC9162SCTCOOPOriginAgentClusterAndCraftDirectusSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ct_rfc9162_coop_craft_directus_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ct_rfc9162_coop_craft_directus_safe else 1


def cmd_tls_rfc8879_integrity_gitlab_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import TLSCertCompressionRFC8879IntegrityPolicyAndGitLabSpringAstroSSRFProver
    prover = TLSCertCompressionRFC8879IntegrityPolicyAndGitLabSpringAstroSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_tls_rfc8879_integrity_gitlab_spring_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_tls_rfc8879_integrity_gitlab_spring_safe else 1


def cmd_ct_consistency_permissions_ai_nextjs_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import CTRFC9162ConsistencyPrecertPermissionsPolicyAIAndNextJSAzureLinkerdSSRFProver
    prover = CTRFC9162ConsistencyPrecertPermissionsPolicyAIAndNextJSAzureLinkerdSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ct_consistency_permissions_ai_nextjs_azure_linkerd_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ct_consistency_permissions_ai_nextjs_azure_linkerd_safe else 1


def cmd_ocsp_ext_revoked_mcp_ssrf_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import OCSPRFC6960ExtendedRevokedCertIDPermissionsPolicyTokensAndMCPAtlassianFastMCPSSRFProver
    prover = OCSPRFC6960ExtendedRevokedCertIDPermissionsPolicyTokensAndMCPAtlassianFastMCPSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ocsp_ext_revoked_permissions_tokens_mcp_atlassian_fastmcp_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ocsp_ext_revoked_permissions_tokens_mcp_atlassian_fastmcp_safe else 1


def cmd_ocsp_sigalg_docker_lmdeploy_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import OCSPRFC6960PreferredSigAlgDowngradePermissionsSensorsAndDockerModelRunnerLMDeploySSRFProver
    prover = OCSPRFC6960PreferredSigAlgDowngradePermissionsSensorsAndDockerModelRunnerLMDeploySSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ocsp_sigalg_permissions_sensors_docker_lmdeploy_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ocsp_sigalg_permissions_sensors_docker_lmdeploy_safe else 1


def cmd_ocsp_archive_cutoff_alt_ip_ssrf_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import OCSPRFC6960ArchiveCutoffCrlIDPermissionsMediaDevicesAndAlternateIPCloudMetadataSSRFProver
    prover = OCSPRFC6960ArchiveCutoffCrlIDPermissionsMediaDevicesAndAlternateIPCloudMetadataSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ocsp_archive_cutoff_permissions_media_alternate_ip_ssrf_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ocsp_archive_cutoff_permissions_media_alternate_ip_ssrf_safe else 1


def cmd_ocsp_servicelocator_pinned_ssrf_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import OCSPRFC6960ServiceLocatorHoldInstructionPermissionsPaymentGeolocationAndPinnedSocketSSRFProver
    prover = OCSPRFC6960ServiceLocatorHoldInstructionPermissionsPaymentGeolocationAndPinnedSocketSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_ocsp_service_locator_permissions_payment_pinned_ssrf_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_ocsp_service_locator_permissions_payment_pinned_ssrf_safe else 1


def cmd_css_scope_style_focus_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsCSSScopeDonutStyleQueriesAndWCAGFocusOrderTrapProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsCSSScopeDonutStyleQueriesAndWCAGFocusOrderTrapProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_vt_anchor_focus_obscured_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsViewTransitionsL2AnchorFallbacksAndWCAGFocusNotObscuredProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsViewTransitionsL2AnchorFallbacksAndWCAGFocusNotObscuredProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_textbox_calcsize_auth_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsTextBoxCapAlphabeticCalcSizeAndWCAGAccessibleAuthProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsTextBoxCapAlphabeticCalcSizeAndWCAGAccessibleAuthProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_viewtimeline_posvis_help_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsViewTimelineEntryExitPositionVisibilityAndWCAGConsistentHelpProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsViewTimelineEntryExitPositionVisibilityAndWCAGConsistentHelpProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_relative_oklch_startingstyle_redundant_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsRelativeOKLCHContrastColorStartingStyleAndWCAGRedundantEntryProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsRelativeOKLCHContrastColorStartingStyleAndWCAGRedundantEntryProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_subgrid_contentvis_reflow_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsCSSSubgridContentVisibilityAndWCAGReflowTextSpacingProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsCSSSubgridContentVisibilityAndWCAGReflowTextSpacingProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_popover_interpolatesize_target_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsPopoverTopLayerInterpolateSizeAndWCAGTargetSizeDraggingProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsPopoverTopLayerInterpolateSizeAndWCAGTargetSizeDraggingProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_fieldsizing_uservalid_error_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsCSSFieldSizingUserValidAccentColorAndWCAGErrorSuggestionProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsCSSFieldSizingUserValidAccentColorAndWCAGErrorSuggestionProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_linearspring_scrollbargutter_errorprev_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsCSSLinearSpringScrollbarGutterAndWCAGErrorPreventionProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsCSSLinearSpringScrollbarGutterAndWCAGErrorPreventionProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_lightdark_colormix_nontext_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsCSSLightDarkColorMixOKLCHAndWCAGNonTextContrastProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsCSSLightDarkColorMixOKLCHAndWCAGNonTextContrastProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_speculationrules_textwrap_forcedcolors_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsSpeculationRulesTextWrapBalanceAndWCAGForcedColorsProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsSpeculationRulesTextWrapBalanceAndWCAGForcedColorsProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_houdini_fontsizeadjust_pause_audit(filepath: str, accent: str = "oklch(0.68 0.19 265)") -> int:
    from dataclasses import asdict
    from aleph_core.verification import AwwwardsCSSPropertyHoudiniFontSizeAdjustAndWCAGPauseStopHideProver
    p = Path(filepath)
    content = p.read_text(encoding="utf-8") if p.exists() else filepath
    rep = AwwwardsCSSPropertyHoudiniFontSizeAdjustAndWCAGPauseStopHideProver.verify_and_synthesize(
        code_or_css=content,
        target_path=str(filepath),
        brand_accent_oklch=accent,
    )
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_verify_dict(target_file: str) -> int:
    from aleph_core.verification import SymbolicDictionarySchemaProver
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = SymbolicDictionarySchemaProver.audit_function(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "function": rep.function_name,
        "formal_proof_passed": rep.formal_proof_passed,
        "accessed_keys": rep.accessed_keys,
        "safe_accesses_count": rep.safe_accesses_count,
        "unsafe_keys_missing": rep.unsafe_keys_missing,
        "synthesized_contracts": rep.synthesized_contracts,
        "solver_duration_ms": rep.solver_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_proof_passed else 1


def cmd_verify_complexity(target_file: str) -> int:
    from aleph_core.verification import AsymptoticComplexityVerifier
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = AsymptoticComplexityVerifier.audit_code(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "function": rep.function_name,
        "worst_case_complexity": rep.worst_case_complexity,
        "max_loop_nesting_depth": rep.max_loop_nesting_depth,
        "has_n_plus_one_query": rep.has_n_plus_one_query,
        "n_plus_one_details": rep.n_plus_one_details,
        "loop_hotspots": rep.loop_hotspots,
        "safe_for_sla": rep.safe_for_sla,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.safe_for_sla else 1


def cmd_deadlock_gate(target_file_or_dir: str = ".") -> int:
    from aleph_core.verification import LockOrderingDeadlockProver
    p = Path(target_file_or_dir)
    files = {}
    if p.is_file():
        files[p.name] = p.read_text(encoding="utf-8")
    else:
        for f in p.rglob("*.py"):
            if not any(ign in f.parts for ign in ("__pycache__", ".venv", "tests")):
                files[str(f.relative_to(p))] = f.read_text(encoding="utf-8", errors="ignore")
    rep = LockOrderingDeadlockProver.audit_codebase(files)
    print(json.dumps({
        "deadlock_free": rep.deadlock_free,
        "analyzed_locks": rep.analyzed_locks,
        "lock_order_edges_count": rep.lock_order_edges_count,
        "detected_cycles": rep.detected_cycles,
        "violating_traces": rep.violating_traces,
        "remediation_advice": rep.remediation_advice,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.deadlock_free else 1


def cmd_index_synth(target_file_or_dir: str = ".") -> int:
    from aleph_core.verification import DatabaseIndexSynthesizer
    p = Path(target_file_or_dir)
    files = {}
    if p.is_file():
        files[p.name] = p.read_text(encoding="utf-8")
    else:
        for f in p.rglob("*.py"):
            if not any(ign in f.parts for ign in ("__pycache__", ".venv", "tests")):
                files[str(f.relative_to(p))] = f.read_text(encoding="utf-8", errors="ignore")
    rep = DatabaseIndexSynthesizer.synthesize_from_codebase(files)
    print(json.dumps({
        "analyzed_queries_count": rep.analyzed_queries_count,
        "unindexed_scan_risks": rep.unindexed_scan_risks,
        "recommended_indexes": [
            {
                "table": idx.table_name,
                "columns": idx.columns,
                "sql_ddl": idx.sql_ddl,
                "covering_query_count": idx.covering_query_count
            }
            for idx in rep.recommended_indexes
        ],
        "synthesis_ddl": rep.synthesis_ddl,
        "safe_for_production": rep.safe_for_production,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.safe_for_production else 1


def cmd_leak_check(target_file: str) -> int:
    from aleph_core.verification import ResourceLeakAndCycleProver
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = ResourceLeakAndCycleProver.audit_code(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "resource_leak_free": rep.resource_leak_free,
        "total_resources_analyzed": rep.total_resources_analyzed,
        "safe_resources_count": rep.safe_resources_count,
        "safe_with_contexts_count": rep.safe_with_contexts_count,
        "leaks": [
            {
                "type": l.resource_type,
                "var": l.variable_name,
                "line": l.acquisition_line,
                "description": l.description,
                "remediation": l.remediation
            }
            for l in rep.leaks_detected
        ],
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.resource_leak_free else 1


def cmd_drift_check(orig_file: str, cand_file: str) -> int:
    from aleph_core.verification import APIContractDriftVerifier
    p1, p2 = Path(orig_file), Path(cand_file)
    if not p1.exists() or not p2.exists():
        print("Error: archivos original o candidato no encontrados.", file=sys.stderr)
        return 1
    rep = APIContractDriftVerifier.compare_contracts(
        p1.read_text(encoding="utf-8"),
        p2.read_text(encoding="utf-8")
    )
    print(json.dumps({
        "backward_compatible": rep.backward_compatible,
        "endpoints_analyzed": rep.endpoints_analyzed,
        "breaking_changes_count": rep.breaking_changes_count,
        "safe_enhancements_count": rep.safe_enhancements_count,
        "violations": [
            {
                "endpoint": v.endpoint_name,
                "change_type": v.change_type,
                "is_breaking": v.is_breaking,
                "target_entity": v.target_entity,
                "description": v.description,
                "guidance": v.migration_guidance
            }
            for v in rep.violations
        ],
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.backward_compatible else 1


def cmd_verify_saga(saga_file: str) -> int:
    from aleph_core.verification import DistributedSagaCompensatorProver
    p = Path(saga_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {saga_file}", file=sys.stderr)
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    rep = DistributedSagaCompensatorProver.verify_saga_dict(data)
    print(json.dumps({
        "saga_name": rep.saga_name,
        "formal_proof_passed": rep.formal_proof_passed,
        "compensability_proven": rep.compensability_proven,
        "idempotency_proven": rep.idempotency_proven,
        "uncompensated_steps": rep.uncompensated_steps,
        "missing_idempotency_steps": rep.missing_idempotency_steps,
        "recovery_trace_summary": rep.recovery_trace_summary,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_proof_passed else 1


def cmd_retry_check(target_file: str) -> int:
    from aleph_core.verification import CircuitBreakerBackoffProver
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = CircuitBreakerBackoffProver.audit_code(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "function_name": rep.function_name,
        "retry_storm_safe": rep.retry_storm_safe,
        "retry_loops_count": rep.retry_loops_count,
        "has_exponential_backoff": rep.has_exponential_backoff,
        "has_jitter": rep.has_jitter,
        "max_retries_bounded": rep.max_retries_bounded,
        "vulnerabilities": rep.vulnerabilities,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.retry_storm_safe else 1


def cmd_verify_policy(policy_file: str) -> int:
    from aleph_core.verification import FirstOrderAuthorizationProver
    p = Path(policy_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {policy_file}", file=sys.stderr)
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    rep = FirstOrderAuthorizationProver.verify_policies_dict(data)
    print(json.dumps({
        "policy_set_name": rep.policy_set_name,
        "formal_safety_proven": rep.formal_safety_proven,
        "default_deny_proven": rep.default_deny_proven,
        "shadowed_policies": rep.shadowed_policies,
        "escalation_witnesses": rep.escalation_witnesses,
        "remediation_advice": rep.remediation_advice,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_safety_proven else 1


def cmd_outbox_audit(target_file: str) -> int:
    from aleph_core.verification import TransactionalOutboxCausalProver
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = TransactionalOutboxCausalProver.audit_code(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "causal_integrity_proven": rep.causal_integrity_proven,
        "analyzed_mutations_count": rep.analyzed_mutations_count,
        "paired_outbox_events_count": rep.paired_outbox_events_count,
        "dual_write_violations": [
            {
                "function": v.function_name,
                "line": v.line_number,
                "table": v.domain_table_updated,
                "type": v.violation_type,
                "description": v.description,
                "remediation": v.remediation
            }
            for v in rep.dual_write_violations
        ],
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.causal_integrity_proven else 1


def cmd_verify_ha(cluster_file: str) -> int:
    from aleph_core.verification import HighAvailabilityFailoverProver
    p = Path(cluster_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {cluster_file}", file=sys.stderr)
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    rep = HighAvailabilityFailoverProver.verify_failover_dict(data)
    print(json.dumps({
        "cluster_name": rep.cluster_name,
        "formal_safety_proven": rep.formal_safety_proven,
        "quorum_threshold": rep.quorum_threshold,
        "split_brain_safe": rep.split_brain_safe,
        "fencing_token_monotone": rep.fencing_token_monotone,
        "data_loss_safe": rep.data_loss_safe,
        "promoted_node_id": rep.promoted_node_id,
        "detected_violations": rep.detected_violations,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_safety_proven else 1


def cmd_privacy_audit(target_file: str) -> int:
    from aleph_core.verification import DifferentialTelemetryPrivacyProver
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = DifferentialTelemetryPrivacyProver.audit_code(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "zero_leakage_proven": rep.zero_leakage_proven,
        "analyzed_log_calls_count": rep.analyzed_log_calls_count,
        "sanitized_logs_count": rep.sanitized_logs_count,
        "pii_leaks": [
            {
                "function": f.function_name,
                "line": f.line_number,
                "field": f.sensitive_field,
                "description": f.description,
                "remediation": f.remediation
            }
            for f in rep.pii_leaks_detected
        ],
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.zero_leakage_proven else 1


def cmd_repomap(target_dir: str = ".", budget: int = 1024) -> int:
    from aleph_core.verification import PageRankRepoMapEngine
    root = Path(target_dir)
    files_map = {}
    for ext in ("*.py", "*.ts", "*.tsx", "*.rs", "*.sql"):
        for p in root.rglob(ext):
            if "__pycache__" not in str(p) and ".git" not in str(p):
                try:
                    files_map[str(p.relative_to(root))] = p.read_text(encoding="utf-8")
                except Exception:
                    pass
    rep = PageRankRepoMapEngine.build_repo_map(files_map, max_token_budget=budget)
    print(rep.packed_repo_map_markdown)
    return 0


def cmd_frontend_ui(target_file: str) -> int:
    from aleph_core.verification import FrontendUIArchitectureProverAndSynthesizer
    p = Path(target_file)
    rep = FrontendUIArchitectureProverAndSynthesizer.audit_and_instrument_ui(
        p.read_text(encoding="utf-8"), component_name=p.stem
    )
    print(json.dumps({
        "formal_ui_soundness_proven": rep.formal_ui_soundness_proven,
        "hydration_safe": rep.hydration_safe,
        "hook_cycle_free": rep.hook_cycle_free,
        "wcag_aa_compliant": rep.wcag_aa_compliant,
        "async_tristate_complete": rep.async_tristate_complete,
        "violations_count": len(rep.violations),
        "dom_to_ast_nodes": len(rep.dom_to_ast_map),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_ui_soundness_proven else 1


def cmd_fullstack_rls(sql_file: str, ts_file: Optional[str] = None) -> int:
    from aleph_core.verification import FullStackRLSAndSchemaIsomorphismProver
    sql_src = Path(sql_file).read_text(encoding="utf-8")
    ts_src = Path(ts_file).read_text(encoding="utf-8") if ts_file and Path(ts_file).exists() else ""
    rep = FullStackRLSAndSchemaIsomorphismProver.verify_fullstack_contract(sql_src, ts_src)
    print(json.dumps({
        "formal_fullstack_safety_proven": rep.formal_fullstack_safety_proven,
        "rls_zero_trust_proven": rep.rls_zero_trust_proven,
        "client_bundle_leak_free": rep.client_bundle_leak_free,
        "schema_isomorphism_proven": rep.schema_isomorphism_proven,
        "synthesized_typescript_contract": rep.synthesized_typescript_contract,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_fullstack_safety_proven else 1


def cmd_zero_downtime_ddl(sql_file: str) -> int:
    from aleph_core.verification import ZeroDowntimeDDLProver
    sql_src = Path(sql_file).read_text(encoding="utf-8")
    rep = ZeroDowntimeDDLProver.audit_ddl(sql_src)
    print(json.dumps({
        "zero_downtime_safe": rep.zero_downtime_safe,
        "statements_analyzed_count": rep.statements_analyzed_count,
        "violations": [
            {
                "line": v.line_number,
                "statement": v.statement,
                "type": v.violation_type,
                "severity": v.severity,
                "description": v.description,
                "remediation": v.remediation
            }
            for v in rep.violations
        ],
        "safe_migration_plan": rep.safe_migration_plan,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.zero_downtime_safe else 1


def cmd_state_rollback(target_file: str) -> int:
    from aleph_core.verification import GlobalStateAndOptimisticUIRollbackProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = GlobalStateAndOptimisticUIRollbackProver.audit_state_and_mutations(code_src)
    print(json.dumps({
        "formal_resilience_proven": rep.formal_resilience_proven,
        "immutability_safe": rep.immutability_safe,
        "rollback_guaranteed": rep.rollback_guaranteed,
        "cache_sync_proven": rep.cache_sync_proven,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_resilience_proven else 1


def cmd_idempotent_consumer(target_file: str) -> int:
    from aleph_core.verification import IdempotentConsumerDeduplicationProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = IdempotentConsumerDeduplicationProver.audit_consumer_code(code_src)
    print(json.dumps({
        "formal_idempotence_proven": rep.formal_idempotence_proven,
        "deduplication_guaranteed": rep.deduplication_guaranteed,
        "atomic_commit_guaranteed": rep.atomic_commit_guaranteed,
        "side_effects_guarded": rep.side_effects_guarded,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_idempotence_proven else 1


def cmd_ssrf_audit(target_file: str) -> int:
    from aleph_core.verification import SSRFSafeEgressGatewayProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = SSRFSafeEgressGatewayProver.audit_egress_code(code_src)
    print(json.dumps({
        "formal_egress_safety_proven": rep.formal_egress_safety_proven,
        "private_ip_blocked": rep.private_ip_blocked,
        "anti_dns_rebinding_proven": rep.anti_dns_rebinding_proven,
        "dangerous_schemes_blocked": rep.dangerous_schemes_blocked,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_egress_safety_proven else 1


def cmd_crypto_timing(target_file: str) -> int:
    from aleph_core.verification import ConstantTimeCryptoProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = ConstantTimeCryptoProver.audit_constant_time(code_src)
    print(json.dumps({
        "constant_time_safe": rep.constant_time_safe,
        "analyzed_comparisons_count": rep.analyzed_comparisons_count,
        "safe_comparisons_count": rep.safe_comparisons_count,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.constant_time_safe else 1


def cmd_rate_limiter(target_file: str) -> int:
    from aleph_core.verification import RateLimiterTokenBucketProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = RateLimiterTokenBucketProver.audit_rate_limiter(code_src)
    print(json.dumps({
        "formal_rate_limit_proven": rep.formal_rate_limit_proven,
        "atomicity_guaranteed": rep.atomicity_guaranteed,
        "boundary_burst_safe": rep.boundary_burst_safe,
        "monotonic_clock_safe": rep.monotonic_clock_safe,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_rate_limit_proven else 1


def cmd_align_prompt_cache(prefix_file: str, chunk_size: int = 1024) -> int:
    from aleph_core.verification import PromptCacheBoundaryAligner
    src = Path(prefix_file).read_text(encoding="utf-8")
    rep = PromptCacheBoundaryAligner.align_prompt(src, chunk_size_tokens=chunk_size)
    print(json.dumps({
        "cache_aligned": rep.cache_aligned,
        "chunk_size_tokens": rep.chunk_size_tokens,
        "padding_tokens_added": rep.padding_tokens_added,
        "estimated_cache_hit_rate_pct": rep.estimated_cache_hit_rate_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_workspace_rollback(tx_id: str, before_dir: str, after_dir: str) -> int:
    from aleph_core.verification import TransactionalWorkspaceRollbackProver
    # Compara directorios y genera recibo inverso
    b_files = {str(p.name): p.read_text(encoding="utf-8") for p in Path(before_dir).glob("*") if p.is_file()}
    a_files = {str(p.name): p.read_text(encoding="utf-8") for p in Path(after_dir).glob("*") if p.is_file()}
    rep = TransactionalWorkspaceRollbackProver.verify_and_generate_rollback(tx_id, b_files, a_files)
    print(json.dumps({
        "rollback_proven": rep.rollback_proven,
        "modified_files_count": rep.modified_files_count,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.rollback_proven else 1


def cmd_queue_backpressure(target_file: str) -> int:
    from aleph_core.verification import QueueBackpressureAndOOMProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = QueueBackpressureAndOOMProver.audit_queue_code(code_src)
    print(json.dumps({
        "formal_backpressure_proven": rep.formal_backpressure_proven,
        "queues_bounded": rep.queues_bounded,
        "backpressure_handled": rep.backpressure_handled,
        "graceful_drain_guaranteed": rep.graceful_drain_guaranteed,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_backpressure_proven else 1


def cmd_csp_audit(target_file: str) -> int:
    from aleph_core.verification import ContentSecurityPolicyProver
    code_src = Path(target_file).read_text(encoding="utf-8")
    rep = ContentSecurityPolicyProver.audit_frontend_security(code_src)
    print(json.dumps({
        "formal_csp_safety_proven": rep.formal_csp_safety_proven,
        "html_sinks_sanitized": rep.html_sinks_sanitized,
        "strict_csp_declared": rep.strict_csp_declared,
        "unsafe_inline_guarded": rep.unsafe_inline_guarded,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_csp_safety_proven else 1


def cmd_multitenant_rls(sql_file: str) -> int:
    from aleph_core.verification import MultiTenantRLSLeakAndMaskingProver
    code_src = Path(sql_file).read_text(encoding="utf-8")
    rep = MultiTenantRLSLeakAndMaskingProver.audit_multitenant_sql(code_src)
    print(json.dumps({
        "multi_tenant_isolation_proven": rep.multi_tenant_isolation_proven,
        "sensitive_columns_masked": rep.sensitive_columns_masked,
        "joins_guarded_count": rep.joins_guarded_count,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.multi_tenant_isolation_proven else 1


def cmd_hmr_patch(orig_file: str, cand_file: str) -> int:
    from aleph_core.verification import ZeroFlickerHMRPatchEngine
    orig_src = Path(orig_file).read_text(encoding="utf-8")
    cand_src = Path(cand_file).read_text(encoding="utf-8")
    rep = ZeroFlickerHMRPatchEngine.synthesize_patch(orig_src, cand_src)
    print(json.dumps({
        "zero_flicker_safe": rep.zero_flicker_safe,
        "state_preserved": rep.state_preserved,
        "modified_nodes": rep.modified_jsx_nodes_count,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.zero_flicker_safe else 1


def cmd_merkle_repomap(target_dir: str = ".", budget: int = 1024) -> int:
    from aleph_core.verification import IncrementalMerkleASTPageRankAndPolyglotBoundaryProver
    root = Path(target_dir)
    files_map = {}
    for ext in ("*.py", "*.rs", "*.ts", "*.tsx", "*.sql", "*.bas", "*.vba"):
        for f in root.rglob(ext):
            if ".venv" in f.parts or "__pycache__" in f.parts:
                continue
            try:
                files_map[str(f.relative_to(root))] = f.read_text(encoding="utf-8")
            except Exception:
                pass
    rep = IncrementalMerkleASTPageRankAndPolyglotBoundaryProver.analyze_and_prove_repo(
        files_map=files_map,
        max_token_budget=budget
    )
    print(json.dumps({
        "formal_boundary_soundness_proven": rep.formal_boundary_soundness_proven,
        "merkle_root_sha256": rep.merkle_root_sha256,
        "total_files_indexed": rep.total_files_indexed,
        "dirty_files_recomputed": rep.dirty_files_recomputed,
        "cached_files_reused": rep.cached_files_reused,
        "total_symbols_ranked": rep.total_symbols_ranked,
        "cross_language_edges_count": rep.cross_language_edges_count,
        "violations_count": len(rep.cross_boundary_violations),
        "tokens_used": rep.tokens_used,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_boundary_soundness_proven else 1


def cmd_design_tokens(tsx_file: str) -> int:
    from aleph_core.verification import DesignTokenAndWCAGContrastProver
    tsx_src = Path(tsx_file).read_text(encoding="utf-8")
    rep = DesignTokenAndWCAGContrastProver.audit_and_repair_design_system(tsx_src)
    print(json.dumps({
        "formal_design_system_proven": rep.formal_design_system_proven,
        "wcag_contrast_aa_proven": rep.wcag_contrast_aa_proven,
        "wcag_target_size_proven": rep.wcag_target_size_proven,
        "wcag_focus_visible_proven": rep.wcag_focus_visible_proven,
        "min_contrast": rep.min_measured_contrast_ratio,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_design_system_proven else 1


def cmd_rsc_boundary(tsx_file: str) -> int:
    from aleph_core.verification import RSCBoundaryAndStudioGraphProver
    tsx_src = Path(tsx_file).read_text(encoding="utf-8")
    rep = RSCBoundaryAndStudioGraphProver.verify_rsc_and_build_studio_graph(tsx_src)
    print(json.dumps({
        "formal_rsc_boundary_proven": rep.formal_rsc_boundary_proven,
        "use_client_directive_sound": rep.use_client_directive_sound,
        "zero_server_secret_leak_in_client": rep.zero_server_secret_leak_in_client,
        "async_component_placement_sound": rep.async_component_placement_sound,
        "bound_nodes_count": rep.interactive_studio_delta_graph["bound_nodes_count"],
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_rsc_boundary_proven else 1


def cmd_deep_rls(sql_file: str) -> int:
    from aleph_core.verification import SupabaseDeepRLSAndSecurityDefinerProver
    sql_src = Path(sql_file).read_text(encoding="utf-8")
    rep = SupabaseDeepRLSAndSecurityDefinerProver.audit_deep_rls(sql_src)
    print(json.dumps({
        "deep_rls_zero_trust_proven": rep.deep_rls_zero_trust_proven,
        "force_rls_enforced": rep.force_rls_enforced,
        "with_check_completeness_proven": rep.with_check_completeness_proven,
        "views_security_invoker_proven": rep.views_security_invoker_proven,
        "security_definer_confined": rep.security_definer_confined,
        "violations_count": len(rep.violations),
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.deep_rls_zero_trust_proven else 1


def cmd_expand_contract(sql_file: str) -> int:
    from aleph_core.verification import ExpandContractZeroDowntimeMigrationProverAndSynthesizer
    sql_src = Path(sql_file).read_text(encoding="utf-8")
    rep = ExpandContractZeroDowntimeMigrationProverAndSynthesizer.audit_and_synthesize_migration(sql_src)
    print(json.dumps({
        "zero_downtime_pipeline_proven": rep.zero_downtime_pipeline_proven,
        "lock_timeout_guarded": rep.lock_timeout_guarded,
        "statement_timeout_guarded": rep.statement_timeout_guarded,
        "backfill_batched_safe": rep.backfill_batched_safe,
        "concurrent_tx_safe": rep.concurrent_tx_safe,
        "violations_count": len(rep.violations),
        "synthesized_4phase_plan": rep.synthesized_4phase_plan,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.zero_downtime_pipeline_proven else 1


def cmd_redteam_audit(file_path: str) -> int:
    from aleph_core.verification import RedTeamOffensiveTaintCryptoAndAntiSSRFProver
    p = Path(file_path)
    if not p.exists():
        print(f"Error: No existe {file_path}")
        return 1
    rep = RedTeamOffensiveTaintCryptoAndAntiSSRFProver.audit_redteam_security(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "secure": rep.secure,
        "ssrf_canonical_isolation_proven": rep.ssrf_canonical_isolation_proven,
        "crypto_constant_time_and_aead_proven": rep.crypto_constant_time_and_aead_proven,
        "ifds_cross_tool_taint_free_proven": rep.ifds_cross_tool_taint_free_proven,
        "mcp_manifest_poison_free_proven": rep.mcp_manifest_poison_free_proven,
        "canonicalized_ips_inspected": rep.canonicalized_ips_inspected,
        "violations_detected": rep.violations_detected,
        "analysis_duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.secure else 1


def cmd_react_lifecycle(tsx_file: str) -> int:
    from aleph_core.verification import ReactLifecycleMemoryLeakAndAsyncRaceConditionProver
    tsx_src = Path(tsx_file).read_text(encoding="utf-8")
    rep = ReactLifecycleMemoryLeakAndAsyncRaceConditionProver.audit_react_lifecycle(tsx_src)
    print(json.dumps({
        "secure": rep.secure,
        "component_name": rep.component_name,
        "uncleaned_event_listeners": rep.uncleaned_event_listeners,
        "uncleaned_timers": rep.uncleaned_timers,
        "async_race_conditions": rep.async_race_conditions,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.secure else 1


def cmd_impact_cone(target_dir: str = ".", focus_sym: str = "main", budget: int = 1024) -> int:
    from aleph_core.verification import BidirectionalImpactConePageRankAndPolyglotMatrixProver
    root = Path(target_dir)
    files_map = {}
    for ext in ("*.py", "*.rs", "*.ts", "*.tsx", "*.sql", "*.bas", "*.vba"):
        for f in root.rglob(ext):
            if ".venv" in f.parts or "__pycache__" in f.parts:
                continue
            try:
                files_map[str(f.relative_to(root))] = f.read_text(encoding="utf-8")
            except Exception:
                pass
    rep = BidirectionalImpactConePageRankAndPolyglotMatrixProver.analyze_impact_cone_and_prove_matrix(
        files_map=files_map,
        focus_symbols=[focus_sym],
        max_token_budget=budget
    )
    print(json.dumps({
        "formal_impact_soundness_proven": rep.formal_impact_soundness_proven,
        "merkle_dag_root_sha256": rep.merkle_dag_root_sha256,
        "total_files_scanned": rep.total_files_scanned,
        "upstream_callers_count": rep.upstream_callers_count,
        "downstream_callees_count": rep.downstream_callees_count,
        "pruned_symbols_in_cone": rep.pruned_symbols_in_cone,
        "violations_count": len(rep.matrix_drift_violations),
        "tokens_used": rep.tokens_used,
        "token_efficiency_ratio": rep.token_efficiency_ratio,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_impact_soundness_proven else 1


def cmd_polyglot_bridge(rust_f: str, ts_f: str, sql_f: str = "") -> int:
    from aleph_core.verification import PolyglotContractBridgeAndIncrementalPersonalizedPageRankProver
    r_code = Path(rust_f).read_text(encoding="utf-8") if Path(rust_f).exists() else rust_f
    t_code = Path(ts_f).read_text(encoding="utf-8") if Path(ts_f).exists() else ts_f
    s_code = Path(sql_f).read_text(encoding="utf-8") if (sql_f and Path(sql_f).exists()) else sql_f
    rep = PolyglotContractBridgeAndIncrementalPersonalizedPageRankProver().verify_and_synthesize(r_code, t_code, s_code)
    print(json.dumps({"is_congruent": rep.is_congruent, "token_savings_pct": rep.token_savings_pct, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.is_congruent else 1


def cmd_simhash_kv(src_f: str, mod_fn: str = "") -> int:
    from aleph_core.verification import SimHashASTCloneDetectorAndHeavyHitterKVCacheProver
    s_code = Path(src_f).read_text(encoding="utf-8") if Path(src_f).exists() else src_f
    rep = SimHashASTCloneDetectorAndHeavyHitterKVCacheProver().verify_and_audit(s_code, [mod_fn] if mod_fn else None)
    print(json.dumps({"proven_clone_sync_safe": rep.proven_clone_sync_safe, "kv_cache_compression_ratio_pct": rep.kv_cache_compression_ratio_pct, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.proven_clone_sync_safe else 1


def cmd_tarjan_pyo3(rust_f: str) -> int:
    from aleph_core.verification import TarjanSCCCondensationPyO3GILDeadlockAndSpeculativeEditProver
    r_code = Path(rust_f).read_text(encoding="utf-8") if Path(rust_f).exists() else rust_f
    rep = TarjanSCCCondensationPyO3GILDeadlockAndSpeculativeEditProver().verify_and_synthesize(r_code)
    print(json.dumps({"is_acyclic_and_ffi_safe": rep.is_acyclic_and_ffi_safe, "speculative_edit_speedup_factor": rep.speculative_edit_speedup_factor, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.is_acyclic_and_ffi_safe else 1


def cmd_dominator_wasm(ts_f: str) -> int:
    from aleph_core.verification import DominatorTreeBlastRadiusRadixKVAndWasmMemoryProver
    t_code = Path(ts_f).read_text(encoding="utf-8") if Path(ts_f).exists() else ts_f
    rep = DominatorTreeBlastRadiusRadixKVAndWasmMemoryProver().verify_and_synthesize(t_code)
    print(json.dumps({"is_wasm_and_blast_radius_safe": rep.is_wasm_and_blast_radius_safe, "radix_cache_hit_ratio_pct": rep.radix_cache_hit_ratio_pct, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.is_wasm_and_blast_radius_safe else 1


def cmd_rowan_cst(rust_f: str) -> int:
    from aleph_core.verification import RowanGreenRedCSTFalseSharingAndAttentionSinkProver
    r_code = Path(rust_f).read_text(encoding="utf-8") if Path(rust_f).exists() else rust_f
    rep = RowanGreenRedCSTFalseSharingAndAttentionSinkProver().verify_and_synthesize(r_code)
    print(json.dumps({"is_cache_aligned_and_sink_safe": rep.is_cache_aligned_and_sink_safe, "green_tree_sharing_ratio_pct": rep.green_tree_sharing_ratio_pct, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.is_cache_aligned_and_sink_safe else 1


def cmd_pld_arena(rust_f: str) -> int:
    from aleph_core.verification import PromptLookupNGramSpeculatorAndBumpArenaDropSoundnessProver
    r_code = Path(rust_f).read_text(encoding="utf-8") if Path(rust_f).exists() else rust_f
    rep = PromptLookupNGramSpeculatorAndBumpArenaDropSoundnessProver().verify_and_synthesize(r_code)
    print(json.dumps({"is_arena_sound_and_pld_optimal": rep.is_arena_sound_and_pld_optimal, "pld_effective_speedup_x": rep.pld_effective_speedup_x, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.is_arena_sound_and_pld_optimal else 1


def cmd_salsa_rkyv(rust_f: str) -> int:
    from aleph_core.verification import SalsaEarlyCutoffRkyvAlignmentAndChunkedPrefillProver
    r_code = Path(rust_f).read_text(encoding="utf-8") if Path(rust_f).exists() else rust_f
    rep = SalsaEarlyCutoffRkyvAlignmentAndChunkedPrefillProver().verify_and_synthesize(r_code)
    print(json.dumps({"is_rkyv_safe_and_stall_free": rep.is_rkyv_safe_and_stall_free, "pruned_downstream_queries_pct": rep.pruned_downstream_queries_pct, "duration_ms": rep.analysis_duration_ms}, indent=2, ensure_ascii=False))
    return 0 if rep.is_rkyv_safe_and_stall_free else 1


def cmd_roaring_iouring(rust_file: str) -> int:
    from aleph_core.verification import RoaringBitmapReachabilityIoUringBarrierAndSnapKVPooledCacheProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = RoaringBitmapReachabilityIoUringBarrierAndSnapKVPooledCacheProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_iouring_barrier_and_cache_sound": rep.is_iouring_barrier_and_cache_sound,
        "total_nodes": rep.total_nodes,
        "transitive_reachability_pairs": rep.transitive_reachability_pairs,
        "bitwise_speedup_factor": rep.bitwise_speedup_factor,
        "iouring_findings_count": len(rep.iouring_barrier_findings),
        "snapkv_compression_ratio_pct": rep.snapkv_compression_ratio_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_iouring_barrier_and_cache_sound else 1


def cmd_egraph_pyramidkv(rust_file: str) -> int:
    from aleph_core.verification import EGraphEqualitySaturationPinProjectionAndPyramidKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = EGraphEqualitySaturationPinProjectionAndPyramidKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_pin_sound_and_egraph_optimal": rep.is_pin_sound_and_egraph_optimal,
        "eclasses_count": rep.eclasses_count,
        "synthesized_optimal_expr": rep.synthesized_optimal_expr,
        "cost_reduction_pct": rep.cost_reduction_pct,
        "pin_findings_count": len(rep.pin_projection_findings),
        "pyramidkv_compression_ratio_pct": rep.pyramidkv_compression_ratio_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_pin_sound_and_egraph_optimal else 1


def cmd_hub_epoch_quest(rust_file: str) -> int:
    from aleph_core.verification import PrunedLandmarkHubLabelingEpochReclamationAndQuestKVCacheProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = PrunedLandmarkHubLabelingEpochReclamationAndQuestKVCacheProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_epoch_reclamation_and_quest_sound": rep.is_epoch_reclamation_and_quest_sound,
        "total_nodes": rep.total_nodes,
        "o1_hub_intersection_queries_verified": rep.o1_hub_intersection_queries_verified,
        "epoch_findings_count": len(rep.epoch_reclamation_findings),
        "quest_query_aware_sparsity_pct": rep.quest_query_aware_sparsity_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_epoch_reclamation_and_quest_sound else 1


def cmd_stackgraph_simd_duo(rust_file: str) -> int:
    from aleph_core.verification import StackGraphNameResolutionSIMDVectorizationAndDuoAttentionProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = StackGraphNameResolutionSIMDVectorizationAndDuoAttentionProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_simd_and_stack_graph_sound": rep.is_simd_and_stack_graph_sound,
        "stitched_cross_file_paths": rep.stitched_cross_file_paths,
        "simd_findings_count": len(rep.simd_vectorization_findings),
        "duo_attention_memory_reduction_pct": rep.duo_attention_memory_reduction_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_simd_and_stack_graph_sound else 1


def cmd_fmindex_uninit_kivi(rust_file: str) -> int:
    from aleph_core.verification import WaveletMatrixFMIndexMaybeUninitAndKIVIQuantizedCacheProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = WaveletMatrixFMIndexMaybeUninitAndKIVIQuantizedCacheProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_maybe_uninit_and_kivi_sound": rep.is_maybe_uninit_and_kivi_sound,
        "matched_occurrences_count": rep.matched_occurrences_count,
        "sublinear_speedup_factor": rep.sublinear_speedup_factor,
        "maybe_uninit_findings_count": len(rep.maybe_uninit_findings),
        "kivi_memory_compression_pct": rep.kivi_memory_compression_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_maybe_uninit_and_kivi_sound else 1


def cmd_ett_treeborrows_minf(rust_file: str) -> int:
    from aleph_core.verification import DynamicEulerTourConnectivityTreeBorrowsAndMInferenceProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = DynamicEulerTourConnectivityTreeBorrowsAndMInferenceProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_tree_borrows_and_minference_sound": rep.is_tree_borrows_and_minference_sound,
        "euler_tour_forest_components": rep.euler_tour_forest_components,
        "replacement_edges_found_in_hlt": rep.replacement_edges_found_in_hlt,
        "tree_borrows_findings_count": len(rep.tree_borrows_findings),
        "minference_prefill_flops_reduction_pct": rep.minference_prefill_flops_reduction_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_tree_borrows_and_minference_sound else 1


def cmd_ddlog_sendsync_yoco(rust_file: str) -> int:
    from aleph_core.verification import DifferentialDatalogZSetSendSyncAndCrossLayerKVCacheProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = DifferentialDatalogZSetSendSyncAndCrossLayerKVCacheProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_send_sync_and_yoco_sound": rep.is_send_sync_and_yoco_sound,
        "incremental_zset_derived_facts": rep.incremental_zset_derived_facts,
        "ddlog_incremental_speedup_factor": rep.ddlog_incremental_speedup_factor,
        "send_sync_findings_count": len(rep.send_sync_findings),
        "yoco_cross_layer_kv_savings_pct": rep.yoco_cross_layer_kv_savings_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_send_sync_and_yoco_sound else 1


def cmd_ahocorasick_ffi_mla(rust_file: str) -> int:
    from aleph_core.verification import AhoCorasickAutomatonFFIUnwindAndMultiHeadLatentAttentionProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = AhoCorasickAutomatonFFIUnwindAndMultiHeadLatentAttentionProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_ffi_unwind_and_mla_sound": rep.is_ffi_unwind_and_mla_sound,
        "multi_pattern_matches_count": rep.multi_pattern_matches_count,
        "single_pass_speedup_factor": rep.single_pass_speedup_factor,
        "ffi_findings_count": len(rep.ffi_unwind_findings),
        "mla_kv_compression_ratio_pct": rep.mla_kv_compression_ratio_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_ffi_unwind_and_mla_sound else 1


def cmd_lct_transmute_infllm(rust_file: str) -> int:
    from aleph_core.verification import SleatorTarjanLinkCutTreeTransmuteNicheAndInfLLMBlockMemoryProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = SleatorTarjanLinkCutTreeTransmuteNicheAndInfLLMBlockMemoryProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_transmute_niche_and_infllm_sound": rep.is_transmute_niche_and_infllm_sound,
        "lct_link_cut_ops_executed": rep.lct_link_cut_ops_executed,
        "lct_logarithmic_speedup_factor": rep.lct_logarithmic_speedup_factor,
        "transmute_findings_count": len(rep.transmute_niche_findings),
        "infllm_memory_savings_pct": rep.infllm_memory_savings_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_transmute_niche_and_infllm_sound else 1


def cmd_fwdpush_staticmut_loki(rust_file: str) -> int:
    from aleph_core.verification import ForwardPushLocalPageRankStaticMutAndLokiEigenKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = ForwardPushLocalPageRankStaticMutAndLokiEigenKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_static_mut_and_loki_sound": rep.is_static_mut_and_loki_sound,
        "active_pushed_nodes": rep.active_pushed_nodes,
        "sublinear_push_speedup_factor": rep.sublinear_push_speedup_factor,
        "static_mut_findings_count": len(rep.static_mut_findings),
        "loki_attention_compute_savings_pct": rep.loki_attention_compute_savings_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_static_mut_and_loki_sound else 1


def cmd_fora_strictprov_chunkkv(rust_file: str) -> int:
    from aleph_core.verification import FORABidirectionalPPRStrictProvenanceAndChunkKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = FORABidirectionalPPRStrictProvenanceAndChunkKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_strict_provenance_and_chunkkv_sound": rep.is_strict_provenance_and_chunkkv_sound,
        "fora_forward_push_nodes": rep.fora_forward_push_nodes,
        "fora_random_walks_sampled": rep.fora_random_walks_sampled,
        "fora_hybrid_speedup_factor": rep.fora_hybrid_speedup_factor,
        "strict_provenance_findings_count": len(rep.strict_provenance_findings),
        "chunkkv_compression_ratio_pct": rep.chunkkv_compression_ratio_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_strict_provenance_and_chunkkv_sound else 1


def cmd_resacc_unsafecell_minicache(rust_file: str) -> int:
    from aleph_core.verification import ResAccResidueAccumulationPPRUnsafeCellAndMiniCacheSLERPProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = ResAccResidueAccumulationPPRUnsafeCellAndMiniCacheSLERPProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_unsafecell_and_minicache_sound": rep.is_unsafecell_and_minicache_sound,
        "resacc_accumulated_hub_nodes": rep.resacc_accumulated_hub_nodes,
        "resacc_push_reduction_factor": rep.resacc_push_reduction_factor,
        "unsafecell_findings_count": len(rep.unsafecell_noalias_findings),
        "minicache_depth_compression_pct": rep.minicache_depth_compression_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_unsafecell_and_minicache_sound else 1


def cmd_chebppr_slice_razor(rust_file: str) -> int:
    from aleph_core.verification import ChebyshevPolynomialPPRSliceRawPartsAndRazorAttentionProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = ChebyshevPolynomialPPRSliceRawPartsAndRazorAttentionProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_slice_raw_parts_and_razor_sound": rep.is_slice_raw_parts_and_razor_sound,
        "chebppr_sqrt_alpha_speedup_factor": rep.chebppr_sqrt_alpha_speedup_factor,
        "slice_raw_parts_findings_count": len(rep.slice_raw_parts_findings),
        "razor_kv_cache_compression_pct": rep.razor_kv_cache_compression_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_slice_raw_parts_and_razor_sound else 1


def cmd_effres_unaligned_adakv(rust_file: str) -> int:
    from aleph_core.verification import EffectiveResistanceSpectralSparsifierUnalignedPtrAndAdaKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = EffectiveResistanceSpectralSparsifierUnalignedPtrAndAdaKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_unaligned_and_adakv_sound": rep.is_unaligned_and_adakv_sound,
        "edge_sparsification_speedup_factor": rep.edge_sparsification_speedup_factor,
        "unaligned_packed_findings_count": len(rep.unaligned_packed_findings),
        "adakv_kv_cache_compression_pct": rep.adakv_kv_cache_compression_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_unaligned_and_adakv_sound else 1


def cmd_blockrank_zst_cla(rust_file: str) -> int:
    from aleph_core.verification import BlockRankHierarchicalPPRZSTAllocAndCrossLayerAttentionProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = BlockRankHierarchicalPPRZSTAllocAndCrossLayerAttentionProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_zst_alloc_and_cla_sound": rep.is_zst_alloc_and_cla_sound,
        "blockrank_hierarchical_speedup_factor": rep.blockrank_hierarchical_speedup_factor,
        "zst_alloc_findings_count": len(rep.zst_alloc_findings),
        "cla_kv_cache_reduction_pct": rep.cla_kv_cache_reduction_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_zst_alloc_and_cla_sound else 1


def cmd_quadext_dealloc_think(rust_file: str) -> int:
    from aleph_core.verification import QuadraticExtrapolationPPRDeallocLayoutAndThinKChannelProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = QuadraticExtrapolationPPRDeallocLayoutAndThinKChannelProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_dealloc_layout_and_think_sound": rep.is_dealloc_layout_and_think_sound,
        "quadratic_extrapolation_speedup_factor": rep.quadratic_extrapolation_speedup_factor,
        "dealloc_layout_findings_count": len(rep.dealloc_layout_findings),
        "think_channel_pruning_savings_pct": rep.think_channel_pruning_savings_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_dealloc_layout_and_think_sound else 1


def cmd_gauss_copy_gear(rust_file: str) -> int:
    from aleph_core.verification import GaussSeidelInPlacePPRCopyOverlapAndGEARKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = GaussSeidelInPlacePPRCopyOverlapAndGEARKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_copy_overlap_and_gear_sound": rep.is_copy_overlap_and_gear_sound,
        "gauss_seidel_in_place_speedup_factor": rep.gauss_seidel_in_place_speedup_factor,
        "copy_nonoverlapping_findings_count": len(rep.copy_nonoverlapping_findings),
        "gear_kv_compression_ratio_pct": rep.gear_kv_compression_ratio_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_copy_overlap_and_gear_sound else 1


def cmd_arnoldi_setlen_palu(rust_file: str) -> int:
    from aleph_core.verification import ArnoldiKrylovPPRVecSetLenAndPaluLowRankKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = ArnoldiKrylovPPRVecSetLenAndPaluLowRankKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_vec_set_len_and_palu_sound": rep.is_vec_set_len_and_palu_sound,
        "arnoldi_krylov_speedup_factor": rep.arnoldi_krylov_speedup_factor,
        "vec_set_len_findings_count": len(rep.vec_set_len_findings),
        "palu_kv_compression_ratio_pct": rep.palu_kv_compression_ratio_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_vec_set_len_and_palu_sound else 1


def cmd_anderson_utf8_kvquant(rust_file: str) -> int:
    from aleph_core.verification import AndersonAcceleratedPPRUtf8UncheckedAndKVQuantPreRoPEProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = AndersonAcceleratedPPRUtf8UncheckedAndKVQuantPreRoPEProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_utf8_unchecked_and_kvquant_sound": rep.is_utf8_unchecked_and_kvquant_sound,
        "anderson_mixing_speedup_factor": rep.anderson_mixing_speedup_factor,
        "utf8_unchecked_findings_count": len(rep.utf8_unchecked_findings),
        "kvquant_memory_savings_pct": rep.kvquant_memory_savings_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_utf8_unchecked_and_kvquant_sound else 1


def cmd_rre_fromraw_retrievalkv(rust_file: str) -> int:
    from aleph_core.verification import RREVectorExtrapolationPPRBoxFromRawAndRetrievalAttentionProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = RREVectorExtrapolationPPRBoxFromRawAndRetrievalAttentionProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_from_raw_and_retrieval_kv_sound": rep.is_from_raw_and_retrieval_kv_sound,
        "rre_extrapolation_speedup_factor": rep.rre_extrapolation_speedup_factor,
        "from_raw_ownership_findings_count": len(rep.from_raw_ownership_findings),
        "retrieval_attention_gpu_vram_savings_pct": rep.retrieval_attention_gpu_vram_savings_pct,
        "retrieval_attention_decoding_speedup": rep.retrieval_attention_decoding_speedup,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_from_raw_and_retrieval_kv_sound else 1


def cmd_innerouter_cstr_shadowkv(rust_file: str) -> int:
    from aleph_core.verification import InnerOuterPPRCStrFromPtrAndShadowKVCacheProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = InnerOuterPPRCStrFromPtrAndShadowKVCacheProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_cstr_and_shadowkv_sound": rep.is_cstr_and_shadowkv_sound,
        "inner_outer_speedup_factor": rep.inner_outer_speedup_factor,
        "cstr_ffi_findings_count": len(rep.cstr_ffi_findings),
        "shadowkv_gpu_memory_savings_pct": rep.shadowkv_gpu_memory_savings_pct,
        "shadowkv_batch_throughput_multiplier": rep.shadowkv_batch_throughput_multiplier,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_cstr_and_shadowkv_sound else 1


def cmd_adaptive_mandrop_gemfilter(rust_file: str) -> int:
    from aleph_core.verification import AdaptivePageRankManuallyDropAndGemFilterKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = AdaptivePageRankManuallyDropAndGemFilterKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_manually_drop_and_gemfilter_sound": rep.is_manually_drop_and_gemfilter_sound,
        "adaptive_ppr_speedup_factor": rep.adaptive_ppr_speedup_factor,
        "adaptive_locked_nodes_pct": rep.adaptive_locked_nodes_pct,
        "manually_drop_findings_count": len(rep.manually_drop_findings),
        "gemfilter_kv_memory_savings_pct": rep.gemfilter_kv_memory_savings_pct,
        "gemfilter_prefill_speedup_factor": rep.gemfilter_prefill_speedup_factor,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_manually_drop_and_gemfilter_sound else 1


def cmd_aitken_nonnull_fastgen(rust_file: str) -> int:
    from aleph_core.verification import AitkenDeltaSquaredPPRNonNullUncheckedAndFastGenKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = AitkenDeltaSquaredPPRNonNullUncheckedAndFastGenKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_nonnull_and_fastgen_sound": rep.is_nonnull_and_fastgen_sound,
        "aitken_speedup_factor": rep.aitken_speedup_factor,
        "nonnull_niche_findings_count": len(rep.nonnull_niche_findings),
        "fastgen_kv_memory_savings_pct": rep.fastgen_kv_memory_savings_pct,
        "fastgen_decoding_speedup_factor": rep.fastgen_decoding_speedup_factor,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_nonnull_and_fastgen_sound else 1


def cmd_lumping_getunchecked_squeeze(rust_file: str) -> int:
    from aleph_core.verification import LumpingPageRankGetUncheckedAndSqueezeAttentionProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = LumpingPageRankGetUncheckedAndSqueezeAttentionProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_get_unchecked_and_squeeze_kv_sound": rep.is_get_unchecked_and_squeeze_kv_sound,
        "lumping_ppr_speedup_factor": rep.lumping_ppr_speedup_factor,
        "reduced_active_core_nodes": rep.reduced_active_core_nodes,
        "get_unchecked_bounds_findings_count": len(rep.get_unchecked_bounds_findings),
        "squeeze_attention_kv_savings_pct": rep.squeeze_attention_kv_savings_pct,
        "squeeze_attention_throughput_multiplier": rep.squeeze_attention_throughput_multiplier,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_get_unchecked_and_squeeze_kv_sound else 1


def cmd_blocktri_packed_cake(rust_file: str) -> int:
    from aleph_core.verification import BlockTriangularSCCPPRPackedAddrOfAndCAKEProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = BlockTriangularSCCPPRPackedAddrOfAndCAKEProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_packed_addr_of_and_cake_kv_sound": rep.is_packed_addr_of_and_cake_kv_sound,
        "block_triangular_ppr_speedup_factor": rep.block_triangular_ppr_speedup_factor,
        "acyclic_dag_scc_nodes": rep.acyclic_dag_scc_nodes,
        "packed_unaligned_ref_findings_count": len(rep.packed_unaligned_ref_findings),
        "cake_kv_memory_savings_pct": rep.cake_kv_memory_savings_pct,
        "cake_prefill_peak_memory_reduction_pct": rep.cake_prefill_peak_memory_reduction_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_packed_addr_of_and_cake_kv_sound else 1


def cmd_bicgstab_writebytes_kvcompress(rust_file: str) -> int:
    from aleph_core.verification import BiCGSTABPPRWriteBytesAndKVCompressProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = BiCGSTABPPRWriteBytesAndKVCompressProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_write_bytes_and_kvcompress_sound": rep.is_write_bytes_and_kvcompress_sound,
        "bicgstab_speedup_factor": rep.bicgstab_speedup_factor,
        "bicgstab_iterations_executed": rep.bicgstab_iterations_executed,
        "write_bytes_bitpattern_findings_count": len(rep.write_bytes_bitpattern_findings),
        "kvcompress_memory_savings_pct": rep.kvcompress_memory_savings_pct,
        "kvcompress_throughput_multiplier": rep.kvcompress_throughput_multiplier,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_write_bytes_and_kvcompress_sound else 1


def cmd_acl_swap_qfilters(rust_file: str) -> int:
    from aleph_core.verification import AndersenChungLangConductancePPRSwapNonOverlappingAndQFiltersProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = AndersenChungLangConductancePPRSwapNonOverlappingAndQFiltersProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_swap_nonoverlapping_and_qfilters_sound": rep.is_swap_nonoverlapping_and_qfilters_sound,
        "acl_local_speedup_factor": rep.acl_local_speedup_factor,
        "acl_sweep_cut_conductance": rep.acl_sweep_cut_conductance,
        "swap_nonoverlapping_findings_count": len(rep.swap_nonoverlapping_findings),
        "qfilters_kv_memory_savings_pct": rep.qfilters_kv_memory_savings_pct,
        "qfilters_cone_projection_retention_pct": rep.qfilters_cone_projection_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_swap_nonoverlapping_and_qfilters_sound else 1


def cmd_speedppr_slicemut_l2norm(rust_file: str) -> int:
    from aleph_core.verification import SpeedPPRPowerPushSliceRawMutAndL2NormKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = SpeedPPRPowerPushSliceRawMutAndL2NormKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_slice_raw_mut_and_l2norm_kv_sound": rep.is_slice_raw_mut_and_l2norm_kv_sound,
        "speedppr_speedup_factor": rep.speedppr_speedup_factor,
        "speedppr_l1_residual": rep.speedppr_l1_residual,
        "slice_from_raw_parts_mut_findings_count": len(rep.slice_from_raw_parts_mut_findings),
        "l2norm_kv_memory_savings_pct": rep.l2norm_kv_memory_savings_pct,
        "l2norm_kv_attention_retention_pct": rep.l2norm_kv_attention_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_slice_raw_mut_and_l2norm_kv_sound else 1


def cmd_fista_volatile_tova(rust_file: str) -> int:
    from aleph_core.verification import FISTAVariationalPPRVolatilePtrAndTOVAKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = FISTAVariationalPPRVolatilePtrAndTOVAKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_volatile_ptr_and_tova_kv_sound": rep.is_volatile_ptr_and_tova_kv_sound,
        "fista_speedup_factor": rep.fista_speedup_factor,
        "fista_variational_objective_gap": rep.fista_variational_objective_gap,
        "volatile_ptr_concurrency_findings_count": len(rep.volatile_ptr_concurrency_findings),
        "tova_kv_memory_savings_pct": rep.tova_kv_memory_savings_pct,
        "tova_long_context_retention_pct": rep.tova_long_context_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_volatile_ptr_and_tova_kv_sound else 1


def cmd_rbs_drop_scissorhands(rust_file: str) -> int:
    from aleph_core.verification import RBSDegreeStratifiedPPRDropInPlaceAndScissorhandsKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = RBSDegreeStratifiedPPRDropInPlaceAndScissorhandsKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_drop_in_place_and_scissorhands_sound": rep.is_drop_in_place_and_scissorhands_sound,
        "rbs_speedup_factor": rep.rbs_speedup_factor,
        "rbs_edges_scanned_ratio": rep.rbs_edges_scanned_ratio,
        "drop_in_place_findings_count": len(rep.drop_in_place_findings),
        "scissorhands_kv_memory_savings_pct": rep.scissorhands_kv_memory_savings_pct,
        "scissorhands_importance_retention_pct": rep.scissorhands_importance_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_drop_in_place_and_scissorhands_sound else 1


def cmd_topppr_replace_keyformer(rust_file: str) -> int:
    from aleph_core.verification import TopPPRPrecisionBoundsPtrReplaceAndKeyformerKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = TopPPRPrecisionBoundsPtrReplaceAndKeyformerKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_ptr_replace_and_keyformer_sound": rep.is_ptr_replace_and_keyformer_sound,
        "topppr_speedup_factor": rep.topppr_speedup_factor,
        "topppr_bound_gap_margin": rep.topppr_bound_gap_margin,
        "ptr_replace_findings_count": len(rep.ptr_replace_findings),
        "keyformer_kv_memory_savings_pct": rep.keyformer_kv_memory_savings_pct,
        "keyformer_gumbel_accuracy_retention_pct": rep.keyformer_gumbel_accuracy_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_ptr_replace_and_keyformer_sound else 1


def cmd_hkpr_ptrread_scissorhands20x(rust_file: str) -> int:
    from aleph_core.verification import HeatKernelPPRPtrReadNonCopyAndQuantScissorhands20xProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = HeatKernelPPRPtrReadNonCopyAndQuantScissorhands20xProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_ptr_read_and_quant_scissorhands_sound": rep.is_ptr_read_and_quant_scissorhands_sound,
        "hkpr_speedup_factor": rep.hkpr_speedup_factor,
        "hkpr_cluster_conductance": rep.hkpr_cluster_conductance,
        "ptr_read_noncopy_findings_count": len(rep.ptr_read_noncopy_findings),
        "quant_scissorhands_compression_factor": rep.quant_scissorhands_compression_factor,
        "quant_scissorhands_kv_savings_pct": rep.quant_scissorhands_kv_savings_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_ptr_read_and_quant_scissorhands_sound else 1


def cmd_bernnet_ptrwrite_aerosketch(rust_file: str) -> int:
    from aleph_core.verification import BernNetPolynomialPPRPtrWriteLeakAndAeroSketchKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = BernNetPolynomialPPRPtrWriteLeakAndAeroSketchKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_ptr_write_and_aerosketch_sound": rep.is_ptr_write_and_aerosketch_sound,
        "bernstein_speedup_factor": rep.bernstein_speedup_factor,
        "bernstein_runge_oscillation_error": rep.bernstein_runge_oscillation_error,
        "ptr_write_leak_findings_count": len(rep.ptr_write_leak_findings),
        "aerosketch_kv_memory_savings_pct": rep.aerosketch_kv_memory_savings_pct,
        "aerosketch_spectral_retention_pct": rep.aerosketch_spectral_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_ptr_write_and_aerosketch_sound else 1


def cmd_chebnetii_provenance_l2kv(rust_file: str) -> int:
    from aleph_core.verification import ChebNetIIInterpolationPPRWithoutProvenanceAndPersistentL2KVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = ChebNetIIInterpolationPPRWithoutProvenanceAndPersistentL2KVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_without_provenance_and_persistent_l2_sound": rep.is_without_provenance_and_persistent_l2_sound,
        "chebnetii_speedup_factor": rep.chebnetii_speedup_factor,
        "chebnetii_minimax_residual": rep.chebnetii_minimax_residual,
        "without_provenance_findings_count": len(rep.without_provenance_findings),
        "persistent_l2_kv_savings_pct": rep.persistent_l2_kv_savings_pct,
        "persistent_l2_passkey_retention_pct": rep.persistent_l2_passkey_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_without_provenance_and_persistent_l2_sound else 1


def cmd_sublinear_add_disjoint_tova(rust_file: str) -> int:
    from aleph_core.verification import SublinearADDPPRGetDisjointMutAndDyadicTOVAKVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = SublinearADDPPRGetDisjointMutAndDyadicTOVAKVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_get_disjoint_mut_and_dyadic_tova_sound": rep.is_get_disjoint_mut_and_dyadic_tova_sound,
        "sublinear_add_speedup_factor": rep.sublinear_add_speedup_factor,
        "sublinear_add_l_inf_residual": rep.sublinear_add_l_inf_residual,
        "get_disjoint_mut_findings_count": len(rep.get_disjoint_mut_findings),
        "dyadic_tova_kv_savings_pct": rep.dyadic_tova_kv_savings_pct,
        "dyadic_tova_retention_pct": rep.dyadic_tova_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_get_disjoint_mut_and_dyadic_tova_sound else 1


def cmd_dynelm_volatile_qfilterl2(rust_file: str) -> int:
    from aleph_core.verification import DynELMStructuralPPRVolatileSplittingAndQFilterL2KVProver
    p = Path(rust_file)
    rs_src = p.read_text(encoding="utf-8") if (len(rust_file) < 200 and "{" not in rust_file and p.exists()) else rust_file
    prover = DynELMStructuralPPRVolatileSplittingAndQFilterL2KVProver()
    rep = prover.verify_and_synthesize(rust_code=rs_src)
    print(json.dumps({
        "is_volatile_splitting_and_qfilter_l2_sound": rep.is_volatile_splitting_and_qfilter_l2_sound,
        "dynelm_speedup_factor": rep.dynelm_speedup_factor,
        "dynelm_log_squared_ops_per_update": rep.dynelm_log_squared_ops_per_update,
        "volatile_load_store_splitting_findings_count": len(rep.volatile_load_store_splitting_findings),
        "qfilter_l2_kv_savings_pct": rep.qfilter_l2_kv_savings_pct,
        "qfilter_l2_flash_retention_pct": rep.qfilter_l2_flash_retention_pct,
        "duration_ms": rep.analysis_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.is_volatile_splitting_and_qfilter_l2_sound else 1


def cmd_scim2_rfc7644_fedcm_aigateway_ssrf_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import SCIM2RFC7644FilterProvisioningPermissionsPolicyIdentityCredentialsGetAndKongEnvoyAIProxyHeaderSSRFProver
    prover = SCIM2RFC7644FilterProvisioningPermissionsPolicyIdentityCredentialsGetAndKongEnvoyAIProxyHeaderSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_scim2_rfc7644_permissions_fedcm_and_ai_gateway_ssrf_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_scim2_rfc7644_permissions_fedcm_and_ai_gateway_ssrf_safe else 1


def cmd_scim2_externalid_idor_fedcm_litellm_cve2026_59823_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import SCIM2ExternalIdCollisionKeycloakIDORFedCMConfigURLAndLiteLLMNestedUserConfigCVE202659823SSRFProver
    prover = SCIM2ExternalIdCollisionKeycloakIDORFedCMConfigURLAndLiteLLMNestedUserConfigCVE202659823SSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_scim2_externalid_idor_fedcm_configurl_and_litellm_nested_ssrf_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_scim2_externalid_idor_fedcm_configurl_and_litellm_nested_ssrf_safe else 1


def cmd_scim2_temporal_ac2_jwt_cve2024_54150_fedcm_litellm_testconn_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import SCIM2TemporalAC2ReconciliationJWTAlgConfusionCVE202454150FedCMMultiIdPAndLiteLLMTestConnectionExfilProver
    prover = SCIM2TemporalAC2ReconciliationJWTAlgConfusionCVE202454150FedCMMultiIdPAndLiteLLMTestConnectionExfilProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_scim2_temporal_ac2_jwt_fedcm_and_litellm_test_connection_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_scim2_temporal_ac2_jwt_fedcm_and_litellm_test_connection_safe else 1


def cmd_tls13_rfc9846_vllm_cve2026_24779_bentoml_cve2026_44345_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import TLS13RFC9846TACACSIoTServiceIdentityVLLMMediaConnectorCVE202624779AndBentoMLRunnerCVE202644345Prover
    prover = TLS13RFC9846TACACSIoTServiceIdentityVLLMMediaConnectorCVE202624779AndBentoMLRunnerCVE202644345Prover()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_tls13_rfc9846_vllm_cve2026_24779_and_bentoml_cve2026_44345_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_tls13_rfc9846_vllm_cve2026_24779_and_bentoml_cve2026_44345_safe else 1


def cmd_privacypass_batched_ollama_cve2026_108836_mlrun_cve2026_92568_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import PrivacyPassRFC9576BatchedTokensOllamaPullCVE2026108836AndMLRunWebhookCVE202692568SSRFProver
    prover = PrivacyPassRFC9576BatchedTokensOllamaPullCVE2026108836AndMLRunWebhookCVE202692568SSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_privacypass_batched_ollama_cve2026_108836_and_mlrun_cve2026_92568_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_privacypass_batched_ollama_cve2026_108836_and_mlrun_cve2026_92568_safe else 1


def cmd_mls_rfc9750_cbor_cde_http2_origin_grafana_ssrf_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import MLSRFC9750CBORCDERFC8949HTTP2OriginRFC8336AndGrafanaDatasourceProxyRoundcubeSSRFProver
    prover = MLSRFC9750CBORCDERFC8949HTTP2OriginRFC8336AndGrafanaDatasourceProxyRoundcubeSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_mls_rfc9750_cbor_cde_http2_origin_and_grafana_ssrf_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_mls_rfc9750_cbor_cde_http2_origin_and_grafana_ssrf_safe else 1


def cmd_mcp_contextforge_toctou_surrealdb_langflow_koa_cve2026_27959_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import MCPContextForgeGHSA9hgcTOCTOUSurrealDBLangflowRedirectSSRFAndKoaCVE202627959Ech0SVGProver
    prover = MCPContextForgeGHSA9hgcTOCTOUSurrealDBLangflowRedirectSSRFAndKoaCVE202627959Ech0SVGProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_mcp_contextforge_surrealdb_langflow_and_koa_cve2026_27959_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_mcp_contextforge_surrealdb_langflow_and_koa_cve2026_27959_safe else 1


def cmd_gocontainerregistry_ipv6_ssrf_dirac_cve2026_61668_dynaconf_ssti_audit(target_path: str) -> int:
    import os
    from dataclasses import asdict
    from aleph_core.verification import GoContainerRegistryIPv6TransitionSSRFDIRACCVE202661668TLSAndDynaconfGHSApxrrSSTIProver
    prover = GoContainerRegistryIPv6TransitionSSRFDIRACCVE202661668TLSAndDynaconfGHSApxrrSSTIProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_gocontainerregistry_ipv6_ssrf_dirac_cve2026_61668_and_dynaconf_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_gocontainerregistry_ipv6_ssrf_dirac_cve2026_61668_and_dynaconf_safe else 1


def cmd_mldsa_connolly_sframe_langflow_cve2025_3248_jupyter_envoy_audit(target_path: str) -> int:
    import os
    from dataclasses import asdict
    from aleph_core.verification import MLDSAConnolly2026SFrameRFC9605LangflowCVE20253248ASTExecAndJupyterProxyEnvoyAdminSSRFProver
    prover = MLDSAConnolly2026SFrameRFC9605LangflowCVE20253248ASTExecAndJupyterProxyEnvoyAdminSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_mldsa_connolly_sframe_langflow_cve2025_3248_and_jupyter_envoy_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_mldsa_connolly_sframe_langflow_cve2025_3248_and_jupyter_envoy_safe else 1


def cmd_eat_rfc9711_mlflow_cve2026_64849_qdrant_cve2024_3829_audit(target_path: str) -> int:
    import os
    from dataclasses import asdict
    from aleph_core.verification import EATRFC9711RFC9782AttestationMLflowCVE202664849SSRFAndQdrantSnapshotCVE20243829Prover
    prover = EATRFC9711RFC9782AttestationMLflowCVE202664849SSRFAndQdrantSnapshotCVE20243829Prover()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_eat_rfc9711_mlflow_cve2026_64849_and_qdrant_cve2024_3829_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_eat_rfc9711_mlflow_cve2026_64849_and_qdrant_cve2024_3829_safe else 1


def cmd_kong_cve2026_17578_autojack_contextforge_ssti_vaultwarden_ssrf_audit(target_path: str) -> int:
    from dataclasses import asdict
    from aleph_core.verification import KongEventGatewayCVE202617578AESGCMAutoJackCSWSHMCPContextForgeSSTIGHSAvwf3AndVaultwardenIconSSRFProver
    prover = KongEventGatewayCVE202617578AESGCMAutoJackCSWSHMCPContextForgeSSTIGHSAvwf3AndVaultwardenIconSSRFProver()
    if os.path.isdir(target_path):
        res = prover.verify_directory(target_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["formal_kong_cve2026_17578_autojack_contextforge_ssti_and_vaultwarden_safe"] else 1
    with open(target_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    rep = prover.verify_code(src, target_path)
    print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
    return 0 if rep.formal_kong_cve2026_17578_autojack_contextforge_ssti_and_vaultwarden_safe else 1



def dispatch_archived_cli_command(cmd: str, argv: Optional[List[str]] = None) -> Optional[int]:
    old_argv = sys.argv
    if argv is not None:
        sys.argv = argv
    try:
        if cmd == "verify-ha" and len(sys.argv) > 2:
            return (cmd_verify_ha(sys.argv[2]))
        elif cmd == "privacy-audit" and len(sys.argv) > 2:
            return (cmd_privacy_audit(sys.argv[2]))
        elif cmd == "verify-policy" and len(sys.argv) > 2:
            return (cmd_verify_policy(sys.argv[2]))
        elif cmd == "outbox-audit" and len(sys.argv) > 2:
            return (cmd_outbox_audit(sys.argv[2]))
        elif cmd == "verify-saga" and len(sys.argv) > 2:
            return (cmd_verify_saga(sys.argv[2]))
        elif cmd == "retry-check" and len(sys.argv) > 2:
            return (cmd_retry_check(sys.argv[2]))
        elif cmd == "leak-check" and len(sys.argv) > 2:
            return (cmd_leak_check(sys.argv[2]))
        elif cmd == "drift-check" and len(sys.argv) > 3:
            return (cmd_drift_check(sys.argv[2], sys.argv[3]))
        elif cmd == "deadlock-gate":
            t = sys.argv[2] if len(sys.argv) > 2 else "."
            return (cmd_deadlock_gate(t))
        elif cmd == "index-synth":
            t = sys.argv[2] if len(sys.argv) > 2 else "."
            return (cmd_index_synth(t))
        elif cmd == "verify-dict" and len(sys.argv) > 2:
            return (cmd_verify_dict(sys.argv[2]))
        elif cmd == "verify-complexity" and len(sys.argv) > 2:
            return (cmd_verify_complexity(sys.argv[2]))
        elif cmd == "repomap":
            d = sys.argv[2] if len(sys.argv) > 2 else "."
            b = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
            return (cmd_repomap(d, b))
        elif cmd == "frontend-ui" and len(sys.argv) > 2:
            return (cmd_frontend_ui(sys.argv[2]))
        elif cmd == "fullstack-rls" and len(sys.argv) > 2:
            ts_f = sys.argv[3] if len(sys.argv) > 3 else None
            return (cmd_fullstack_rls(sys.argv[2], ts_f))
        elif cmd == "zero-downtime-ddl" and len(sys.argv) > 2:
            return (cmd_zero_downtime_ddl(sys.argv[2]))
        elif cmd == "state-rollback" and len(sys.argv) > 2:
            return (cmd_state_rollback(sys.argv[2]))
        elif cmd == "idempotent-consumer" and len(sys.argv) > 2:
            return (cmd_idempotent_consumer(sys.argv[2]))
        elif cmd == "ssrf-audit" and len(sys.argv) > 2:
            return (cmd_ssrf_audit(sys.argv[2]))
        elif cmd == "crypto-timing" and len(sys.argv) > 2:
            return (cmd_crypto_timing(sys.argv[2]))
        elif cmd == "rate-limiter" and len(sys.argv) > 2:
            return (cmd_rate_limiter(sys.argv[2]))
        elif cmd == "align-prompt-cache" and len(sys.argv) > 2:
            c = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
            return (cmd_align_prompt_cache(sys.argv[2], c))
        elif cmd == "workspace-rollback" and len(sys.argv) > 4:
            return (cmd_workspace_rollback(sys.argv[2], sys.argv[3], sys.argv[4]))
        elif cmd == "queue-backpressure" and len(sys.argv) > 2:
            return (cmd_queue_backpressure(sys.argv[2]))
        elif cmd == "csp-audit" and len(sys.argv) > 2:
            return (cmd_csp_audit(sys.argv[2]))
        elif cmd == "multitenant-rls" and len(sys.argv) > 2:
            return (cmd_multitenant_rls(sys.argv[2]))
        elif cmd == "hmr-patch" and len(sys.argv) > 3:
            return (cmd_hmr_patch(sys.argv[2], sys.argv[3]))
        elif cmd == "merkle-repomap":
            d = sys.argv[2] if len(sys.argv) > 2 else "."
            b = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
            return (cmd_merkle_repomap(d, b))
        elif cmd == "design-tokens" and len(sys.argv) > 2:
            return (cmd_design_tokens(sys.argv[2]))
        elif cmd == "rsc-boundary" and len(sys.argv) > 2:
            return (cmd_rsc_boundary(sys.argv[2]))
        elif cmd == "deep-rls" and len(sys.argv) > 2:
            return (cmd_deep_rls(sys.argv[2]))
        elif cmd == "expand-contract" and len(sys.argv) > 2:
            return (cmd_expand_contract(sys.argv[2]))
        elif cmd == "redteam-audit" and len(sys.argv) > 2:
            return (cmd_redteam_audit(sys.argv[2]))
        elif cmd == "react-lifecycle" and len(sys.argv) > 2:
            return (cmd_react_lifecycle(sys.argv[2]))
        elif cmd == "impact-cone" and len(sys.argv) > 3:
            return (cmd_impact_cone(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1024))
        elif cmd == "master-release-audit" and len(sys.argv) > 2:
            return (cmd_master_release_audit(sys.argv[2]))
        elif cmd == "spec-slsa-audit" and len(sys.argv) > 3:
            return (cmd_spec_slsa_audit(sys.argv[2], sys.argv[3]))
        elif cmd == "ast-merge-repro" and len(sys.argv) > 4:
            return (cmd_ast_merge_repro(sys.argv[2], sys.argv[3], sys.argv[4]))
        elif cmd == "hermetic-sbom-audit" and len(sys.argv) > 2:
            tf = sys.argv[3] if len(sys.argv) > 3 else ""
            pr = sys.argv[4] if len(sys.argv) > 4 else "MONOTONICITY"
            return (cmd_hermetic_sbom_audit(sys.argv[2], tf, pr))
        elif cmd == "awwwards-ui" and len(sys.argv) > 2:
            obj = sys.argv[3] if len(sys.argv) > 3 else "awwwards_editorial_scrollytelling"
            return (cmd_awwwards_ui(sys.argv[2], obj))
        elif cmd == "diff-fuzz-intoto" and len(sys.argv) > 2:
            cf = sys.argv[3] if len(sys.argv) > 3 else ""
            ps = sys.argv[4] if len(sys.argv) > 4 else ""
            return (cmd_diff_fuzz_intoto(sys.argv[2], cf, ps))
        elif cmd == "awwwards-choreography" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsSotYCanvas"
            return (cmd_awwwards_choreography(sys.argv[2], cn))
        elif cmd == "awwwards-wcag22-cq" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsIntrinsicBento"
            return (cmd_awwwards_wcag22_cq(sys.argv[2], cn))
        elif cmd == "awwwards-inp-toplayer" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsINPTopLayerHero"
            return (cmd_awwwards_inp_toplayer(sys.argv[2], cn))
        elif cmd == "awwwards-dtcg-cv-actions" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsDTCGActionSurface"
            return (cmd_awwwards_dtcg_cv_actions(sys.argv[2], cn))
        elif cmd == "awwwards-speculation-rsc" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsSpeculativeRSCShell"
            return (cmd_awwwards_speculation_rsc(sys.argv[2], cn))
        elif cmd == "awwwards-intrinsic-webgpu" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsWebGPUIntrinsicStudio"
            return (cmd_awwwards_intrinsic_webgpu(sys.argv[2], cn))
        elif cmd == "awwwards-houdini-wcag-svg" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsHoudiniShaderCard"
            return (cmd_awwwards_houdini_wcag_svg(sys.argv[2], cn))
        elif cmd == "awwwards-positiontry-p3-inert" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "SovereignAwwwardsP3AnchoredStage"
            return (cmd_awwwards_positiontry_p3_inert(sys.argv[2], cn))
        elif cmd == "awwwards-carousel-vt-wcag1413" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "CarouselAndTooltipShowcase.tsx"
            return (cmd_awwwards_carousel_vt_wcag1413(sys.argv[2], cn))
        elif cmd == "awwwards-shape-readingflow-activity" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsBentoStage.tsx"
            return (cmd_awwwards_shape_readingflow_activity(sys.argv[2], cn))
        elif cmd == "awwwards-css-function-scrollstate" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsStickyHeaderAndOptimisticAction.tsx"
            return (cmd_awwwards_css_function_scrollstate(sys.argv[2], cn))
        elif cmd == "awwwards-css-if-attr-invoker" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsInvokerStageV9.tsx"
            return (cmd_awwwards_css_if_attr_invoker(sys.argv[2], cn))
        elif cmd == "awwwards-base-select-sibling-trim" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsCustomizableSelectAndKanban.tsx"
            return (cmd_awwwards_base_select_sibling_trim(sys.argv[2], cn))
        elif cmd == "awwwards-popover-hint-effect-event" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsPopoverHintAndEffectEventForm.tsx"
            return (cmd_awwwards_popover_hint_effect_event(sys.argv[2], cn))
        elif cmd == "awwwards-stretch-gap-cachesignal" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsBentoGapAndCacheSignalRSC.tsx"
            return (cmd_awwwards_stretch_gap_cachesignal(sys.argv[2], cn))
        elif cmd == "awwwards-closedby-cornershape-vtclass" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsSquircleDialogAndAuthModal.tsx"
            return (cmd_awwwards_closedby_cornershape_vtclass(sys.argv[2], cn))
        elif cmd == "awwwards-interest-masonry-reflow" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsInterestMasonryAndActionForm.tsx"
            return (cmd_awwwards_interest_masonry_reflow(sys.argv[2], cn))
        elif cmd == "awwwards-details-highlight-textspacing" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsExclusiveAccordionAndHighlightSearch.tsx"
            return (cmd_awwwards_details_highlight_textspacing(sys.argv[2], cn))
        elif cmd == "awwwards-lightdark-fontsizeadjust-pausestophide" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsLightDarkAndAccessibleMarqueeStage.tsx"
            return (cmd_awwwards_lightdark_fontsizeadjust_pausestophide(sys.argv[2], cn))
        elif cmd == "awwwards-colormix-shapeoutside-wcag1411" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsEditorialShapeAndHiDPICanvasStage.tsx"
            return (cmd_awwwards_colormix_shapeoutside_wcag1411(sys.argv[2], cn))
        elif cmd == "awwwards-subgrid-userinvalid-wcag333" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsSubgridAndWCAG333FormStage.tsx"
            return (cmd_awwwards_subgrid_userinvalid_wcag333(sys.argv[2], cn))
        elif cmd == "awwwards-linearspring-scrollbargutter-wcag334" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsLinearSpringAndWCAG334TransactionDrawer.tsx"
            return (cmd_awwwards_linearspring_scrollbargutter_wcag334(sys.argv[2], cn))
        elif cmd == "awwwards-startingstyle-textboxtrim-wcag221" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsTextBoxTrimAndWCAG221TimingStage.tsx"
            return (cmd_awwwards_startingstyle_textboxtrim_wcag221(sys.argv[2], cn))
        elif cmd == "awwwards-contrastcolor-reduceddata-wcag143" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsContrastColorAndAdaptiveBandwidthStage.tsx"
            return (cmd_awwwards_contrastcolor_reduceddata_wcag143(sys.argv[2], cn))
        elif cmd == "awwwards-animationrange-oklab-wcag233" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsAnimationRangeOKLabAndF95Stage.tsx"
            return (cmd_awwwards_animationrange_oklab_wcag233(sys.argv[2], cn))
        elif cmd == "awwwards-insetinline-systemcolor-wcag331" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsInsetInlineSystemColorAndWCAG331Stage.tsx"
            return (cmd_awwwards_insetinline_systemcolor_wcag331(sys.argv[2], cn))
        elif cmd == "awwwards-colorfn-textsizeadjust-wcagstatus" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsColorFnTextSizeAdjustAndPoliteOutputStage.tsx"
            return (cmd_awwwards_colorfn_textsizeadjust_wcagstatus(sys.argv[2], cn))
        elif cmd == "awwwards-lightdarkimage-inset-wcag1413" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsLightDarkImageInsetAndWCAG1413Stage.tsx"
            return (cmd_awwwards_lightdarkimage_inset_wcag1413(sys.argv[2], cn))
        elif cmd == "awwwards-centennial-level100-wcag22" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsCentennialLevel100MasterStage.tsx"
            return (cmd_awwwards_centennial_level100_wcag22(sys.argv[2], cn))
        elif cmd == "awwwards-scrollbars-where-wcag33" and len(sys.argv) > 2:
            cn = sys.argv[3] if len(sys.argv) > 3 else "AwwwardsScrollbarsWhereAndWCAG33Stage.tsx"
            return (cmd_awwwards_scrollbars_where_wcag33(sys.argv[2], cn))
        elif cmd == "dot-aleph-audit" and len(sys.argv) > 2:
            tp = sys.argv[3] if len(sys.argv) > 3 else ".aleph/UNIFIED_GOVERNANCE_MANIFEST.json"
            return (cmd_dot_aleph_audit(sys.argv[2], tp))
        elif cmd == "aead-cswsh-graphql-audit" and len(sys.argv) > 2:
            return (cmd_aead_cswsh_graphql_audit(sys.argv[2]))
        elif cmd == "ecdsa-ssti-ipv6-ssrf-audit" and len(sys.argv) > 2:
            return (cmd_ecdsa_ssti_ipv6_ssrf_audit(sys.argv[2]))
        elif cmd == "jwk-rsaoaep-sri-audit" and len(sys.argv) > 2:
            return (cmd_jwk_rsaoaep_sri_audit(sys.argv[2]))
        elif cmd == "webauthn-nosql-archive-audit" and len(sys.argv) > 2:
            return (cmd_webauthn_nosql_archive_audit(sys.argv[2]))
        elif cmd == "argon2id-host-grpc-audit" and len(sys.argv) > 2:
            return (cmd_argon2id_host_grpc_audit(sys.argv[2]))
        elif cmd == "trojan-x509-webhook-audit" and len(sys.argv) > 2:
            return (cmd_trojan_x509_webhook_audit(sys.argv[2]))
        elif cmd == "cors-mass-assign-svg-audit" and len(sys.argv) > 2:
            return (cmd_cors_mass_assign_svg_audit(sys.argv[2]))
        elif cmd == "pqc-cookie-dns-rebind-audit" and len(sys.argv) > 2:
            return (cmd_pqc_cookie_dns_rebind_audit(sys.argv[2]))
        elif cmd == "mldsa-saml-redirect-audit" and len(sys.argv) > 2:
            return (cmd_mldsa_saml_redirect_audit(sys.argv[2]))
        elif cmd == "slhdsa-postmessage-imdsv2-audit" and len(sys.argv) > 2:
            return (cmd_slhdsa_postmessage_imdsv2_audit(sys.argv[2]))
        elif cmd == "hpke-oauth-headless-turn-audit" and len(sys.argv) > 2:
            return (cmd_hpke_oauth_headless_turn_audit(sys.argv[2]))
        elif cmd == "tls13-xsleaks-urlparser-audit" and len(sys.argv) > 2:
            return (cmd_tls13_xsleaks_urlparser_audit(sys.argv[2]))
        elif cmd == "jwe-csp-baseuri-envoy-audit" and len(sys.argv) > 2:
            return (cmd_jwe_csp_baseuri_envoy_audit(sys.argv[2]))
        elif cmd == "sdjwt-worker-uds-audit" and len(sys.argv) > 2:
            return (cmd_sdjwt_worker_uds_audit(sys.argv[2]))
        elif cmd == "cose-fetchmeta-connect-audit" and len(sys.argv) > 2:
            return (cmd_cose_fetchmeta_connect_audit(sys.argv[2]))
        elif cmd == "rfc9421-clearsitedata-etcd-audit" and len(sys.argv) > 2:
            return (cmd_rfc9421_clearsitedata_etcd_audit(sys.argv[2]))
        elif cmd == "uuidv7-sandbox-altsvc-audit" and len(sys.argv) > 2:
            return (cmd_uuidv7_sandbox_altsvc_audit(sys.argv[2]))
        elif cmd == "dpop-fencedframe-h2c-audit" and len(sys.argv) > 2:
            return (cmd_dpop_fencedframe_h2c_audit(sys.argv[2]))
        elif cmd == "oprf-trustedtypes-fcgi-audit" and len(sys.argv) > 2:
            return (cmd_oprf_trustedtypes_fcgi_audit(sys.argv[2]))
        elif cmd == "mls-importmap-cilium-audit" and len(sys.argv) > 2:
            return (cmd_mls_importmap_cilium_audit(sys.argv[2]))
        elif cmd == "frost-referrer-vault-audit" and len(sys.argv) > 2:
            return (cmd_frost_referrer_vault_audit(sys.argv[2]))
        elif cmd == "rfc9380-docisolation-ray-audit" and len(sys.argv) > 2:
            return (cmd_rfc9380_docisolation_ray_audit(sys.argv[2]))
        elif cmd == "ocsp-permissions-sonicwall-audit" and len(sys.argv) > 2:
            return (cmd_ocsp_permissions_sonicwall_audit(sys.argv[2]))
        elif cmd == "ct-rfc9162-coop-craft-audit" and len(sys.argv) > 2:
            return (cmd_ct_rfc9162_coop_craft_audit(sys.argv[2]))
        elif cmd == "tls-rfc8879-integrity-gitlab-audit" and len(sys.argv) > 2:
            return (cmd_tls_rfc8879_integrity_gitlab_audit(sys.argv[2]))
        elif cmd == "ct-consistency-permissions-ai-nextjs-audit" and len(sys.argv) > 2:
            return (cmd_ct_consistency_permissions_ai_nextjs_audit(sys.argv[2]))
        elif cmd == "ocsp-ext-revoked-mcp-ssrf-audit" and len(sys.argv) > 2:
            return (cmd_ocsp_ext_revoked_mcp_ssrf_audit(sys.argv[2]))
        elif cmd == "ocsp-sigalg-docker-lmdeploy-audit" and len(sys.argv) > 2:
            return (cmd_ocsp_sigalg_docker_lmdeploy_audit(sys.argv[2]))
        elif cmd == "ocsp-archive-cutoff-alt-ip-ssrf-audit" and len(sys.argv) > 2:
            return (cmd_ocsp_archive_cutoff_alt_ip_ssrf_audit(sys.argv[2]))
        elif cmd == "ocsp-servicelocator-pinned-ssrf-audit" and len(sys.argv) > 2:
            return (cmd_ocsp_servicelocator_pinned_ssrf_audit(sys.argv[2]))
        elif cmd == "polyglot-bridge" and len(sys.argv) > 3:
            sf = sys.argv[4] if len(sys.argv) > 4 else ""
            return (cmd_polyglot_bridge(sys.argv[2], sys.argv[3], sf))
        elif cmd == "simhash-kv" and len(sys.argv) > 2:
            mf = sys.argv[3] if len(sys.argv) > 3 else ""
            return (cmd_simhash_kv(sys.argv[2], mf))
        elif cmd == "tarjan-pyo3" and len(sys.argv) > 2:
            return (cmd_tarjan_pyo3(sys.argv[2]))
        elif cmd == "dominator-wasm" and len(sys.argv) > 2:
            return (cmd_dominator_wasm(sys.argv[2]))
        elif cmd == "rowan-cst" and len(sys.argv) > 2:
            return (cmd_rowan_cst(sys.argv[2]))
        elif cmd == "pld-arena" and len(sys.argv) > 2:
            return (cmd_pld_arena(sys.argv[2]))
        elif cmd == "salsa-rkyv" and len(sys.argv) > 2:
            return (cmd_salsa_rkyv(sys.argv[2]))
        elif cmd == "roaring-iouring" and len(sys.argv) > 2:
            return (cmd_roaring_iouring(sys.argv[2]))
        elif cmd == "egraph-pyramidkv" and len(sys.argv) > 2:
            return (cmd_egraph_pyramidkv(sys.argv[2]))
        elif cmd == "hub-epoch-quest" and len(sys.argv) > 2:
            return (cmd_hub_epoch_quest(sys.argv[2]))
        elif cmd == "stackgraph-simd-duo" and len(sys.argv) > 2:
            return (cmd_stackgraph_simd_duo(sys.argv[2]))
        elif cmd == "fmindex-uninit-kivi" and len(sys.argv) > 2:
            return (cmd_fmindex_uninit_kivi(sys.argv[2]))
        elif cmd == "ett-treeborrows-minf" and len(sys.argv) > 2:
            return (cmd_ett_treeborrows_minf(sys.argv[2]))
        elif cmd == "ddlog-sendsync-yoco" and len(sys.argv) > 2:
            return (cmd_ddlog_sendsync_yoco(sys.argv[2]))
        elif cmd == "ahocorasick-ffi-mla" and len(sys.argv) > 2:
            return (cmd_ahocorasick_ffi_mla(sys.argv[2]))
        elif cmd == "lct-transmute-infllm" and len(sys.argv) > 2:
            return (cmd_lct_transmute_infllm(sys.argv[2]))
        elif cmd == "fwdpush-staticmut-loki" and len(sys.argv) > 2:
            return (cmd_fwdpush_staticmut_loki(sys.argv[2]))
        elif cmd == "fora-strictprov-chunkkv" and len(sys.argv) > 2:
            return (cmd_fora_strictprov_chunkkv(sys.argv[2]))
        elif cmd == "resacc-unsafecell-minicache" and len(sys.argv) > 2:
            return (cmd_resacc_unsafecell_minicache(sys.argv[2]))
        elif cmd == "chebppr-slice-razor" and len(sys.argv) > 2:
            return (cmd_chebppr_slice_razor(sys.argv[2]))
        elif cmd == "effres-unaligned-adakv" and len(sys.argv) > 2:
            return (cmd_effres_unaligned_adakv(sys.argv[2]))
        elif cmd == "blockrank-zst-cla" and len(sys.argv) > 2:
            return (cmd_blockrank_zst_cla(sys.argv[2]))
        elif cmd == "quadext-dealloc-think" and len(sys.argv) > 2:
            return (cmd_quadext_dealloc_think(sys.argv[2]))
        elif cmd == "gauss-copy-gear" and len(sys.argv) > 2:
            return (cmd_gauss_copy_gear(sys.argv[2]))
        elif cmd == "arnoldi-setlen-palu" and len(sys.argv) > 2:
            return (cmd_arnoldi_setlen_palu(sys.argv[2]))
        elif cmd == "anderson-utf8-kvquant" and len(sys.argv) > 2:
            return (cmd_anderson_utf8_kvquant(sys.argv[2]))
        elif cmd == "rre-fromraw-retrievalkv" and len(sys.argv) > 2:
            return (cmd_rre_fromraw_retrievalkv(sys.argv[2]))
        elif cmd == "innerouter-cstr-shadowkv" and len(sys.argv) > 2:
            return (cmd_innerouter_cstr_shadowkv(sys.argv[2]))
        elif cmd == "adaptive-mandrop-gemfilter" and len(sys.argv) > 2:
            return (cmd_adaptive_mandrop_gemfilter(sys.argv[2]))
        elif cmd == "aitken-nonnull-fastgen" and len(sys.argv) > 2:
            return (cmd_aitken_nonnull_fastgen(sys.argv[2]))
        elif cmd == "lumping-getunchecked-squeeze" and len(sys.argv) > 2:
            return (cmd_lumping_getunchecked_squeeze(sys.argv[2]))
        elif cmd == "blocktri-packed-cake" and len(sys.argv) > 2:
            return (cmd_blocktri_packed_cake(sys.argv[2]))
        elif cmd == "bicgstab-writebytes-kvcompress" and len(sys.argv) > 2:
            return (cmd_bicgstab_writebytes_kvcompress(sys.argv[2]))
        elif cmd == "acl-swap-qfilters" and len(sys.argv) > 2:
            return (cmd_acl_swap_qfilters(sys.argv[2]))
        elif cmd == "speedppr-slicemut-l2norm" and len(sys.argv) > 2:
            return (cmd_speedppr_slicemut_l2norm(sys.argv[2]))
        elif cmd == "fista-volatile-tova" and len(sys.argv) > 2:
            return (cmd_fista_volatile_tova(sys.argv[2]))
        elif cmd == "rbs-drop-scissorhands" and len(sys.argv) > 2:
            return (cmd_rbs_drop_scissorhands(sys.argv[2]))
        elif cmd == "topppr-replace-keyformer" and len(sys.argv) > 2:
            return (cmd_topppr_replace_keyformer(sys.argv[2]))
        elif cmd == "hkpr-ptrread-scissorhands20x" and len(sys.argv) > 2:
            return (cmd_hkpr_ptrread_scissorhands20x(sys.argv[2]))
        elif cmd == "bernnet-ptrwrite-aerosketch" and len(sys.argv) > 2:
            return (cmd_bernnet_ptrwrite_aerosketch(sys.argv[2]))
        elif cmd == "chebnetii-provenance-l2kv" and len(sys.argv) > 2:
            return (cmd_chebnetii_provenance_l2kv(sys.argv[2]))
        elif cmd == "sublinear-add-disjoint-tova" and len(sys.argv) > 2:
            return (cmd_sublinear_add_disjoint_tova(sys.argv[2]))
        elif cmd == "dynelm-volatile-qfilterl2" and len(sys.argv) > 2:
            return (cmd_dynelm_volatile_qfilterl2(sys.argv[2]))
        elif cmd == "css-scope-style-focus-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_css_scope_style_focus_audit(sys.argv[2], acc))
        elif cmd == "vt-anchor-focus-obscured-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_vt_anchor_focus_obscured_audit(sys.argv[2], acc))
        elif cmd == "textbox-calcsize-auth-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_textbox_calcsize_auth_audit(sys.argv[2], acc))
        elif cmd == "viewtimeline-posvis-help-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_viewtimeline_posvis_help_audit(sys.argv[2], acc))
        elif cmd == "relative-oklch-startingstyle-redundant-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_relative_oklch_startingstyle_redundant_audit(sys.argv[2], acc))
        elif cmd == "subgrid-contentvis-reflow-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_subgrid_contentvis_reflow_audit(sys.argv[2], acc))
        elif cmd == "popover-interpolatesize-target-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_popover_interpolatesize_target_audit(sys.argv[2], acc))
        elif cmd == "fieldsizing-uservalid-error-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_fieldsizing_uservalid_error_audit(sys.argv[2], acc))
        elif cmd == "linearspring-scrollbargutter-errorprev-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_linearspring_scrollbargutter_errorprev_audit(sys.argv[2], acc))
        elif cmd == "lightdark-colormix-nontext-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_lightdark_colormix_nontext_audit(sys.argv[2], acc))
        elif cmd == "speculationrules-textwrap-forcedcolors-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_speculationrules_textwrap_forcedcolors_audit(sys.argv[2], acc))
        elif cmd == "houdini-fontsizeadjust-pause-audit" and len(sys.argv) > 2:
            acc = sys.argv[3] if len(sys.argv) > 3 else "oklch(0.68 0.19 265)"
            return (cmd_houdini_fontsizeadjust_pause_audit(sys.argv[2], acc))
        elif cmd == "vcorfu-csmr-autobahn-bft":
            from aleph_core.verification.z3_prover import VCorfuMaterializedStreamsComposableSMRAndAutobahnSeamlessHighSpeedBFTProver
            rep = VCorfuMaterializedStreamsComposableSMRAndAutobahnSeamlessHighSpeedBFTProver.audit_and_repair_vcorfu_csmr_and_autobahn_bft()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "halfmoon-logoptimal-shoalpp-dag":
            from aleph_core.verification.z3_prover import HalfmoonLogOptimalStatefulServerlessAndShoalPlusPlusFastDirectCommitStaggeredDAGProver
            rep = HalfmoonLogOptimalStatefulServerlessAndShoalPlusPlusFastDirectCommitStaggeredDAGProver.audit_and_repair_halfmoon_and_shoal_plusplus()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "beldi-intent-kudzu-bft":
            from aleph_core.verification.z3_prover import BeldiTransactionalServerlessIntentCollectorAndKudzuFastSimpleHighThroughputBFTProver
            rep = BeldiTransactionalServerlessIntentCollectorAndKudzuFastSimpleHighThroughputBFTProver.audit_and_repair_beldi_and_kudzu_bft()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "tango-sharedlog-hydrangea-bft":
            from aleph_core.verification.z3_prover import TangoDistributedDataStructuresSharedLogAndHydrangeaOptimisticTwoRoundMixedFaultBFTProver
            rep = TangoDistributedDataStructuresSharedLogAndHydrangeaOptimisticTwoRoundMixedFaultBFTProver.audit_and_repair_tango_and_hydrangea_bft()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "fuzzylog-colordag-mirbft":
            from aleph_core.verification.z3_prover import FuzzyLogPartiallyOrderedColorDAGAndMirBFTRotatingBucketMultiLeaderProver
            rep = FuzzyLogPartiallyOrderedColorDAGAndMirBFTRotatingBucketMultiLeaderProver.audit_and_repair_fuzzylog_and_mirbft()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "replex-multiindex-simplex-bft":
            from aleph_core.verification.z3_prover import ReplexHybridMultiIndexChainReplicationAndSimplexDummyBlockFastViewChangeConsensusProver
            rep = ReplexHybridMultiIndexChainReplicationAndSimplexDummyBlockFastViewChangeConsensusProver.audit_and_repair_replex_and_simplex_consensus()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "ford-rdma-gatling-bft":
            from aleph_core.verification.z3_prover import FORDOneSidedRDMADisaggregatedPMTransactionAndGatlingRapidFireParallelConsensusProver
            rep = FORDOneSidedRDMADisaggregatedPMTransactionAndGatlingRapidFireParallelConsensusProver.audit_and_repair_ford_rdma_and_gatling_consensus()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "motor-cvt-alpenglow-bft":
            from aleph_core.verification.z3_prover import MotorConsecutiveVersionTupleDisaggregatedMVCCAndAlpenglowVotorRotorDualPathConsensusProver
            rep = MotorConsecutiveVersionTupleDisaggregatedMVCCAndAlpenglowVotorRotorDualPathConsensusProver.audit_and_repair_motor_cvt_and_alpenglow_consensus()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "boki-logbook-remora-dag":
            from aleph_core.verification.z3_prover import BokiStatefulServerlessLogBookReadCacheAndRemoraOptimisticPathDAGProver
            rep = BokiStatefulServerlessLogBookReadCacheAndRemoraOptimisticPathDAGProver.audit_and_repair_boki_logbook_and_remora_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "delos-vlog-lightdag":
            from aleph_core.verification.z3_prover import DelosVirtualLogLogletSealingAndLightDAGConsistentBroadcastTotalityProver
            rep = DelosVirtualLogLogletSealingAndLightDAGConsistentBroadcastTotalityProver.audit_and_repair_delos_virtuallog_and_lightdag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "scalog-cut-starfish-dag":
            from aleph_core.verification.z3_prover import ScalogSharedLogCutAggregatorTotalOrderAndStarfishErasureCodedUncertifiedDAGProver
            rep = ScalogSharedLogCutAggregatorTotalOrderAndStarfishErasureCodedUncertifiedDAGProver.audit_and_repair_scalog_cut_and_starfish_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "deuteronomy-tc-gradeddag":
            from aleph_core.verification.z3_prover import DeuteronomyDecoupledTransactionDataComponentLLSNAndGradedDAGTwoRoundBroadcastConsensusProver
            rep = DeuteronomyDecoupledTransactionDataComponentLLSNAndGradedDAGTwoRoundBroadcastConsensusProver.audit_and_repair_deuteronomy_tc_dc_and_graded_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "callas-rnl-mahimahi-dag":
            from aleph_core.verification.z3_prover import CallasModularConcurrencyGoldenRulesRNLAndMahiMahiMultiLeaderAsynchronousUncertifiedDAGProver
            rep = CallasModularConcurrencyGoldenRulesRNLAndMahiMahiMultiLeaderAsynchronousUncertifiedDAGProver.audit_and_repair_callas_rnl_mahimahi_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "orthrus-cc-jolteon-ditto-dag":
            from aleph_core.verification.z3_prover import OrthrusMessagePassingDecoupledConcurrencyAndJolteonDittoTwoChainAsynchronousFallbackDAGProver
            rep = OrthrusMessagePassingDecoupledConcurrencyAndJolteonDittoTwoChainAsynchronousFallbackDAGProver.audit_and_repair_orthrus_cc_jolteon_ditto_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "foedus-occ-mysticeti-dag":
            from aleph_core.verification.z3_prover import FOEDUSDualPageSnapshotMasterTreeOCCAndMysticetiUncertifiedFastCommitPathDAGProver
            rep = FOEDUSDualPageSnapshotMasterTreeOCCAndMysticetiUncertifiedFastCommitPathDAGProver.audit_and_repair_foedus_occ_mysticeti_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "hyper-mvcc-hotstuff1-dag":
            from aleph_core.verification.z3_prover import HyPerPrecisionLockingUndoBufferMVCCAndHotStuff1OnePhaseSpeculativeSlottingDAGProver
            rep = HyPerPrecisionLockingUndoBufferMVCCAndHotStuff1OnePhaseSpeculativeSlottingDAGProver.audit_and_repair_hyper_mvcc_hotstuff1_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "hekaton-mvcc-dumbong-dag":
            from aleph_core.verification.z3_prover import HekatonLockFreeMVCCSpeculativeCommitDepAndDumboNGThroughputObliviousBroadcastDAGProver
            rep = HekatonLockFreeMVCCSpeculativeCommitDepAndDumboNGThroughputObliviousBroadcastDAGProver.audit_and_repair_hekaton_mvcc_dumbong_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "plor-tail-fin-acs-dag":
            from aleph_core.verification.z3_prover import PlorPessimisticLockOptimisticReadTailLatencyAndFINSignatureFreeConstantTimeACSDAGProver
            rep = PlorPessimisticLockOptimisticReadTailLatencyAndFINSignatureFreeConstantTimeACSDAGProver.audit_and_repair_plor_tail_fin_acs_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "bcc-occ-dagrider-dag":
            from aleph_core.verification.z3_prover import BCCBalancedOCCAntiDependencyPatternAndDAGRiderFourRoundWaveQuantumSafeConsensusProver
            rep = BCCBalancedOCCAntiDependencyPatternAndDAGRiderFourRoundWaveQuantumSafeConsensusProver.audit_and_repair_bcc_occ_dagrider_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "mocc-temperature-bbca-dag":
            from aleph_core.verification.z3_prover import MOCCAdaptiveTemperatureCanonicalLockAndBBCAChainSingleMessageAnchorProbeDAGProver
            rep = MOCCAdaptiveTemperatureCanonicalLockAndBBCAChainSingleMessageAnchorProbeDAGProver.audit_and_repair_mocc_temperature_bbca_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "ermia-ssn-cordial-dag":
            from aleph_core.verification.z3_prover import ERMIASerialSafetyNetPiEtaExclusionAndCordialMinersUncertifiedBlockDAGProver
            rep = ERMIASerialSafetyNetPiEtaExclusionAndCordialMinersUncertifiedBlockDAGProver.audit_and_repair_ermia_ssn_cordial_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "ic3-constrained-hammerhead-dag":
            from aleph_core.verification.z3_prover import IC3ConstrainedParallelPieceDependencyGraphAndHammerHeadLeaderUtilizationDAGProver
            rep = IC3ConstrainedParallelPieceDependencyGraphAndHammerHeadLeaderUtilizationDAGProver.audit_and_repair_ic3_constrained_hammerhead_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "quecc-priority-shoal-dag":
            from aleph_core.verification.z3_prover import QueCCPriorityQueueControlFreeExecutionAndShoalPipelinedReputationDAGProver
            rep = QueCCPriorityQueueControlFreeExecutionAndShoalPipelinedReputationDAGProver.audit_and_repair_quecc_priority_shoal_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "pwv-rendezvous-sailfish-dag":
            from aleph_core.verification.z3_prover import PWVPieceWiseEarlyWriteVisibilityRendezvousAndSailfishOneRoundLeaderDAGProver
            rep = PWVPieceWiseEarlyWriteVisibilityRendezvousAndSailfishOneRoundLeaderDAGProver.audit_and_repair_pwv_rendezvous_sailfish_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "caracal-batch-narwhal-tusk-dag":
            from aleph_core.verification.z3_prover import CaracalDeterministicPreInitializedVersionArrayAndNarwhalTuskZeroOverheadDAGProver
            rep = CaracalDeterministicPreInitializedVersionArrayAndNarwhalTuskZeroOverheadDAGProver.audit_and_repair_caracal_batch_narwhal_tusk_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "polyjuice-policy-meerkat-quorum-dag":
            from aleph_core.verification.z3_prover import PolyjuiceLearnedPolicyMatrixSafetyGuardAndMeerkatZeroCoordinationFastQuorumDAGProver
            rep = PolyjuiceLearnedPolicyMatrixSafetyGuardAndMeerkatZeroCoordinationFastQuorumDAGProver.audit_and_repair_polyjuice_policy_meerkat_quorum_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "janus-scc-consensus-taurus-lv-dag":
            from aleph_core.verification.z3_prover import JanusDependencyGraphSCCConsensusAndTaurusParallelLoggingLSNVectorDAGProver
            rep = JanusDependencyGraphSCCConsensusAndTaurusParallelLoggingLSNVectorDAGProver.audit_and_repair_janus_scc_consensus_taurus_lv_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "sundial-logical-lease-tapir-dag":
            from aleph_core.verification.z3_prover import SundialLogicalLeaseCachingAndTAPIRInconsistentReplicationFastQuorumDAGProver
            rep = SundialLogicalLeaseCachingAndTAPIRInconsistentReplicationFastQuorumDAGProver.audit_and_repair_sundial_logical_lease_tapir_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "bamboo-retired-lock-rococo-dag":
            from aleph_core.verification.z3_prover import BambooRetiredLockEarlyReleaseCommitBarrierAndRococoDeferredPieceDAGProver
            rep = BambooRetiredLockEarlyReleaseCommitBarrierAndRococoDeferredPieceDAGProver.audit_and_repair_bamboo_retired_lock_rococo_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "tictoc-interval-cicada-mvcc-dag":
            from aleph_core.verification.z3_prover import TicTocDataDrivenTimestampIntervalExtensionAndCicadaContentionAwareMVCCDAGProver
            rep = TicTocDataDrivenTimestampIntervalExtensionAndCicadaContentionAwareMVCCDAGProver.audit_and_repair_tictoc_interval_cicada_mvcc_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "caracal-batch-append-bohm-mvcc-dag":
            from aleph_core.verification.z3_prover import CaracalBatchAppendHotspotPieceSplittingAndBohmPlaceholderMVCCDAGProver
            rep = CaracalBatchAppendHotspotPieceSplittingAndBohmPlaceholderMVCCDAGProver.audit_and_repair_caracal_batch_append_bohm_mvcc_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "block-stm-mvmemory-incarnation-dag":
            from aleph_core.verification.z3_prover import BlockSTMMVMemoryEstimateMarkerAndIncarnationValidationDAGProver
            rep = BlockSTMMVMemoryEstimateMarkerAndIncarnationValidationDAGProver.audit_and_repair_block_stm_mvmemory_incarnation_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "silo-three-phase-occ-tid-dag":
            from aleph_core.verification.z3_prover import SiloThreePhaseOCCSortedWriteLockAndTIDWordValidationDAGProver
            rep = SiloThreePhaseOCCSortedWriteLockAndTIDWordValidationDAGProver.audit_and_repair_silo_three_phase_occ_tid_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "aria-epoch-batch-reservation-dag":
            from aleph_core.verification.z3_prover import AriaDeterministicEpochBatchReservationAndConflictReorderingZero2PCDAGProver
            rep = AriaDeterministicEpochBatchReservationAndConflictReorderingZero2PCDAGProver.audit_and_repair_aria_epoch_batch_reservation_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "ssi-rw-antidependency-phantom-lock-dag":
            from aleph_core.verification.z3_prover import SerializableSnapshotIsolationRWAntidependencyCycleAndPhantomPredicateLockDAGProver
            rep = SerializableSnapshotIsolationRWAntidependencyCycleAndPhantomPredicateLockDAGProver.audit_and_repair_ssi_rw_antidependency_phantom_lock_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "epoch-wal-group-commit-truncate-dag":
            from aleph_core.verification.z3_prover import EpochFencedLeaseWriteAheadLogGroupCommitAndLinearizableTruncateDAGProver
            rep = EpochFencedLeaseWriteAheadLogGroupCommitAndLinearizableTruncateDAGProver.audit_and_repair_epoch_wal_group_commit_truncate_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "bft-three-chain-equivocation-dag":
            from aleph_core.verification.z3_prover import ByzantineQuorumCertificateThreeChainFinalityAndEquivocationSlashingDAGProver
            rep = ByzantineQuorumCertificateThreeChainFinalityAndEquivocationSlashingDAGProver.audit_and_repair_bft_three_chain_equivocation_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "joint-consensus-readindex-lease-dag":
            from aleph_core.verification.z3_prover import DynamicQuorumJointConsensusReadIndexLeaseAndSplitBrainPreventionDAGProver
            rep = DynamicQuorumJointConsensusReadIndexLeaseAndSplitBrainPreventionDAGProver.audit_and_repair_joint_consensus_readindex_lease_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "saga-pivot-compensation-dag":
            from aleph_core.verification.z3_prover import SagaPivotPhaseOrderingReverseTopologicalCompensationAndOutboxDAGProver
            rep = SagaPivotPhaseOrderingReverseTopologicalCompensationAndOutboxDAGProver.audit_and_repair_saga_pivot_compensation_dag()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "mazurkiewicz-dpor-diamond-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import MazurkiewiczTraceEquivalenceOptimalDPORAndDiamondCommutativityDAGProver
            rep = MazurkiewiczTraceEquivalenceOptimalDPORAndDiamondCommutativityDAGProver.verify_and_synthesize_mazurkiewicz_dpor_diamond_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "drr-maxmin-quota-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import DeficitRoundRobinMaxMinFairnessAndMultiTenantTokenQuotaIsolationDAGProver
            rep = DeficitRoundRobinMaxMinFairnessAndMultiTenantTokenQuotaIsolationDAGProver.verify_and_synthesize_drr_maxmin_quota_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "chandy-lamport-causal-cut-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import ChandyLamportConsistentCausalCutAndDominoFreeRollbackRecoveryDAGProver
            rep = ChandyLamportConsistentCausalCutAndDominoFreeRollbackRecoveryDAGProver.verify_and_synthesize_chandy_lamport_causal_cut_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "vector-clock-semilattice-hedged-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import VectorClockCausalBarrierJoinSemilatticeReducerAndHedgedStragglerIdempotentDAGProver
            rep = VectorClockCausalBarrierJoinSemilatticeReducerAndHedgedStragglerIdempotentDAGProver.verify_and_synthesize_vector_clock_semilattice_hedged_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "credit-parks-cmh-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import CreditBasedBackpressureParksBoundedBufferAndChandyMisraHaasKnotFreeDAGProver
            rep = CreditBasedBackpressureParksBoundedBufferAndChandyMisraHaasKnotFreeDAGProver.verify_and_synthesize_credit_parks_cmh_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "edf-wait-die-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import EDFWorkConservingLaxityAndWaitDieStarvationFreeDAGProver
            rep = EDFWorkConservingLaxityAndWaitDieStarvationFreeDAGProver.verify_and_synthesize_edf_wait_die_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "critical-path-brent-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import CriticalPathBrentMakespanAndPriorityInheritanceHolBlockingFreeDAGProver
            rep = CriticalPathBrentMakespanAndPriorityInheritanceHolBlockingFreeDAGProver.verify_and_synthesize_critical_path_brent_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "action-intent-deadswitch":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import ContextCarryingActionIntentEpochFencedDeadSwitchAndNurseryCancellationProver
            rep = ContextCarryingActionIntentEpochFencedDeadSwitchAndNurseryCancellationProver.verify_and_synthesize_action_intent_deadswitch()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "speculative-wave-mvmemory":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import SpeculativeWaveReadWriteConflictMVMemoryAndCausalEdgeSynthesizerProver
            rep = SpeculativeWaveReadWriteConflictMVMemoryAndCausalEdgeSynthesizerProver.verify_and_synthesize_speculative_wave_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "durable-replay-bft-wave":
            return (cmd_durable_replay_bft_wave())
        elif cmd == "speculative-recovery-minimmit-bft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import SpeculativeRecoveryDisaggregatedSuperCollapseAndMinimmitGenericSimplexSignatureFreeConsensusProver
            rep = SpeculativeRecoveryDisaggregatedSuperCollapseAndMinimmitGenericSimplexSignatureFreeConsensusProver.verify_and_synthesize_speculative_recovery_and_minimmit_consensus()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "mako-speculative-2pc-banyan-bft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import MakoSpeculative2PCGeoReplicationAndBanyanFastRotatingLeaderTwoStepBFTProver
            rep = MakoSpeculative2PCGeoReplicationAndBanyanFastRotatingLeaderTwoStepBFTProver.verify_and_synthesize_mako_speculative_2pc_and_banyan_bft()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "rtx-repairable-index-simple-it-bft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import RTXRepairableDisaggregatedMemoryIndexTransactionAndSimpleITSignatureFreeSpeculativePipelinedBFTProver
            rep = RTXRepairableDisaggregatedMemoryIndexTransactionAndSimpleITSignatureFreeSpeculativePipelinedBFTProver.verify_and_synthesize_rtx_repairable_index_and_simple_it_bft()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "foresight-predictive-db-autopilot-bft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import ForeSightPredictiveSchedulingDeterministicDatabaseAndAutoPilotAdaptiveByzantineResilientAutobahnBFTProver
            rep = ForeSightPredictiveSchedulingDeterministicDatabaseAndAutoPilotAdaptiveByzantineResilientAutobahnBFTProver.verify_and_synthesize_foresight_predictive_db_and_autopilot_bft()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "nox-disaggregated-index-hydra-multibft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import NoxCompilerRuntimeDisaggregatedMemoryIndexAndHydraObjectCentricGlobalOrderingFreeMultiBFTProver
            rep = NoxCompilerRuntimeDisaggregatedMemoryIndexAndHydraObjectCentricGlobalOrderingFreeMultiBFTProver.verify_and_synthesize_nox_disaggregated_index_and_hydra_multibft()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "tiga-1wrtt-geo-tx-cassandra-bft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import TigaSynchronizedClockOneWRTTGeoTransactionAndCassandraTwoTierPoAPoRPartitionableBFTProver
            rep = TigaSynchronizedClockOneWRTTGeoTransactionAndCassandraTwoTierPoAPoRPartitionableBFTProver.verify_and_synthesize_tiga_1wrtt_and_cassandra_partitionable_bft()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "quirinus-geo-dcc-pine-consistency":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import QuirinusGeoReplicatedDCCBatchSnapshotAndPineHardSoftDAGConsistencyProver
            rep = QuirinusGeoReplicatedDCCBatchSnapshotAndPineHardSoftDAGConsistencyProver.verify_and_synthesize_quirinus_geo_dcc_and_pine_consistency()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "vigil-selective-silence-brbco-causal":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import VigilAccountableLivenessSelectiveSilenceAndBRBCOCausalByzantineBroadcastProver
            rep = VigilAccountableLivenessSelectiveSilenceAndBRBCOCausalByzantineBroadcastProver.verify_and_synthesize_vigil_selective_silence_and_brbco_causal_broadcast()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "prdts-finite-counter-trm-raft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import PRDTSParameterizedFiniteCounterReductionAndTRMRaftByzantineReputationProver
            rep = PRDTSParameterizedFiniteCounterReductionAndTRMRaftByzantineReputationProver.verify_and_synthesize_prdts_finite_counter_and_trm_raft()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "fast-tendermint-flamingo-dag":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import FastTendermintTwoStepMergedStateAndFlamingoDualLayerDAGLoadBalancingProver
            rep = FastTendermintTwoStepMergedStateAndFlamingoDualLayerDAGLoadBalancingProver.verify_and_synthesize_fast_tendermint_and_flamingo_dag()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "seamless-dag-bft-hakicc":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import SeamlessDAGBFTFourRoundReconfigurationAndHakiCCTwoStageVerifiedCCProver
            rep = SeamlessDAGBFTFourRoundReconfigurationAndHakiCCTwoStageVerifiedCCProver.verify_and_synthesize_seamless_dag_bft_and_hakicc()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "stateless-recovery-bftide":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import StatelessRecoveryTightNormalFormAndBFTideLeaderlessSwitchingProver
            rep = StatelessRecoveryTightNormalFormAndBFTideLeaderlessSwitchingProver.verify_and_synthesize_stateless_recovery_and_bftide()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "multi-agent-budget-mcp-tfm":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import FaultTolerantMultiAgentEscrowBudgetConservationAndConcurrentProposerEquilibriumTFMProver
            rep = FaultTolerantMultiAgentEscrowBudgetConservationAndConcurrentProposerEquilibriumTFMProver.verify_and_synthesize_multi_agent_budget_conservation_and_concurrent_proposer_tfm()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "lifeline-vba-metadb-mvcc":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import LifelineMinimalSynchronyValidatedBAAndMetaDBTreeTopologyInMemoryMVCCProver
            rep = LifelineMinimalSynchronyValidatedBAAndMetaDBTreeTopologyInMemoryMVCCProver.verify_and_synthesize_lifeline_minimal_synchrony_vba_and_metadb_tree_mvcc()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "level400-fast-bft-proofsax":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import CentennialLevel400FastBFTSMRTwoDelayAndProofSaXShardedProofSynthesisProver
            rep = CentennialLevel400FastBFTSMRTwoDelayAndProofSaXShardedProofSynthesisProver.verify_and_synthesize_level400_fast_bft_smr_and_proofsax_sharding()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "adaptive-snapshots-mvba":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import AdaptiveSnapshotsVisibleReadLinearizabilityAndOptimalAdaptiveMultiValuedBAProver
            rep = AdaptiveSnapshotsVisibleReadLinearizabilityAndOptimalAdaptiveMultiValuedBAProver.verify_and_synthesize_adaptive_snapshots_and_optimal_adaptive_mvba()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "quadratic-adkg-qhi-llsc":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import QuadraticAsynchronousDKGPlainSetupAndQuiescentHistoryIndependentRandomizedLLSCProver
            rep = QuadraticAsynchronousDKGPlainSetupAndQuiescentHistoryIndependentRandomizedLLSCProver.verify_and_synthesize_quadratic_adkg_plain_setup_and_qhi_llsc()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "eaid-dispersal-lockfree-mtf":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import EAIDElasticAsynchronousInformationDispersalAndLockFreeMoveToFrontWorkingSetListProver
            rep = EAIDElasticAsynchronousInformationDispersalAndLockFreeMoveToFrontWorkingSetListProver.verify_and_synthesize_eaid_dispersal_and_lockfree_mtf_list()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "finwhale-dag-nonleaking-objects":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import FinWhaleTwoRoundTerminatingDAGAndEpistemicNonLeakingConcurrentObjectsProver
            rep = FinWhaleTwoRoundTerminatingDAGAndEpistemicNonLeakingConcurrentObjectsProver.verify_and_synthesize_finwhale_two_round_dag_and_epistemic_non_leaking_objects()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "lockfree-linear-probing-convex-agreement":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import SpaceEfficientLockFreeLinearProbingHashTableAndExtractorGraphConvexAgreementProver
            rep = SpaceEfficientLockFreeLinearProbingHashTableAndExtractorGraphConvexAgreementProver.verify_and_synthesize_lockfree_linear_probing_and_convex_agreement()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "responsive-validity-ba-general-adversary-mvba":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import ResponsiveByzantineAgreementValidityAndGeneralAdversaryMultivaluedConsensusProver
            rep = ResponsiveByzantineAgreementValidityAndGeneralAdversaryMultivaluedConsensusProver.verify_and_synthesize_responsive_ba_validity_and_general_adversary_mvba()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "subcubic-pkifree-coin-waitfree-fair-reconciliation":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import SubcubicPKIFreeAsynchronousCoinTossingAndWaitFreeFairReconciliationProver
            rep = SubcubicPKIFreeAsynchronousCoinTossingAndWaitFreeFairReconciliationProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "bounded-maximin-swap-stochastic-sweep-consensus":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import BoundedMaximinFairAtomicSwapAndStochasticBroadcastSweepConsensusProver
            rep = BoundedMaximinFairAtomicSwapAndStochasticBroadcastSweepConsensusProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "opinion-density-3majority-2choices-simplicial-agreement":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import OpinionDensity3Majority2ChoicesAndSimplicialApproximateAgreementProver
            rep = OpinionDensity3Majority2ChoicesAndSimplicialApproximateAgreementProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "lpmso-unbounded-degree-gap-sublinear-mpc-ncc":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import LPMSOUnboundedDegreeGapAndSublinearMPCNodeCapacitatedCliqueProver
            rep = LPMSOUnboundedDegreeGapAndSublinearMPCNodeCapacitatedCliqueProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "congest-vizing-edge-coloring-and-lfl-gaps":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import DeterministicCongestDeltaPlusOneEdgeColoringAndLocallyFiniteLabelingProver
            rep = DeterministicCongestDeltaPlusOneEdgeColoringAndLocallyFiniteLabelingProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "degree-splitting-hso-and-uniform-port-self-stabilization":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import DeterministicDegreeSplittingHSOAndUniformPortSelfStabilizationProver
            rep = DeterministicDegreeSplittingHSOAndUniformPortSelfStabilizationProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "node-edge-checkable-lcl-and-local-distributed-mechanisms":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import NodeEdgeCheckableLCLRobustnessAndLocalDistributedMechanismDesignProver
            rep = NodeEdgeCheckableLCLRobustnessAndLocalDistributedMechanismDesignProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "low-arboricity-2-ruling-sets-and-stable-parity-population":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import LowArboricityTwoRulingSetAndStableParityPopulationProtocolProver
            rep = LowArboricityTwoRulingSetAndStableParityPopulationProtocolProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "tree-intersection-leader-election-and-resilient-lll-coloring":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import TreeIntersectionLeaderElectionAndResilientLLLTriangleFreeColoringProver
            rep = TreeIntersectionLeaderElectionAndResilientLLLTriangleFreeColoringProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "bounded-degree-tree-population-and-average-anonymous-sb":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import BoundedDegreeTreePopulationProtocolAndAverageAnonymousNetworkSBProver
            rep = BoundedDegreeTreePopulationProtocolAndAverageAnonymousNetworkSBProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "hypergraph-simplex-enumeration-and-graph-population-counting":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import HypergraphTriangleSimplexEnumerationAndGraphPopulationCountingProver
            rep = HypergraphTriangleSimplexEnumerationAndGraphPopulationCountingProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "asymmetric-quorum-symmetry-compiler-and-multiword-swmr-space":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import AsymmetricQuorumSymmetryCompilerAndMultiWordSWMRRegisterSpaceProver
            rep = AsymmetricQuorumSymmetryCompilerAndMultiWordSWMRRegisterSpaceProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "sublinear-mpc-peeling-and-semisync-dynamic-exploration":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import SublinearMPCFixedThresholdPeelingAndSemiSyncDynamicGraphExplorationProver
            rep = SublinearMPCFixedThresholdPeelingAndSemiSyncDynamicGraphExplorationProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "discrete-token-distribution-and-fluctuating-sleepy-consensus":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import DiscreteTokenDistributionAndFluctuatingSleepyConsensusProver
            rep = DiscreteTokenDistributionAndFluctuatingSleepyConsensusProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "collective-communication-rate-and-sleeping-congest-dominating-set":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import CollectiveCommunicationRateAndSleepingCongestDominatingSetProver
            rep = CollectiveCommunicationRateAndSleepingCongestDominatingSetProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "weighted-beeping-network-and-quantum-local-tree-lcl-gap":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import WeightedBeepingNetworkLocalBroadcastAndQuantumLocalTreeLCLGapProver
            rep = WeightedBeepingNetworkLocalBroadcastAndQuantumLocalTreeLCLGapProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "infinite-sequential-consistency-and-stone-duality-colorless-computability":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import InfiniteSequentialConsistencyComplexityAndStoneDualityColorlessComputabilityProver
            rep = InfiniteSequentialConsistencyComplexityAndStoneDualityColorlessComputabilityProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "deterministic-congest-few-colors-edge-coloring-and-anonymous-dynamic-self-organization":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import DeterministicCongestFewColorsEdgeColoringAndAnonymousDynamicSelfOrganizationProver
            rep = DeterministicCongestFewColorsEdgeColoringAndAnonymousDynamicSelfOrganizationProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "parallel-discrete-frechet-distance-and-exponentially-fewer-bits-initialization":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import ParallelDiscreteFrechetDistanceAndExponentiallyFewerBitsInitializationProver
            rep = ParallelDiscreteFrechetDistanceAndExponentiallyFewerBitsInitializationProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "byzantine-agreement-with-predictions-and-accountable-monadbft":
            from dataclasses import asdict
            from aleph_core.verification.z3_prover import ByzantineAgreementWithPredictionsAndAccountableMonadBFTSpeculationProver
            rep = ByzantineAgreementWithPredictionsAndAccountableMonadBFTSpeculationProver.prove_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "byzantine-agreement-strong-efficiency-lower-bounds-and-planar-max-flow-dual-incision":
            from aleph_core.verification.z3_prover import ByzantineAgreementStrongEfficiencyLowerBoundsAndPlanarMaxFlowDualIncisionProver
            rep = ByzantineAgreementStrongEfficiencyLowerBoundsAndPlanarMaxFlowDualIncisionProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "sleeping-congest-energy-lower-bounds-and-noisy-pull-quasi-self-stabilizing-spreading":
            from aleph_core.verification.z3_prover import SleepingCongestEnergyLowerBoundsAndNoisyPullQuasiSelfStabilizingSpreadingProver
            rep = SleepingCongestEnergyLowerBoundsAndNoisyPullQuasiSelfStabilizingSpreadingProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "fast-tendermint-two-step-consensus-and-local-parity-certification-lcl-synthesizer":
            from aleph_core.verification.z3_prover import FastTendermintTwoStepConsensusAndLocalParityCertificationLCLSynthesizerProver
            rep = FastTendermintTwoStepConsensusAndLocalParityCertificationLCLSynthesizerProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "fast-tetrabft-semantic-lock-conflict-graph-and-fair-binding-smr":
            from aleph_core.verification.z3_prover import FastTetraBFTSemanticLockConflictGraphAndFairBindingHiddenStateSMRProver
            rep = FastTetraBFTSemanticLockConflictGraphAndFairBindingHiddenStateSMRProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "correlated-liquid-democracy-certified-paths-and-kwta-self-stabilization":
            from aleph_core.verification.z3_prover import CorrelatedLiquidDemocracyCertifiedPathAndSelfStabilizingKWTAProver
            rep = CorrelatedLiquidDemocracyCertifiedPathAndSelfStabilizingKWTAProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "partially-authenticated-byzantine-consensus-and-gcas-infinite-arrival-universal":
            from aleph_core.verification.z3_prover import PartiallyAuthenticatedByzantineConsensusAndGCASInfiniteArrivalUniversalProver
            rep = PartiallyAuthenticatedByzantineConsensusAndGCASInfiniteArrivalUniversalProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "conflict-free-mazurkiewicz-universal-and-prediction-phase-king-ba":
            from aleph_core.verification.z3_prover import ConflictFreeMazurkiewiczUniversalAndPredictionPhaseKingBAProver
            rep = ConflictFreeMazurkiewiczUniversalAndPredictionPhaseKingBAProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "balanced-subquadratic-async-common-coin-aba-and-overwrite-lattice-lfp":
            from aleph_core.verification.z3_prover import BalancedSubquadraticAsyncCommonCoinABAAndOverwriteLatticeLFPProver
            rep = BalancedSubquadraticAsyncCommonCoinABAAndOverwriteLatticeLFPProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "disperser-adaptive-byzantine-agreement-and-recursive-asynchronous-dkg":
            from aleph_core.verification.z3_prover import DisperserAdaptiveByzantineAgreementAndRecursiveAsynchronousDKGProver
            rep = DisperserAdaptiveByzantineAgreementAndRecursiveAsynchronousDKGProver.verify_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "circles-opinion-ranking-and-distributed-szk-sumcheck":
            from aleph_core.verification.z3_prover import (
                CirclesOpinionRankingAndDistributedSZKSumcheckProver,
            )
            rep = CirclesOpinionRankingAndDistributedSZKSumcheckProver.verify_and_repair()
            print(json.dumps(asdict(rep), indent=2))
            return (0 if rep.is_valid else 1)
        elif cmd == "generalized-mpx-graph-decomposition-matching-and-distributed-stochastic-graph-optimization":
            from aleph_core.verification.z3_prover import (
                GeneralizedMPXGraphDecompositionMatchingAndDistributedStochasticGraphProver,
            )
            rep = GeneralizedMPXGraphDecompositionMatchingAndDistributedStochasticGraphProver.verify_and_repair()
            print(json.dumps(asdict(rep), indent=2))
            return (0 if rep.is_valid else 1)
        elif cmd == "two-dimensional-matrix-avid-recovery-and-optimal-bounded-arboricity-dominating-set":
            from aleph_core.verification.z3_prover import (
                TwoDimensionalMatrixAVIDRecoveryAndBoundedArboricityDominatingSetProver,
            )
            rep = TwoDimensionalMatrixAVIDRecoveryAndBoundedArboricityDominatingSetProver.verify_and_repair()
            print(json.dumps(asdict(rep), indent=2))
            return (0 if rep.is_valid else 1)
        elif cmd == "small-message-graph-sketch-gossip-and-adversarial-majority-supervised-computing":
            from aleph_core.verification.z3_prover import (
                SmallMessageGraphSketchGossipAndAdversarialMajoritySupervisedComputingProver,
            )
            rep = SmallMessageGraphSketchGossipAndAdversarialMajoritySupervisedComputingProver.verify_and_repair()
            print(json.dumps(asdict(rep), indent=2))
            return (0 if rep.is_valid else 1)
        elif cmd == "early-stabilizing-byzantine-counting-and-practically-constant-local-skew-gcs":
            from aleph_core.verification.z3_prover import EarlyStabilizingByzantineCountingAndPracticallyConstantLocalSkewGCSProver
            prover = EarlyStabilizingByzantineCountingAndPracticallyConstantLocalSkewGCSProver()
            rep = prover.verify_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "subquadratic-byzantine-renaming-and-network-agnostic-multidimensional-approximate-agreement":
            from aleph_core.verification.z3_prover import SubquadraticByzantineRenamingAndNetworkAgnosticMultidimensionalApproximateAgreementProver
            prover = SubquadraticByzantineRenamingAndNetworkAgnosticMultidimensionalApproximateAgreementProver()
            rep = prover.verify_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "forget-it-constant-storage-bft-and-optimistic-information-theoretic-vss":
            from aleph_core.verification.z3_prover import ForgetITConstantStorageBFTAndOptimisticInformationTheoreticVSSProver
            rep = ForgetITConstantStorageBFTAndOptimisticInformationTheoreticVSSProver.verify_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "flutter-blink-fast-byzantine-tob-and-seniorlock-retrospective-waitfree":
            from aleph_core.verification.z3_prover import FlutterBlinkFastByzantineTOBAndSeniorLockRetrospectiveWaitFreeProver
            rep = FlutterBlinkFastByzantineTOBAndSeniorLockRetrospectiveWaitFreeProver.prove_and_repair()
            print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
        elif cmd == "near-optimal-parallel-m-matrix-scaling-and-byzantine-resilient-dflc-tacs-consensus":
            from aleph_core.verification.z3_prover import NearOptimalParallelMMatrixScalingAndByzantineResilientDFLCTACSConsensusProver
            rep = NearOptimalParallelMMatrixScalingAndByzantineResilientDFLCTACSConsensusProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "parallel-noisy-shallow-circuit-ac0-simulation-and-dcoco-parallel-draft-contextual-correction":
            from aleph_core.verification.z3_prover import ParallelNoisyShallowCircuitAC0AndDCOCOContextualCorrectionProver
            rep = ParallelNoisyShallowCircuitAC0AndDCOCOContextualCorrectionProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "mojos-batch-parallel-link-cut-euler-tour-trees-and-metadb-in-memory-mvcc":
            from aleph_core.verification.z3_prover import MOJOSBatchParallelLinkCutEulerTourTreesAndMetaDBInMemoryMVCCProver
            rep = MOJOSBatchParallelLinkCutEulerTourTreesAndMetaDBInMemoryMVCCProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "lachesis-lifetime-aware-kv-cache-hbm-hbf-and-monadically-dependent-fo-model-checking":
            from aleph_core.verification.z3_prover import LachesisLifetimeAwareKVCacheHBMHBFAndMonadicallyDependentFOModelCheckingProver
            rep = LachesisLifetimeAwareKVCacheHBMHBFAndMonadicallyDependentFOModelCheckingProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "fault-tolerant-delegation-dag-budget-conservation-and-acca-continuous-authorization":
            from aleph_core.verification.z3_prover import FaultTolerantDelegationDAGBudgetConservationAndACCAContinuousAuthorizationProver
            rep = FaultTolerantDelegationDAGBudgetConservationAndACCAContinuousAuthorizationProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "s2mr-serverless-disaggregated-smr-and-kairos-transactional-boundary-security":
            from aleph_core.verification.z3_prover import S2MRServerlessDisaggregatedSMRAndKairosTransactionalBoundarySecurityProver
            rep = S2MRServerlessDisaggregatedSMRAndKairosTransactionalBoundarySecurityProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "plume-rocq-mechanized-tap-read-atomicity-and-hakicc-conflict-serializable-cc":
            from aleph_core.verification.z3_prover import PlumeRocqMechanizedTAPReadAtomicityAndHakiCCConflictSerializableProtocolProver
            rep = PlumeRocqMechanizedTAPReadAtomicityAndHakiCCConflictSerializableProtocolProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "firstswap-preconsensus-quorum-admissibility-and-guarded-commits-transactional-approval":
            from aleph_core.verification.z3_prover import FirstSwapPreConsensusQuorumAdmissibilityAndGuardedCommitsTransactionalApprovalProver
            rep = FirstSwapPreConsensusQuorumAdmissibilityAndGuardedCommitsTransactionalApprovalProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "agent-state-footprint-semantic-conflict-and-zengram-lite-mvcc-cow-branching":
            from aleph_core.verification.z3_prover import AgentStateFootprintSemanticConflictAndZengramLiteMVCCCoWBranchingProver
            rep = AgentStateFootprintSemanticConflictAndZengramLiteMVCCCoWBranchingProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "pangolin-dag-bft-tee-commitment-and-cognitive-serializability-tct":
            from aleph_core.verification.z3_prover import PangolinDAGBFTTEECommitmentAndCognitiveSerializabilityTCTProver
            rep = PangolinDAGBFTTEECommitmentAndCognitiveSerializabilityTCTProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "vantage-availability-graded-broadcast-bft-and-shieldfs-authenticated-wal-cow":
            from aleph_core.verification.z3_prover import VantageAvailabilityGradedBroadcastBFTAndShieldFSAuthenticatedWALCoWProver
            rep = VantageAvailabilityGradedBroadcastBFTAndShieldFSAuthenticatedWALCoWProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "hydrozoan-latency-adaptive-dag-consensus-and-git4data-mvcc-branching":
            from aleph_core.verification.z3_prover import HydrozoanLatencyAdaptiveDAGConsensusAndGit4DataMVCCBranchingProver
            rep = HydrozoanLatencyAdaptiveDAGConsensusAndGit4DataMVCCBranchingProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "veriprotocol-roundtick-consensus-time-semantics-and-augur-view-serializability":
            from aleph_core.verification.z3_prover import VeriProtocolRoundTickConsensusTimeSemanticsAndAugurViewSerializabilityProver
            rep = VeriProtocolRoundTickConsensusTimeSemanticsAndAugurViewSerializabilityProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "barnacle-adaptive-multileader-dag-consensus-and-zetalite-logcentric-mvcc":
            from aleph_core.verification.z3_prover import BarnacleAdaptiveMultiLeaderDAGConsensusAndZetaLiteLogCentricMVCCProver
            rep = BarnacleAdaptiveMultiLeaderDAGConsensusAndZetaLiteLogCentricMVCCProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "parallel-task-multiple-cluster-scheduling-and-generic-simplex-view-agreement-consensus":
            from aleph_core.verification.z3_prover import ParallelTaskMultipleClusterSchedulingAndGenericSimplexViewAgreementConsensusProver
            rep = ParallelTaskMultipleClusterSchedulingAndGenericSimplexViewAgreementConsensusProver.verify_and_synthesize()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == "parallel-ldd-spectral-sparsification-and-deterministic-mpc-distance-hitting-sets":
            from aleph_core.verification.z3_prover import ParallelLDDSpectralSparsificationAndDeterministicMPCDistanceHittingSetsProver
            rep = ParallelLDDSpectralSparsificationAndDeterministicMPCDistanceHittingSetsProver().verify_and_repair()
            print(json.dumps(asdict(rep), indent=2, ensure_ascii=False))
        elif cmd == 'scim2-rfc7644-fedcm-aigateway-ssrf-audit' and len(sys.argv) > 2:
            return (cmd_scim2_rfc7644_fedcm_aigateway_ssrf_audit(sys.argv[2]))
        elif cmd == 'scim2-externalid-idor-fedcm-litellm-cve2026-59823-audit' and len(sys.argv) > 2:
            return (cmd_scim2_externalid_idor_fedcm_litellm_cve2026_59823_audit(sys.argv[2]))
        elif cmd == 'scim2-temporal-ac2-jwt-cve2024-54150-fedcm-litellm-testconn-audit' and len(sys.argv) > 2:
            return (cmd_scim2_temporal_ac2_jwt_cve2024_54150_fedcm_litellm_testconn_audit(sys.argv[2]))
        elif cmd == 'tls13-rfc9846-vllm-cve2026-24779-bentoml-cve2026-44345-audit' and len(sys.argv) > 2:
            return (cmd_tls13_rfc9846_vllm_cve2026_24779_bentoml_cve2026_44345_audit(sys.argv[2]))
        elif cmd == 'privacypass-batched-ollama-cve2026-108836-mlrun-cve2026-92568-audit' and len(sys.argv) > 2:
            return (cmd_privacypass_batched_ollama_cve2026_108836_mlrun_cve2026_92568_audit(sys.argv[2]))
        elif cmd == 'mls-rfc9750-cbor-cde-http2-origin-grafana-ssrf-audit' and len(sys.argv) > 2:
            return (cmd_mls_rfc9750_cbor_cde_http2_origin_grafana_ssrf_audit(sys.argv[2]))
        elif cmd == 'mcp-contextforge-toctou-surrealdb-langflow-koa-cve2026-27959-audit' and len(sys.argv) > 2:
            return (cmd_mcp_contextforge_toctou_surrealdb_langflow_koa_cve2026_27959_audit(sys.argv[2]))
        elif cmd == 'kong-cve2026-17578-autojack-contextforge-ssti-vaultwarden-ssrf-audit' and len(sys.argv) > 2:
            return (cmd_kong_cve2026_17578_autojack_contextforge_ssti_vaultwarden_ssrf_audit(sys.argv[2]))
        elif cmd == 'eat-rfc9711-mlflow-cve2026-64849-qdrant-cve2024-3829-audit' and len(sys.argv) > 2:
            return (cmd_eat_rfc9711_mlflow_cve2026_64849_qdrant_cve2024_3829_audit(sys.argv[2]))
        elif cmd == 'mldsa-connolly-sframe-langflow-cve2025-3248-jupyter-envoy-audit' and len(sys.argv) > 2:
            return (cmd_mldsa_connolly_sframe_langflow_cve2025_3248_jupyter_envoy_audit(sys.argv[2]))
        elif cmd == 'gocontainerregistry-ipv6-ssrf-dirac-cve2026-61668-dynaconf-ssti-audit' and len(sys.argv) > 2:
            return (cmd_gocontainerregistry_ipv6_ssrf_dirac_cve2026_61668_dynaconf_ssti_audit(sys.argv[2]))
        elif cmd == 'rivet-ppr-tidekv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'rivet_ppr_tidekv_cluster'
            res = engine.prove_rivet_utility_preserving_repo_ppr_and_tidekv_chunked_prefill(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'inlinecoder-fastkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'inlinecoder_fastkv_cluster'
            res = engine.prove_inlinecoder_bidirectional_callgraph_and_fastkv_behavior_preserving(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'hydra-crosstoken-kv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'hydra_crosstoken_kv_cluster'
            res = engine.prove_hydra_hierarchical_repo_index_and_crosstoken_kv_prefetch(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'saracoder-novakv-gsrq':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'saracoder_novakv_gsrq_cluster'
            res = engine.prove_saracoder_hierarchical_context_pruning_and_novakv_gsrq(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'adabool-selfindex-sign':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'adabool_selfindex_sign_cluster'
            res = engine.prove_adabool_adaptive_sparse_reachability_and_self_indexing_sign_attention(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'mojos-retroinfer-wave':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'mojos_retroinfer_wave_cluster'
            res = engine.prove_mojos_batch_parallel_dynamic_trees_and_retroinfer_wave_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'alpha-independent-ppr-sals':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'alpha_independent_ppr_sals_cluster'
            res = engine.prove_alpha_independent_recursive_active_set_ppr_and_sals_latent_prerope_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'adaptive-graph-yoio':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'adaptive_graph_yoio_cluster'
            res = engine.prove_adaptive_graph_edgetype_ppr_and_yoio_shared_index_sparse_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'chebpush-eta-deferkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'chebpush_eta_deferkv_cluster'
            res = engine.prove_chebpush_subset_recurrence_ppr_and_eta_shifted_silu_deferkv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'pdg-trigraph-commvq':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'pdg_trigraph_commvq_cluster'
            res = engine.prove_partial_dependency_trigraph_ppr_and_attention_preserving_commvq(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'reposcope-thinkv-randattn':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'reposcope_thinkv_randattn_cluster'
            res = engine.prove_reposcope_callchain_multiview_cha_ppr_and_thinkv_random_attention(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'dkb-crosscoder-qjl-infokv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'dkb_crosscoder_qjl_infokv_cluster'
            res = engine.prove_deterministic_ast_interface_graph_ppr_and_qjl_zero_metadata_infokv_lcdf(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'saga-workflow-oscar-int2':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'saga_workflow_oscar_int2_cluster'
            res = engine.prove_saga_atomic_workflow_callsite_transform_ppr_and_oscar_spectral_int2_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'draco-longcodezip-abridgekv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'draco_longcodezip_abridgekv_cluster'
            res = engine.prove_draco_dataflow_topological_longcodezip_ppr_and_abridgekv_pause_nested_routing(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'arise-featlens-still-hysparse2':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'arise_featlens_still_hysparse2_cluster'
            res = engine.prove_arise_intraprocedural_kgcompass_featlens_ppr_and_still_perceiver_hysparse2_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'aircoder-recalkv-kvlinc':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'aircoder_recalkv_kvlinc_cluster'
            res = engine.prove_aircoder_procc_bandit_multiview_ppr_and_recalkv_hsr_kvlinc_leverage(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'dycoder-puzzlekv-starkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'dycoder_puzzlekv_starkv_cluster'
            res = engine.prove_dycoder_codemem_partial_dep_graph_ppr_and_puzzlekv_starkv_deferkv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'ranger-sac-residualkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'ranger_sac_residualkv_cluster'
            res = engine.prove_ranger_dualpath_cypher_mcts_ppr_and_sac_cxl_residualkv_contiguouskv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'livecoder-repo0-eager-sekv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'livecoder_repo0_eager_sekv_cluster'
            res = engine.prove_livecoder_repo0_dualdag_ppr_and_eager_sekv_s3attention(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'fastcode-locagent-lrkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'fastcode_locagent_lrkv_cluster'
            res = engine.prove_fastcode_locagent_scouting_graph_ppr_and_lrkv_paged_eviction(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'rpg-gala-mlra-turboquant':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'rpg_gala_mlra_turboquant_cluster'
            res = engine.prove_rpg_encoder_gala_multimodal_graph_ppr_and_mlra_4way_tp_belt_turboquant(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'skillforge-lycheedecode-tsa':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'skillforge_lycheedecode_tsa_cluster'
            res = engine.prove_skillforge_codecraft_hcgs_graph_ppr_and_lycheedecode_hardkuma_token_sparse(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'acquire-codegraph-s4r-hylra':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'acquire_codegraph_s4r_hylra_cluster'
            res = engine.prove_acquire_codegraph_wikidata_ppr_and_s4r_subspace_hylra_layer_reuse(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'sweagile-seerepo-fastkvzip-heterocache':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'sweagile_seerepo_fastkvzip_heterocache_cluster'
            res = engine.prove_sweagile_seerepo_denovoswe_graph_ppr_and_fastkvzip_heterocache_ojakv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'steer-fafim-spla-grkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'steer_fafim_spla_grkv_cluster'
            res = engine.prove_steer_critic_fafim_triage_pdg_and_spla_residual_linear_grkv_kvreviver(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'schrodinger-abtest-residualkv-kqsvd':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'schrodinger_abtest_residualkv_kqsvd_cluster'
            res = engine.prove_schrodinger_repo_abtest_sweatscale_and_residualkv_kqsvd_closed_form(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'scaleswe-trimkv-expected-attn':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'scaleswe_trimkv_expected_attn_cluster'
            res = engine.prove_scaleswe_noop_ablation_audit_and_trimkv_expected_attention_encoder_heal(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'codespecweave-hybridgym-wgkv-xkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'codespecweave_hybridgym_wgkv_xkv_cluster'
            res = engine.prove_codespecweave_hybridgym_propel_and_wgkv_admission_cross_layer_xkv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'sweevo-unique-blasst':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'sweevo_antislop_unique_blasst_cluster'
            res = engine.prove_sweevo_monitor_antislop_cleanup_and_unique_page_mean_std_blasst_softmax(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'prometheus-repoprobe-depthweave-dropkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'prometheus_repoprobe_depthweave_dropkv_cluster'
            res = engine.prove_prometheus_repoprobe_checklist_and_depthweavekv_dropkv_cone(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'sweexplore-jssa-oasiskv-spectrumkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'sweexplore_depthgee_jssa_oasiskv_spectrumkv_cluster'
            res = engine.prove_sweexplore_depthgee_multihop_and_jssa_gatherfree_oasiskv_spectrumkv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'hermes-fathom-programmablekv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'hermes_fathom_programmable_kv_cluster'
            res = engine.prove_hermes_dev_primitives_dynamic_activation_and_fathom_bitplane_programmable_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'autocompact-swetrace-jointkv-pikv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'autocompact_swetrace_grade_jointkv_pikv_cluster'
            res = engine.prove_autocompact_swetrace_grade_and_joint_kv_block_encoding_pikv_moe(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'repomirage-sweatlas-kvdrive-rabitqcache':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'repomirage_sweatlas_kvdrive_rabitqcache_cluster'
            res = engine.prove_repomirage_sweatlas_perturbation_and_kvdrive_multitier_rabitqcache(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'gagar-codescout-thinkeys-twinkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'gagar_codescout_thinkeys_twinkv_cluster'
            res = engine.prove_gagar_codescout_advantage_redistribution_and_thinkeys_twinkv_minimax(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'agenticperf-csa2fp4-jacap-phase':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'agenticperf_csa2fp4_jacap_phase_cluster'
            res = engine.prove_agentic_perf_pr_validation_and_csa2_fp4_bounded_replay_jacap_phase(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'reponavigator-tooltrain-atma-skis':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'reponavigator_tooltrain_atma_skis_cluster'
            res = engine.prove_reponavigator_tooltrain_deep_search_and_atma_polar_gated_delta_skis(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'promax-sweprime-leyline-longflow-epikv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'promax_sweprime_leyline_longflow_epikv_cluster'
            res = engine.prove_swebench_promax_sweprime_and_leyline_rope_splice_longflow_epikv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'akv-river-kvcompass-hla-confkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'akv_river_kvcompass_hla_confkv_cluster'
            res = engine.prove_akv_cache_engineering_river_terminal_and_kvcompass_hla_confkv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'execcritic-cxi-certifiedsparse-e8-cmm':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'execcritic_cxi_certified_sparse_e8_ksa_cmm_cluster'
            res = engine.prove_execcritic_cxi_integrity_and_certified_sparse_e8_lattice_ksa_cmm(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'exlabel-swetq-semkv-qevict-nvm-fractal':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'exlabel_swetq_semkv_qevict_nvm_fractal_cluster'
            res = engine.prove_exlabel_swetq_and_semkv_quality_cliff_qevict_nvm_fractal(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'traceeval-convergence-momentkv-riskkv-indexmem':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'traceeval_convergence_momentkv_risk_indexmem_cluster'
            res = engine.prove_traceeval_convergence_audit_and_momentkv_risk_controlled_indexmem(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'swescience-prometheus-jevmem-intentkv-rksc':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'swescience_prometheus_jevmem_intentkv_rksc_cluster'
            res = engine.prove_swescience_prometheus_and_jevmem_intentkv_rksc(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'openswetraces-reasonalloc-tangram-redknot':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'openswetraces_reasonalloc_tangram_redknot_cluster'
            res = engine.prove_openswetraces_swehero_and_reasonalloc_tangram_redknot_segpaged(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'p2t-swemaster-redknotmla-vase-momentkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'p2t_swemaster_redknot_mla_vase_momentkv_cluster'
            res = engine.prove_p2t_swemaster_and_redknot_mla_vase_momentkv_pariskv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'repoatlas-semnav-sherloc-a2agent-tierkv-hierasparse':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'repoatlas_semnav_sherloc_a2agent_tierkv_hierasparse_cluster'
            res = engine.prove_repoatlas_semnav_and_sherloc_a2agent_tierkv_hierasparse(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'blagent-effiholmes-loc2repair-rdkv-pbkv-dgap':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'blagent_effiholmes_loc2repair_rdkv_pbkv_dgap_innerq_cluster'
            res = engine.prove_blagent_effiholmes_loc2repair_and_rdkv_pbkv_dgap_innerq(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'kvboost-restkv-laprox-kvgov-issueloc-themis':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'kvboost_restkv_laprox_kvgov_issueloc_themis_cluster'
            res = engine.prove_kvboost_restkv_laprox_and_kvgov_provenance_issueloc_themis(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'fusesearch-tdad-trajeval-mixeddimkv-moend':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'fusesearch_tdad_trajeval_mixeddimkv_moend_cluster'
            res = engine.prove_fusesearch_tdad_trajeval_and_mixeddimkv_moend_certified_qattn(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'sweadept-depthgee-suffixreplay-breadthkv-wakman':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'swe_adept_depthgee_suffix_replay_breadthkv_wakman_cluster'
            res = engine.prove_swe_adept_depthgee_suffix_replay_and_breadthkv_wakman(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'recap-issueexec-amomp-ratequant-rustcompcert':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'recap_issueexec_am_omp_ratequant_rustcompcert_cluster'
            res = engine.prove_recap_issueexec_attention_matching_and_ratequant_rustcompcert(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'spaderig-rrevict-c2kv-kvlearn-lukv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'spade_rig_rrevict_c2kv_kvlearn_lukv_cluster'
            res = engine.prove_spade_rig_rr_evict_c2kv_and_kvlearn_lukv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'codenib-cacheslide-concatrecompute-qkvshare':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'codenib_cacheslide_concatrecompute_qkvshare_cluster'
            res = engine.prove_codenib_cacheslide_concat_recompute_and_qkvshare(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'cakeir-kvcmas-kvcomm-swemilestone-doublep':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'cakeir_kvcmas_kvcomm_swemilestone_doublep_cluster'
            res = engine.prove_cake_ir_kvcmas_kvcomm_swemilestone_and_doublep(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'polykv-adaptivehuffman-e2eswe-llm4cov':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'polykv_adaptive_huffman_kv_e2eswe_llm4cov_cluster'
            res = engine.prove_polykv_adaptive_huffman_kv_and_e2e_swe_llm4cov(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'tokendance-relaycaching-lragent-harnessrsi':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'tokendance_relaycaching_lragent_harnessrsi_cluster'
            res = engine.prove_tokendance_relaycaching_lragent_and_harness_rsi(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'contextsniper-ctrepair-refuntangle-swereview-phasekv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'contextsniper_ctrepair_refuntangle_swereview_phasekv_cluster'
            res = engine.prove_contextsniper_ctrepair_refuntangle_swereview_and_phase_kv_abstention(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'coharden-stair-testgrad-montecarlokv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'coharden_patchfusion_stair_testgrad_lorekv_faithfulness_cluster'
            res = engine.prove_coharden_stair_testgrad_and_montecarlo_kv_quant_faithfulness(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'desc2fix-grapheng-hasa-tracedllmkvq':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'desc2fix_grapheng_hasa_trace_dllm_kvq_cluster'
            res = engine.prove_desc2fix_grapheng_hasa_and_trace_dllm_kvq(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'acrouter-harnessadapt-mlafication-zipfusion':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'acrouter_harnessadapt_swebenchpro_mlafication_zipfusion_cluster'
            res = engine.prove_acrouter_harnessadapt_swebenchpro_mlafication_and_zipfusion(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'cachescout-yasa-probe-depwaretrans-rcllm':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'cachescout_yasa_probe_depwaretrans_rcllm_kv_cluster'
            res = engine.prove_cachescout_yasa_probe_depwaretrans_and_rcllm_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'curaloc-salt-cpygraph-memuse-flashkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'curaloc_salt_cpygraph_memuse_flashkv_cluster'
            res = engine.prove_curaloc_salt_cpygraph_memuse_and_flash_kv_offload(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'deskcheck-graph2env-typify-typepro-recube-pltkv':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'deskcheck_graph2env_typify_typepro_recube_pltkv_cluster'
            res = engine.prove_deskcheck_graph2env_typify_typepro_recube_and_plt_kv(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'codecomp-efficientagent-cachewise-rustmir-vericache':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'codecomp_efficientagent_cachewise_rustmir_vericache_rift_cluster'
            res = engine.prove_codecomp_efficientagent_cachewise_rustmir_and_vericache_rift(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'kvfetch-kara-kapilot-trust-flcontext':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'kvfetch_kara_kapilot_trust_fl_context_cluster'
            res = engine.prove_kvfetch_kara_kapilot_trust_and_fl_context(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'aegisasync-swepruner-kvcat-kvcodec-rustoracle':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'aegisasync_swepruner_kvcat_kvcodec_rust_oracle_cluster'
            res = engine.prove_aegisasync_swepruner_kvcat_kvcodec_and_rust_unsafe_oracle(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'tracelite-sweedit-bascet-rust-kvtc':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'tracelite_sweedit_bascet_rust_kvtc_ml_quality_cluster'
            res = engine.prove_tracelite_sweedit_bascet_rust_kvtc_and_ml_quality(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'devskills-kvfact-terminaluniverse-gdn':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'devskills_kvfact_terminal_universe_gdn_cluster'
            res = engine.prove_devskills_kvfact_masking_terminal_universe_and_gdn_handoff(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'coharl-qsa-sga-ropeprofiler-cavespine':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'coharl_qsa_sga_rope_profiler_cave_spine_cluster'
            res = engine.prove_coharl_qsa_sga_rope_profiler_and_cave_assurance_spine(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'dge-colgrep-xagent-unsafechecker-tmax':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'dge_kv_colgrep_xagent_rust_unsafechecker_tmax_cluster'
            res = engine.prove_dge_kv_colgrep_xagent_rust_unsafechecker_and_tmax(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'tidekv-aatc-semnav-easyprover-corten-swecc':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'tidekv_aatc_semnav_easyprover_corten_swecc_cluster'
            res = engine.prove_tidekv_aatc_semnav_easyprover_aegis_corten_rust_async_and_swe_cc(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'page-minimakv-cabra-forte-aeneas-verus':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'page_minimakv_cabra_forte_aeneas_verus_cluster'
            res = engine.prove_page_minimakv_cabra_callgraph_forte_rust_and_aeneas_lean_verus(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'valuediff-multialloc-ripplekv-chronos-c2rust':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'valuediff_multialloc_ripplekv_chronos_c2rust_cluster'
            res = engine.prove_valuediff_multialloc_ripplekv_selkv_chronos_and_c2rust_security(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'blockgtq-mosaickv-patchperf-rustgo-kani':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'blockgtq_mosaickv_patchperf_rustgo_kani_cluster'
            res = engine.prove_blockgtq_mosaickv_patch_perf_anova_rustgo_and_kani_mir(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'twinkv-rustc-schwarz-harnessllm-testgrad-swetaskflow':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'twinkv_rustc_schwarz_harnessllm_testgrad_swetaskflow_cluster'
            res = engine.prove_twinkv_rustc_schwarz_harnessllm_testgrad_and_swetaskflow(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'alerus-rustgpu-queryvis-race-pnmix-asner-isorag':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'alerus_rustgpu_queryvis_race_pnmix_asner_isorag_cluster'
            res = engine.prove_alerus_rust_gpu_offload_query_visibility_race_pnmix_and_asner_isorag(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'patchkv-slimkv-kpa-tasq-localppr-agint-adarepair-rust':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'patchkv_slimkv_kpa_tasq_localppr_agint_adarepair_rust_cluster'
            res = engine.prove_patchkv_slimkv_kpa_tasq_local_ppr_agint_and_adarepair_rust(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'vericontest-lean-veruseval-tlaverus-vestigekv-gva-smem-eirwr':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'vericontest_lean_veruseval_tlaverus_vestigekv_gva_smem_eirwr_cluster'
            res = engine.prove_vericontest_lean_veruseval_tlaverus_vestigekv_gva_smem_and_eirwr(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'prefixacc-cachecraft-hyquant-activesetppr-petrirust-tqs':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'prefixacc_cachecraft_hyquant_activesetppr_petrirust_tqs_cluster'
            res = engine.prove_prefix_accounting_cachecraft_frc_hyquant_activeset_ppr_petri_rust_and_tqs(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'foldedbiaskey-sur-residualquant-pulseinfer-dquant-reponav':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'foldedbiaskey_sur_residualquant_pulseinfer_dquant_reponav_cluster'
            res = engine.prove_folded_bias_key_sur_repair_residualquant_pulseinfer_dquant_and_reponav(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'ramnet-crossmodelkv-headguard-kvec-starkv-humanize-feynrir-crosscoder':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'ramnet_crossmodelkv_headguard_kvec_starkv_humanize_feynrir_crosscoder_cluster'
            res = engine.prove_ramnet_crossmodel_kv_headguard_kvec_starkv_humanize_feynrir_and_crosscoder(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'ulacache-oval-relaxkv-bytecrossover-hisparse-graft-edge':
            engine = AlephEngine()
            tgt = sys.argv[2] if len(sys.argv) > 2 else 'ulacache_oval_relaxkv_bytecrossover_hisparse_graft_edge_cluster'
            res = engine.prove_ulacache_oval_relaxkv_byte_crossover_hisparse_graft_rust_and_edge_callgraph(target_name=tgt)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'deferkv-crossflow-heterofold-decodebranch-optr-kvprov-graml-grads':
            engine = AlephEngine()
            res = engine.prove_deferkv_crossflow_heterofold_decodebranch_optr_kvprovenance_graml_and_grads()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'acache-conduit-kvsharearena-hijackkv-kvgov-mags-sweadv-interdepspec-repograph':
            engine = AlephEngine()
            res = engine.prove_acache_conduit_kvsharearena_hijackkv_kvgov_mags_sweadv_interdepspec_and_repograph()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'netkv-prefilldeflect-pcr-regimekv-topas-memdraftsd-peekkv-kvstream-cslibpremise-retrace':
            engine = AlephEngine()
            res = engine.prove_netkv_prefilldeflect_pcr_regimekv_topas_memdraftsd_peekkv_kvstream_cslibpremise_and_retrace()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'herald-3dls-eldr-aoh-circuitprover-cocoprover-formalreward-paichecker-dialogueswe-procgrep':
            engine = AlephEngine()
            res = engine.prove_herald_3dls_eldr_aoh_circuitprover_cocoprover_formalreward_paichecker_dialogueswe_and_procgrep()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'hexagent-topomove-ainferpd-pdd-rarecache-blis-vericodebench-dalekbench-reuf2f-calcg':
            engine = AlephEngine()
            res = engine.prove_hexagent_topomove_ainferpd_pdd_rarecache_blis_vericodebench_dalekbench_reuf2f_and_calcg()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'specstream-hspec-groupkv-exfold-elasticvmm-vha-rcsd-p3lean4-hyperflconfl-omegadafny':
            engine = AlephEngine()
            res = engine.prove_specstream_hspec_groupkv_exfold_elasticvmm_vha_rcsd_p3lean4_hyperflconfl_and_omegadafny()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        elif cmd == 'specla-sparsespecl-moezip-slimwise-foldattention-witcert-axdafny-openprover-leaf-pprcgdiff':
            engine = AlephEngine()
            res = engine.prove_specla_sparsespecl_moezip_slimwise_foldattention_witcert_axdafny_openprover_leaf_and_pprcgdiff()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return (0 if res.get('passed', False) else 1)
        return None
    finally:
        sys.argv = old_argv
