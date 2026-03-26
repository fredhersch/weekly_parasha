from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=False,
        text=True,
        capture_output=True,
    )


def push_note(
    *,
    git_root: Path,
    file_path: Path,
    commit_message: str,
) -> dict:
    """
    Stage the given file (must be under git_root), commit if there are staged
    changes, then push. Returns a small status dict for logging.
    """
    git_root = git_root.resolve()
    file_path = file_path.resolve()
    if not (git_root / ".git").exists():
        return {"ok": False, "skipped": True, "reason": "not a git repository", "git_root": str(git_root)}

    try:
        rel = file_path.relative_to(git_root)
    except ValueError:
        return {
            "ok": False,
            "skipped": True,
            "reason": f"file not under git root: {file_path} vs {git_root}",
            "git_root": str(git_root),
        }

    add = _run(["git", "add", "--", str(rel)], cwd=git_root)
    if add.returncode != 0:
        return {
            "ok": False,
            "skipped": False,
            "step": "git add",
            "stderr": add.stderr.strip(),
            "stdout": add.stdout.strip(),
        }

    diff = _run(["git", "diff", "--cached", "--quiet"], cwd=git_root)
    if diff.returncode == 0:
        return {"ok": True, "skipped": True, "reason": "nothing to commit", "git_root": str(git_root)}

    commit = _run(
        ["git", "commit", "-m", commit_message],
        cwd=git_root,
    )
    if commit.returncode != 0:
        return {
            "ok": False,
            "skipped": False,
            "step": "git commit",
            "stderr": commit.stderr.strip(),
            "stdout": commit.stdout.strip(),
        }

    push = _run(["git", "push"], cwd=git_root)
    if push.returncode != 0:
        return {
            "ok": False,
            "skipped": False,
            "step": "git push",
            "stderr": push.stderr.strip(),
            "stdout": push.stdout.strip(),
        }

    return {"ok": True, "skipped": False, "git_root": str(git_root), "pushed": True}


def resolve_git_root(*, vault_root: Path) -> Path:
    """SECOND_BRAIN_GIT_ROOT or OBSIDIAN_GIT_ROOT, else vault_root."""
    override = os.getenv("SECOND_BRAIN_GIT_ROOT") or os.getenv("OBSIDIAN_GIT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return vault_root
