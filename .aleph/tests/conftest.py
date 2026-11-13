"""Configuración compartida de pytest para .aleph/tests: garantiza aislamiento del repo frente a ~/.aleph."""
import os
from pathlib import Path
import sys


def isolate_repo_dot_aleph() -> None:
    """Prioriza las rutas locales de este repositorio y neutraliza variables globales ~/.aleph."""
    aleph_dir = Path(__file__).resolve().parent.parent
    repo_root = aleph_dir.parent
    os.environ["ALEPH_HOME"] = str(aleph_dir)

    aleph_resolved = aleph_dir.resolve()
    home_aleph = (Path.home() / ".aleph").resolve()

    def _under(candidate: str, root: Path) -> bool:
        try:
            res = Path(candidate).resolve()
        except OSError:
            return False
        return res == root or root in res.parents

    preferred = [
        str(repo_root),
        str(aleph_dir),
        str(aleph_dir / "lib"),
        str(aleph_dir / "scripts"),
        str(aleph_dir / "hooks"),
    ]
    preferred_resolved = {Path(p).resolve() for p in preferred}

    cleaned = []
    for entry in sys.path:
        if home_aleph != aleph_resolved and entry and _under(entry, home_aleph):
            continue
        try:
            if entry and Path(entry).resolve() in preferred_resolved:
                continue
        except OSError:
            pass
        cleaned.append(entry)
    sys.path[:] = preferred + cleaned

    for mod_name in list(sys.modules):
        top = mod_name.split(".")[0]
        if top not in {"lib", "scripts", "hooks", "v4_engine"}:
            continue
        mod = sys.modules.get(mod_name)
        mod_file = getattr(mod, "__file__", None)
        if mod_file and not _under(mod_file, aleph_resolved):
            del sys.modules[mod_name]
            continue
        mod_paths = getattr(mod, "__path__", None)
        if mod_paths and any(not _under(str(p), aleph_resolved) for p in mod_paths):
            del sys.modules[mod_name]


isolate_repo_dot_aleph()
