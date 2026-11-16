"""Aleph Core Library Package (Unified `.aleph/lib` exports)."""
from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import (
        aleph_compiler_html,
        aleph_compiler_react,
        aleph_design_critic,
        aleph_design_facade,
        aleph_design_ir,
        aleph_direction_engine,
        aleph_kinetic_ode,
        aleph_mcp_server,
        aleph_omega_facade,
        aleph_render_oracle,
        aleph_shader_compiler,
        aleph_smt_layout_verifier,
        aleph_token_compiler,
        aleph_visual_stage_synthesizer,
        v5_aeos_kernel,
        v5_blackboard_squads,
        v5_context_cache,
        v5_goal_loop_tdd,
        v5_sentinel_tooling,
        v5_skill_security,
        v5_skills_router,
        v5_uar_harness,
        v6_battle_harness,
        v6_flash_executor,
        v6_native_bridge,
        v7_mmap_skill_compiler,
        v7_mmap_skill_router,
    )

_EXPORTED_MODULES = (
    "aleph_compiler_html",
    "aleph_compiler_react",
    "aleph_design_critic",
    "aleph_design_facade",
    "aleph_design_ir",
    "aleph_direction_engine",
    "aleph_kinetic_ode",
    "aleph_mcp_server",
    "aleph_omega_facade",
    "aleph_render_oracle",
    "aleph_shader_compiler",
    "aleph_smt_layout_verifier",
    "aleph_token_compiler",
    "aleph_visual_stage_synthesizer",
    "v5_aeos_kernel",
    "v5_blackboard_squads",
    "v5_context_cache",
    "v5_goal_loop_tdd",
    "v5_sentinel_tooling",
    "v5_skill_security",
    "v5_skills_router",
    "v5_uar_harness",
    "v6_battle_harness",
    "v6_flash_executor",
    "v6_native_bridge",
    "v7_mmap_skill_compiler",
    "v7_mmap_skill_router",
)


def __getattr__(name: str):
    if name in _EXPORTED_MODULES:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_EXPORTED_MODULES)
