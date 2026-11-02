"""MCP stdio server exposing a persistent Jupyter kernel and .ipynb editing.

Run it with:

    pixi run python -m jupyter_mcp.server
"""

from __future__ import annotations

from typing import Any

import nbformat
from mcp.server import MCPServer

from . import core

INSTRUCTIONS = f"""\
Jupyter notebook server for the MLE / convex-optimization portfolio.

Workspace root: {core.ROOT}
All notebook paths are resolved against that root; paths outside it are rejected.

Typical loop:
1. `create_notebook` (or open an existing one).
2. `insert_cell` / `write_cell` to add markdown and code.
3. `execute_notebook` to run the whole file and save outputs, or `start_kernel`
   + `execute` for exploratory one-off runs in a persistent kernel.
4. `validate_notebook` before declaring a notebook finished: every code cell
   must be executed and no cell may contain an error output.
"""

mcp = MCPServer(
    name="jupyter",
    version="0.1.0",
    instructions=INSTRUCTIONS,
)


def _rel(path) -> str:
    try:
        return str(path.relative_to(core.ROOT))
    except ValueError:
        return str(path)


def _summary(path) -> dict[str, Any]:
    nb = nbformat.read(path, as_version=4)
    return core.notebook_summary_data(nb, path=_rel(path))


# --------------------------------------------------------------------------- kernel


@mcp.tool()
def start_kernel(kernel_id: str = "default", kernel_name: str = "python3", cwd: str | None = None) -> dict[str, Any]:
    """Start (or reuse) a persistent IPython kernel.

    Args:
        kernel_id: Name used by later `execute` calls. Defaults to "default".
        kernel_name: Jupyter kernelspec name. Defaults to "python3".
        cwd: Kernel working directory, relative to the workspace root.
    """
    kernel = core.KERNELS.start(kernel_id, kernel_name, cwd)
    return {"kernel_id": kernel.kernel_id, "kernel_name": kernel.kernel_name, "cwd": str(kernel.cwd), "alive": True}


@mcp.tool()
def list_kernels() -> dict[str, Any]:
    """List kernels started by this server and whether they are still alive."""
    return {"kernels": core.KERNELS.list()}


@mcp.tool()
def execute(
    code: str,
    kernel_id: str = "default",
    timeout: float = 120.0,
    silent: bool = False,
) -> dict[str, Any]:
    """Execute code in a running kernel and return its streams, results and errors.

    The kernel keeps all state between calls. Start one with `start_kernel` first.

    Args:
        code: Python source to run.
        kernel_id: Kernel to use. Defaults to "default".
        timeout: Seconds before the execution is interrupted. Defaults to 120.
        silent: Run without storing history or echoing results.
    """
    return core.KERNELS.get(kernel_id).execute(code, timeout=timeout, silent=silent)


@mcp.tool()
def restart_kernel(kernel_id: str = "default") -> dict[str, Any]:
    """Restart a kernel, discarding all Python state."""
    kernel = core.KERNELS.get(kernel_id)
    kernel.restart()
    return {"kernel_id": kernel_id, "restarted": True}


@mcp.tool()
def stop_kernel(kernel_id: str = "default") -> dict[str, Any]:
    """Shut a kernel down and forget it."""
    return {"kernel_id": kernel_id, "stopped": core.KERNELS.stop(kernel_id)}


# ------------------------------------------------------------------------- notebook


@mcp.tool()
def create_notebook(path: str, title: str | None = None, overwrite: bool = False) -> dict[str, Any]:
    """Create an empty notebook with a python3 kernelspec.

    Args:
        path: Destination .ipynb path relative to the workspace root.
        title: Optional markdown title cell to add first.
        overwrite: Replace the file if it already exists. Defaults to false.
    """
    resolved = core.resolve_path(path)
    if resolved.suffix != ".ipynb":
        raise ValueError(f"not a notebook: {path}")
    if resolved.exists() and not overwrite:
        raise FileExistsError(f"notebook already exists: {_rel(resolved)}")
    nb = core.new_notebook(title)
    core.write_notebook(resolved, nb)
    return core.notebook_summary_data(nb, path=_rel(resolved))


@mcp.tool()
def list_cells(path: str) -> dict[str, Any]:
    """List every cell with its index, type, execution count and a short preview."""
    resolved, nb = core.read_notebook(path)
    cells = []
    for index, cell in enumerate(nb.cells):
        cells.append(
            {
                "index": index,
                "cell_type": cell.cell_type,
                "execution_count": cell.get("execution_count"),
                "preview": core.cell_preview(cell.source),
                "lines": len(cell.source.splitlines()),
            }
        )
    return {"path": _rel(resolved), "cells": cells}


