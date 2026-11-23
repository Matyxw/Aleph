"""Rutas de importación uniformes y aislamiento frente a ~/.aleph para los tests de .aleph/ (unittest y pytest)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

_ALEPH = Path(__file__).resolve().parent.parent
_ROOT = _ALEPH.parent


def isolate_repo_dot_aleph() -> None:
    """Prioriza las rutas locales de este repositorio y neutraliza ~/.aleph global."""
    os.environ["ALEPH_HOME"] = str(_ALEPH)
    aleph_resolved = _ALEPH.resolve()
    home_aleph = (Path.home() / ".aleph").resolve()

    def _under(candidate: str, root: Path) -> bool:
        try:
            res = Path(candidate).resolve()
        except OSError:
            return False
        return res == root or root in res.parents

    preferred = [
        str(_ROOT),
        str(_ALEPH),
        str(_ALEPH / "lib"),
        str(_ALEPH / "v4_engine"),
        str(_ALEPH / "scripts"),
        str(_ALEPH / "hooks"),
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

try:
    import pytest  # type: ignore
except ImportError:
    pytest = None  # type: ignore


def _chromium_or_playwright_disponible() -> bool:
    """True si Python Playwright+Chromium, Chromium/Selenium CDP o Node Playwright están disponibles."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            exe = pw.chromium.executable_path
            if exe and os.path.isfile(exe):
                return True
    except Exception:
        pass
    try:
        import selenium  # noqa: F401
        if shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome"):
            return True
    except ImportError:
        pass
    node = shutil.which("node")
    if not node:
        return False
    try:
        r = subprocess.run(
            [node, "--input-type=module", "-e", "await import('playwright')"],
            cwd=str(_ALEPH), capture_output=True, timeout=20,
        )
        return r.returncode == 0
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if pytest is None or _chromium_or_playwright_disponible():
        return
    skip = pytest.mark.skip(
        reason="requiere Chromium+Selenium o Playwright+Chromium"
    )
    for item in items:
        if item.fspath.basename == "test_aleph_live_oracle.py" and "live" in item.name.lower():
            item.add_marker(skip)
