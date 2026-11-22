"""
aleph_core/sandbox/driver.py
Sandbox Soberano Pluggable de Ejecución Desatendida (Superación de OpenHands).
Soporta:
1. DockerSandboxDriver (isolation_tier="DOCKER_CONTAINER"): --network none, límites CPU/RAM/PIDs, docker kill garantizado.
2. IsolatedWorktreeProcessDriver (isolation_tier="PROCESS_WORKTREE"): git worktree efímero en disco,
   aislamiento estricto de HOME/TMP/TEMP y bloqueo total de secretos del host, pre-chequeo AegisShield y
   terminación dura de árbol de procesos (taskkill /F /T /PID en Windows).
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from aleph_core.security.aegis_shield import AegisShield


SAFE_HOST_ENV_ALLOWLIST = frozenset({
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "PATH",
    "OS",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_IDENTIFIER",
    "LANG",
    "LC_ALL",
})

_SECRET_ENV_KEY_RE = re.compile(r"(?:SECRET|TOKEN|API_KEY|_KEY|PASSWORD|PASSWD|CREDENTIAL|PRIVATE)", re.IGNORECASE)


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    isolation_tier: str
    timed_out: bool
    killed_processes: int
    artifacts_cas_sha256: str
    command: str
    worktree_clean: bool = True
    blocked_by_aegis: bool = False
    aegis_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _hash_workspace_cas(workspace_dir: Path) -> str:
    """Calcula el hash CAS SHA-256 determinista del contenido del workspace excluyendo metadatos efímeros."""
    ignored_parts = {".git", "__pycache__", ".pytest_cache", ".sandbox_home", ".sandbox_tmp"}
    if not workspace_dir.exists():
        return hashlib.sha256(b"").hexdigest()
    entries: List[str] = []
    for fpath in sorted(workspace_dir.rglob("*")):
        if not fpath.is_file():
            continue
        if set(fpath.parts) & ignored_parts:
            continue
        rel = fpath.relative_to(workspace_dir).as_posix()
        digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
        entries.append(f"{rel}:{digest}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


def _format_cmd_display(command: Union[str, Sequence[str]]) -> str:
    if isinstance(command, str):
        return command
    return " ".join(str(x) for x in command)


def _build_isolated_env(
    sandbox_root: Path,
    env_allowlist: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    home_dir = sandbox_root / ".sandbox_home"
    tmp_dir = sandbox_root / ".sandbox_tmp"
    home_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    clean_env: Dict[str, str] = {}
    for key in SAFE_HOST_ENV_ALLOWLIST:
        val = os.environ.get(key)
        if val is not None:
            clean_env[key] = val

    clean_env.update({
        "HOME": str(home_dir),
        "USERPROFILE": str(home_dir),
        "TMP": str(tmp_dir),
        "TEMP": str(tmp_dir),
        "TMPDIR": str(tmp_dir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1",
    })
    if isinstance(env_allowlist, dict):
        for k, v in env_allowlist.items():
            k_str = str(k)
            if _SECRET_ENV_KEY_RE.search(k_str):
                continue
            clean_env[k_str] = str(v)
    return clean_env


class DockerSandboxDriver:
    """Driver real basado en contenedores Docker efímeros con red deshabilitada y límites duros."""

    isolation_tier = "DOCKER_CONTAINER"

    def __init__(
        self,
        image: str = "python:3.12-slim",
        cpus: str = "1.0",
        memory: str = "512m",
        pids_limit: int = 64,
    ):
        self.image = image
        self.cpus = cpus
        self.memory = memory
        self.pids_limit = max(8, int(pids_limit))

    @staticmethod
    def is_available() -> bool:
        if not shutil.which("docker"):
            return False
        try:
            proc = subprocess.run(["docker", "info"], capture_output=True, timeout=4)
            return proc.returncode == 0
        except Exception:
            return False

    def build_docker_command(
        self,
        worktree_dir: Path,
        command: Union[str, Sequence[str]],
        container_name: str,
        env_allowlist: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        cmd_list: List[str] = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--cpus",
            self.cpus,
            "--memory",
            self.memory,
            "--pids-limit",
            str(self.pids_limit),
            "--security-opt",
            "no-new-privileges",
            "-e",
            "PYTHONDONTWRITEBYTECODE=1",
            "-e",
            "PYTHONUNBUFFERED=1",
            "-e",
            "HOME=/workspace/.sandbox_home",
            "-e",
            "TMP=/workspace/.sandbox_tmp",
            "-e",
            "TEMP=/workspace/.sandbox_tmp",
        ]
        if isinstance(env_allowlist, dict):
            for k, v in sorted(env_allowlist.items()):
                if not _SECRET_ENV_KEY_RE.search(str(k)):
                    cmd_list.extend(["-e", f"{k}={v}"])
        cmd_list.extend([
            "-v",
            f"{Path(worktree_dir).resolve()}:/workspace:rw",
            "-w",
            "/workspace",
            self.image,
        ])
        if isinstance(command, str):
            cmd_list.extend(["/bin/sh", "-lc", command])
        else:
            cmd_list.extend(str(c) for c in command)
        return cmd_list

    def execute(
        self,
        repo_dir: Path,
        command: Union[str, Sequence[str]],
        timeout_sec: float = 30.0,
        env_allowlist: Optional[Dict[str, str]] = None,
        overlay_files: Optional[Dict[str, str]] = None,
    ) -> SandboxResult:
        cmd_str = _format_cmd_display(command)
        t0 = time.perf_counter()
        sec = AegisShield.scan_text(cmd_str)
        if not sec.safe:
            reason = sec.findings[0].rule_id if sec.findings else "AEGIS_BLOCKED"
            return SandboxResult(
                exit_code=126,
                stdout="",
                stderr=f"Blocked by AegisShield: {reason}",
                duration_ms=round((time.perf_counter() - t0) * 1000.0, 3),
                isolation_tier=self.isolation_tier,
                timed_out=False,
                killed_processes=0,
                artifacts_cas_sha256="",
                command=cmd_str,
                worktree_clean=True,
                blocked_by_aegis=True,
                aegis_reason=reason,
            )

        if not self.is_available():
            raise RuntimeError("Docker daemon is not available on this host")

        repo_path = Path(repo_dir).resolve()
        container_name = f"aleph_sbx_{uuid.uuid4().hex[:12]}"
        has_git = (repo_path / ".git").exists()
        wt_parent = Path(tempfile.mkdtemp(prefix="aleph_docker_wt_"))
        wt_dir = wt_parent / "workspace"
        timed_out = False
        killed = 0
        rc = 1
        stdout = ""
        stderr = ""
        cas_digest = ""

        try:
            if has_git:
                subprocess.run(
                    ["git", "-C", str(repo_path), "worktree", "add", "--detach", str(wt_dir), "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                shutil.copytree(repo_path, wt_dir)

            if overlay_files:
                for rel, content in overlay_files.items():
                    fp = (wt_dir / rel).resolve()
                    if wt_dir.resolve() not in fp.parents and fp != wt_dir.resolve():
                        raise ValueError(f"Path traversal blocked in overlay: {rel}")
                    fp.parent.mkdir(parents=True, exist_ok=True)
                    fp.write_text(content, encoding="utf-8")

            docker_cmd = self.build_docker_command(wt_dir, command, container_name, env_allowlist=env_allowlist)
            try:
                proc = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout_sec)
                rc = proc.returncode
                stdout = proc.stdout or ""
                stderr = proc.stderr or ""
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                rc = 124
                stdout = exc.stdout.decode("utf-8", errors="ignore") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                stderr = exc.stderr.decode("utf-8", errors="ignore") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                subprocess.run(["docker", "kill", container_name], capture_output=True, timeout=5)
                killed = 1
            cas_digest = _hash_workspace_cas(wt_dir)
        finally:
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, timeout=5)
            if has_git and wt_dir.exists():
                subprocess.run(
                    ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(wt_dir)],
                    capture_output=True,
                    text=True,
                )
                subprocess.run(["git", "-C", str(repo_path), "worktree", "prune"], capture_output=True, text=True)
            shutil.rmtree(wt_parent, ignore_errors=True)

        return SandboxResult(
            exit_code=rc,
            stdout=stdout,
            stderr=stderr,
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 3),
            isolation_tier=self.isolation_tier,
            timed_out=timed_out,
            killed_processes=killed,
            artifacts_cas_sha256=cas_digest,
            command=cmd_str,
            worktree_clean=not wt_parent.exists(),
        )


class IsolatedWorktreeProcessDriver:
    """
    Driver determinista de aislamiento local basado en git worktree efímero real + entorno limpio
    (sin secretos del host) + terminación dura del árbol de subprocesos del SO al exceder timeout.
    """

    isolation_tier = "PROCESS_WORKTREE"

    @staticmethod
    def _kill_process_tree(proc: subprocess.Popen) -> int:
        if proc.poll() is not None:
            return 0
        killed = 1
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except Exception:
                pass
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass
        else:
            try:
                import signal
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        return killed

    def execute(
        self,
        repo_dir: Path,
        command: Union[str, Sequence[str]],
        timeout_sec: float = 30.0,
        env_allowlist: Optional[Dict[str, str]] = None,
        overlay_files: Optional[Dict[str, str]] = None,
    ) -> SandboxResult:
        cmd_str = _format_cmd_display(command)
        t0 = time.perf_counter()
        sec = AegisShield.scan_text(cmd_str)
        if not sec.safe:
            reason = sec.findings[0].rule_id if sec.findings else "AEGIS_BLOCKED"
            return SandboxResult(
                exit_code=126,
                stdout="",
                stderr=f"Blocked by AegisShield: {reason}",
                duration_ms=round((time.perf_counter() - t0) * 1000.0, 3),
                isolation_tier=self.isolation_tier,
                timed_out=False,
                killed_processes=0,
                artifacts_cas_sha256="",
                command=cmd_str,
                worktree_clean=True,
                blocked_by_aegis=True,
                aegis_reason=reason,
            )

        repo_path = Path(repo_dir).resolve()
        has_git = (repo_path / ".git").exists()
        wt_parent = Path(tempfile.mkdtemp(prefix="aleph_proc_wt_"))
        wt_dir = wt_parent / "workspace"
        timed_out = False
        killed = 0
        rc = 1
        stdout = ""
        stderr = ""
        cas_digest = ""

        try:
            if has_git:
                git_add = subprocess.run(
                    ["git", "-C", str(repo_path), "worktree", "add", "--detach", str(wt_dir), "HEAD"],
                    capture_output=True,
                    text=True,
                )
                if git_add.returncode != 0:
                    shutil.copytree(repo_path, wt_dir, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
                    has_git = False
            else:
                shutil.copytree(repo_path, wt_dir, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))

            if overlay_files:
                for rel, content in overlay_files.items():
                    fp = (wt_dir / rel).resolve()
                    if wt_dir.resolve() not in fp.parents and fp != wt_dir.resolve():
                        raise ValueError(f"Path traversal blocked in overlay: {rel}")
                    fp.parent.mkdir(parents=True, exist_ok=True)
                    fp.write_text(content, encoding="utf-8")

            clean_env = _build_isolated_env(wt_parent, env_allowlist=env_allowlist)
            popen_kwargs: Dict[str, Any] = {
                "cwd": str(wt_dir),
                "env": clean_env,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "shell": isinstance(command, str),
            }
            if os.name == "nt":
                popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                popen_kwargs["start_new_session"] = True

            proc = subprocess.Popen(command, **popen_kwargs)
            try:
                stdout, stderr = proc.communicate(timeout=timeout_sec)
                rc = proc.returncode if proc.returncode is not None else 0
            except subprocess.TimeoutExpired:
                timed_out = True
                killed = self._kill_process_tree(proc)
                try:
                    stdout, stderr = proc.communicate(timeout=3)
                except Exception:
                    stdout, stderr = "", ""
                rc = 124
            cas_digest = _hash_workspace_cas(wt_dir)
        finally:
            if has_git and wt_dir.exists():
                subprocess.run(
                    ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(wt_dir)],
                    capture_output=True,
                    text=True,
                )
                subprocess.run(["git", "-C", str(repo_path), "worktree", "prune"], capture_output=True, text=True)
            shutil.rmtree(wt_parent, ignore_errors=True)

        return SandboxResult(
            exit_code=rc,
            stdout=stdout or "",
            stderr=stderr or "",
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 3),
            isolation_tier=self.isolation_tier,
            timed_out=timed_out,
            killed_processes=killed,
            artifacts_cas_sha256=cas_digest,
            command=cmd_str,
            worktree_clean=not wt_parent.exists(),
        )


def probe_sandbox_environment() -> Dict[str, Any]:
    docker_ok = DockerSandboxDriver.is_available()
    return {
        "docker_available": docker_ok,
        "wsl_available": bool(shutil.which("wsl")),
        "git_available": bool(shutil.which("git")),
        "taskkill_available": bool(shutil.which("taskkill")),
        "default_isolation_tier": "DOCKER_CONTAINER" if docker_ok else "PROCESS_WORKTREE",
    }


def create_sandbox_driver(mode: str = "auto", **kwargs: Any) -> Union[DockerSandboxDriver, IsolatedWorktreeProcessDriver]:
    m = str(mode or "auto").strip().lower()
    if m == "docker":
        if not DockerSandboxDriver.is_available():
            raise RuntimeError("Requested sandbox mode 'docker', but Docker daemon is not running")
        return DockerSandboxDriver(**kwargs)
    if m == "auto" and DockerSandboxDriver.is_available():
        return DockerSandboxDriver(**kwargs)
    return IsolatedWorktreeProcessDriver()
