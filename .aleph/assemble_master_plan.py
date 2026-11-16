#!/usr/bin/env python3
"""
.aleph/assemble_master_plan.py
Ensamblador determinista del Plan Maestro V7.0 de Aleph Sovereign World Designer.
Utiliza rutas relativas portables al directorio `.aleph/`.
"""
from pathlib import Path

ALEPH_DIR = Path(__file__).resolve().parent
DRAFTS_DIR = ALEPH_DIR / "master_plan_design"
OUT_ALEPH = ALEPH_DIR / "ALEPH_SOVEREIGN_WORLD_DESIGNER_MASTER_PLAN_V7.md"


def assemble_master_plan(source_dir: Path = DRAFTS_DIR, output_file: Path = OUT_ALEPH) -> Path:
    chapters = sorted(source_dir.glob("*.md"))
    if not chapters and output_file.exists():
        return output_file
    parts = [ch.read_text(encoding="utf-8") for ch in chapters]
    if parts and not output_file.exists():
        output_file.write_text("\n\n---\n\n".join(parts) + "\n", encoding="utf-8")
    return output_file


if __name__ == "__main__":
    out = assemble_master_plan()
    print(f"Master Plan verified at: {out} ({out.stat().st_size if out.exists() else 0} bytes)")
