"""Modulo visual diferido de El Aleph (Playwright se importa lazy solo al auditar)."""

from aleph_core.visual.browser_auditor import VisualAuditReport, VisualBrowserAuditor, audit_visual_target

__all__ = ["VisualAuditReport", "VisualBrowserAuditor", "audit_visual_target"]