@mcp.tool()
def read_cell(path: str, index: int) -> dict[str, Any]:
    """Return the full source and metadata of one cell.

    Args:
        path: Notebook path relative to the workspace root.
        index: Zero-based cell index.
    """
    resolved, nb = core.read_notebook(path)
    cell = _cell(nb, index)
    return {
        "path": _rel(resolved),
        "index": index,
        "cell_type": cell.cell_type,
        "source": cell.source,
        "execution_count": cell.get("execution_count"),
    }


@mcp.tool()
def write_cell(path: str, index: int, source: str, cell_type: str | None = None) -> dict[str, Any]:
    """Replace the source of an existing cell.

    Args:
        path: Notebook path relative to the workspace root.
        index: Zero-based cell index.
        source: New cell source.
        cell_type: Optionally convert the cell to "code" or "markdown".
    """
    resolved, nb = core.read_notebook(path)
    cell = _cell(nb, index)
    if cell_type is not None and cell_type != cell.cell_type:
        nb.cells[index] = _new_cell(cell_type, source)
    else:
        cell.source = source
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    core.write_notebook(resolved, nb)
    return {"path": _rel(resolved), "index": index, "cell_type": nb.cells[index].cell_type, "cells": len(nb.cells)}


@mcp.tool()
def insert_cell(path: str, index: int, source: str, cell_type: str = "code") -> dict[str, Any]:
    """Insert a new cell at a zero-based index (len(cells) appends)."""
    resolved, nb = core.read_notebook(path)
    if index < 0 or index > len(nb.cells):
        raise IndexError(f"index {index} out of range for {len(nb.cells)} cells")
    nb.cells.insert(index, _new_cell(cell_type, source))
    core.write_notebook(resolved, nb)
    return {"path": _rel(resolved), "index": index, "cell_type": cell_type, "cells": len(nb.cells)}


@mcp.tool()
def delete_cell(path: str, index: int) -> dict[str, Any]:
    """Delete the cell at a zero-based index."""
    resolved, nb = core.read_notebook(path)
    _cell(nb, index)
    nb.cells.pop(index)
    core.write_notebook(resolved, nb)
    return {"path": _rel(resolved), "deleted": index, "cells": len(nb.cells)}


@mcp.tool()
def move_cell(path: str, index: int, new_index: int) -> dict[str, Any]:
    """Move a cell to another zero-based position."""
    resolved, nb = core.read_notebook(path)
    cell = _cell(nb, index)
    if new_index < 0 or new_index >= len(nb.cells):
        raise IndexError(f"new_index {new_index} out of range for {len(nb.cells)} cells")
    nb.cells.pop(index)
    nb.cells.insert(new_index, cell)
    core.write_notebook(resolved, nb)
    return {"path": _rel(resolved), "from": index, "to": new_index, "cells": len(nb.cells)}


@mcp.tool()
def execute_notebook(path: str, timeout: float = 1200.0, allow_errors: bool = False) -> dict[str, Any]:
    """Execute every code cell in a fresh kernel and save the outputs in place.

    Args:
        path: Notebook path relative to the workspace root.
        timeout: Per-cell timeout in seconds. Defaults to 1200.
        allow_errors: Keep going after a failing cell. Defaults to false.
    """
    return core.execute_notebook_file(path, timeout=timeout, allow_errors=allow_errors)


@mcp.tool()
def validate_notebook(path: str, require_executed: bool = True) -> dict[str, Any]:
    """Check the notebook schema, kernelspec, execution counts and error outputs."""
    resolved, nb = core.read_notebook(path)
    result = core.validate_notebook_data(nb, require_executed=require_executed)
    result["path"] = _rel(resolved)
    result["summary"]["path"] = result["path"]
    return result


@mcp.tool()
def notebook_summary(path: str) -> dict[str, Any]:
    """Report cell counts, execution counts, errors and metadata for a notebook."""
    resolved = core.resolve_path(path)
    return _summary(resolved)


def _cell(nb, index: int):
    if index < 0 or index >= len(nb.cells):
        raise IndexError(f"index {index} out of range for {len(nb.cells)} cells")
    return nb.cells[index]


def _new_cell(cell_type: str, source: str):
    if cell_type == "code":
        return nbformat.v4.new_code_cell(source)
    if cell_type == "markdown":
        return nbformat.v4.new_markdown_cell(source)
    if cell_type == "raw":
        return nbformat.v4.new_raw_cell(source)
    raise ValueError(f"unsupported cell_type: {cell_type!r}")


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
