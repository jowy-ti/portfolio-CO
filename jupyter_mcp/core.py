"""Kernel and notebook primitives used by the MCP tools.

Everything here is synchronous and blocking. The MCP layer runs each tool in a
worker thread, so a lock is enough to keep one kernel from being driven by two
calls at once.
"""

from __future__ import annotations

import atexit
import os
import threading
import time
from pathlib import Path
from typing import Any

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
from queue import Empty

MAX_TEXT = 20_000


def _root() -> Path:
    return Path(os.environ.get("JUPYTER_MCP_ROOT", os.getcwd())).resolve()


ROOT = _root()


def resolve_path(path: str) -> Path:
    """Resolve *path* against the workspace root and refuse to leave it."""
    if not path or not str(path).strip():
        raise ValueError("path must not be empty")
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    if candidate != ROOT and ROOT not in candidate.parents:
        raise ValueError(f"path escapes the workspace root {ROOT}: {path}")
    return candidate


def _notebook_path(path: str) -> Path:
    resolved = resolve_path(path)
    if resolved.suffix != ".ipynb":
        raise ValueError(f"not a notebook: {path}")
    return resolved


def _clip(text: str) -> str:
    if len(text) <= MAX_TEXT:
        return text
    return text[:MAX_TEXT] + f"\n... [truncated {len(text) - MAX_TEXT} chars]"


def read_notebook(path: str) -> tuple[Path, nbformat.NotebookNode]:
    resolved = _notebook_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"notebook does not exist: {resolved}")
    nb = nbformat.read(resolved, as_version=4)
    return resolved, nb


def write_notebook(path: Path, nb: nbformat.NotebookNode) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    nbformat.write(nb, tmp)
    os.replace(tmp, path)


def new_notebook(title: str | None = None) -> nbformat.NotebookNode:
    cells = []
    if title:
        cells.append(nbformat.v4.new_markdown_cell(f"# {title}"))
    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python"}
    return nb


class Kernel:
    def __init__(self, kernel_id: str, kernel_name: str = "python3", cwd: Path | None = None):
        self.kernel_id = kernel_id
        self.kernel_name = kernel_name
        self.cwd = cwd or ROOT
        self.km = KernelManager(kernel_name=kernel_name)
        self.km.start_kernel(cwd=str(self.cwd))
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready(timeout=60)
        self.lock = threading.RLock()

    def alive(self) -> bool:
        return bool(self.km.is_alive())

    def execute(self, code: str, timeout: float = 120.0, silent: bool = False) -> dict[str, Any]:
        with self.lock:
            if not self.alive():
                raise RuntimeError(f"kernel {self.kernel_id!r} is not running")
            msg_id = self.kc.execute(
                code,
                silent=silent,
                store_history=not silent,
                allow_stdin=False,
                stop_on_error=True,
            )
            deadline = time.monotonic() + timeout
            outputs: list[dict[str, Any]] = []
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self.km.interrupt_kernel()
                    raise TimeoutError(f"cell did not finish within {timeout}s")
                try:
                    msg = self.kc.get_iopub_msg(timeout=remaining)
                except Empty:
                    self.km.interrupt_kernel()
                    raise TimeoutError(f"cell did not finish within {timeout}s") from None
                if msg["parent_header"].get("msg_id") != msg_id:
                    continue
                kind = msg["msg_type"]
                content = msg["content"]
                if kind == "status":
                    if content.get("execution_state") == "idle":
                        break
                elif kind == "stream":
                    outputs.append(
                        {"type": "stream", "name": content.get("name", "stdout"), "text": _clip(content.get("text", ""))}
                    )
                elif kind in ("execute_result", "display_data"):
                    data = content.get("data", {})
                    entry: dict[str, Any] = {
                        "type": kind,
                        "data": {key: _clip(value) for key, value in data.items() if key == "text/plain"},
                    }
                    if "image/png" in data:
                        entry["image_png_bytes"] = len(data["image/png"])
                    entry["execution_count"] = content.get("execution_count")
                    outputs.append(entry)
                elif kind == "error":
                    outputs.append(
                        {
                            "type": "error",
                            "ename": content.get("ename"),
                            "evalue": content.get("evalue"),
                            "traceback": [_clip(line) for line in content.get("traceback", [])],
                        }
                    )

            reply: dict[str, Any] = {}
            try:
                shell_msg = self.kc.get_shell_msg(timeout=10)
                while shell_msg["parent_header"].get("msg_id") != msg_id:
                    shell_msg = self.kc.get_shell_msg(timeout=10)
                reply = shell_msg["content"]
            except Empty:
                pass

            failed = any(output["type"] == "error" for output in outputs) or reply.get("status") == "error"
            return {
                "kernel_id": self.kernel_id,
                "status": "error" if failed else "ok",
                "execution_count": reply.get("execution_count"),
                "outputs": outputs,
            }

    def restart(self) -> None:
        with self.lock:
            self.km.restart_kernel(now=True)
            self.kc.wait_for_ready(timeout=60)

    def stop(self) -> None:
        with self.lock:
            try:
                self.kc.stop_channels()
            finally:
                self.km.shutdown_kernel(now=True)


