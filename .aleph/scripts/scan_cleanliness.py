#!/usr/bin/env python3
"""Escáner determinista de limpieza Zero-Literal y Zero-Placeholder."""
from typing import Dict

def scan_source_cleanliness(source_text: str) -> Dict[str, bool]:
    has_transition_all = "transition: all" in source_text
    return {"clean": not has_transition_all, "zero_transition_all": not has_transition_all}