class KernelRegistry:
    def __init__(self) -> None:
        self._kernels: dict[str, Kernel] = {}
        self._lock = threading.RLock()

    def start(self, kernel_id: str = "default", kernel_name: str = "python3", cwd: str | None = None) -> Kernel:
        with self._lock:
            existing = self._kernels.get(kernel_id)
            if existing is not None and existing.alive():
                return existing
            workdir = resolve_path(cwd) if cwd else ROOT
            if not workdir.is_dir():
                raise FileNotFoundError(f"kernel cwd does not exist: {workdir}")
            kernel = Kernel(kernel_id, kernel_name, workdir)
            self._kernels[kernel_id] = kernel
            return kernel

    def get(self, kernel_id: str = "default") -> Kernel:
        with self._lock:
            kernel = self._kernels.get(kernel_id)
        if kernel is None or not kernel.alive():
            raise KeyError(f"no running kernel named {kernel_id!r}; call start_kernel first")
        return kernel

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            items = [
                {
                    "kernel_id": kernel.kernel_id,
                    "kernel_name": kernel.kernel_name,
                    "alive": kernel.alive(),
                    "cwd": str(kernel.cwd),
                }
                for kernel in self._kernels.values()
            ]
        return items

    def stop(self, kernel_id: str = "default") -> bool:
        with self._lock:
            kernel = self._kernels.pop(kernel_id, None)
        if kernel is None:
            return False
        kernel.stop()
        return True

    def stop_all(self) -> None:
        for kernel_id in list(self._kernels):
            try:
                self.stop(kernel_id)
            except Exception:
                pass


KERNELS = KernelRegistry()
atexit.register(KERNELS.stop_all)


def cell_preview(source: str, limit: int = 100) -> str:
    first = source.strip().splitlines()[0] if source.strip() else ""
    first = " ".join(first.split())
    return first[:limit] + ("..." if len(first) > limit else "")


def notebook_summary_data(nb: nbformat.NotebookNode, path: str | None = None) -> dict[str, Any]:
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    errors = sum(
        1 for cell in code_cells for output in cell.get("outputs", []) if output.get("output_type") == "error"
    )
    return {
        "path": path,
        "nbformat": f"{nb.nbformat}.{nb.nbformat_minor}",
        "kernelspec": nb.metadata.get("kernelspec", {}).get("name"),
        "cells": len(nb.cells),
        "code_cells": len(code_cells),
        "markdown_cells": len(nb.cells) - len(code_cells),
        "executed_code_cells": sum(1 for cell in code_cells if cell.get("execution_count") is not None),
        "error_outputs": errors,
    }


def validate_notebook_data(nb: nbformat.NotebookNode, require_executed: bool = True) -> dict[str, Any]:
    issues: list[str] = []
    try:
        nbformat.validate(nb)
    except Exception as exc:  # nbformat.ValidationError
        issues.append(f"schema: {exc}")

    if not nb.metadata.get("kernelspec", {}).get("name"):
        issues.append("metadata.kernelspec.name is missing")

    for index, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        if require_executed and cell.get("execution_count") is None:
            issues.append(f"cell {index}: not executed")
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                issues.append(f"cell {index}: error {output.get('ename')}: {output.get('evalue')}")

    return {"ok": not issues, "issues": issues, "summary": notebook_summary_data(nb)}


def execute_notebook_file(
    path: str,
    timeout: float = 1200.0,
    allow_errors: bool = False,
    kernel_name: str = "python3",
) -> dict[str, Any]:
    resolved, nb = read_notebook(path)
    write_notebook(resolved, nb)  # normalise before executing
    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name=kernel_name,
        allow_errors=allow_errors,
        resources={"metadata": {"path": str(resolved.parent)}},
    )
    error: str | None = None
    try:
        client.execute()
    except CellExecutionError as exc:
        error = str(exc)
    write_notebook(resolved, nb)
    result = validate_notebook_data(nb, require_executed=True)
    result["path"] = str(resolved.relative_to(ROOT)) if resolved != ROOT else str(resolved)
    result["summary"]["path"] = result["path"]
    result["execution_error"] = error
    return result


__all__ = [
    "KERNELS",
    "ROOT",
    "cell_preview",
    "execute_notebook_file",
    "new_notebook",
    "notebook_summary_data",
    "read_notebook",
    "resolve_path",
    "validate_notebook_data",
    "write_notebook",
]
