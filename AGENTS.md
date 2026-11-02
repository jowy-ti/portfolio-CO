# AGENTS.md

## What this project is

Solved portfolio for `TOML2026_27_MLE_COP_Portfolio.pdf`: 33 exercises across
9 sections, combining the Maximum Likelihood Estimation and Convex
Optimization course notes.

Deliverable: one **executed** Jupyter notebook per section, `notebooks/s01…s09`.
Exercises are organized as `Task`, `Explore`, `Explain` (some omit `Explore`);
the `Explain` answers are part of the deliverable and belong in markdown cells.

Source material (read-only):

- `TOML2026_27_MLE_COP_Portfolio.pdf` — statements
- `TOML2026_27_Maximum_Likelihood_Estimation.pdf` — MLE notes, referenced as `[MLE x.y]`
- `TOML2026_27__Convex_Optimization.pdf` — CO notes, referenced as `[CO x]`

## Environment

Use pixi for everything:

```sh
pixi run python ...
pixi run jupyter lab
```

Dependencies are pinned in `pixi.toml`. Do not add packages without asking;
`numpy`, `scipy`, `matplotlib`, `networkx`, `nbformat`, `nbclient` and
`ipykernel` are available.

There are no `.py` notebook sources. Edit `.ipynb` files directly (or through
the MCP tools below); do not reintroduce a `.py → .ipynb` build pipeline. The
only script in the project is `tools/pdftext.py` (PDF text extraction, see
below).

## Jupyter MCP server

`opencode.json` registers the project-local server `jupyter`
(`pixi run python -m jupyter_mcp.server`). Its code lives in `jupyter_mcp/`.
Tools appear as `jupyter_*`; in Code Mode call them through
`tools.jupyter.<tool>`.

- Kernel: `start_kernel`, `execute`, `list_kernels`, `restart_kernel`, `stop_kernel`
- Notebook: `create_notebook`, `list_cells`, `read_cell`, `write_cell`,
  `insert_cell`, `delete_cell`, `move_cell`, `execute_notebook`,
  `validate_notebook`, `notebook_summary`

Prefer `execute_notebook` for the final artifact: it runs in a fresh kernel,
saves outputs in place, and reports unexecuted cells or error outputs. Use
`start_kernel` + `execute` only for quick exploration. Call `stop_kernel` when a
persistent kernel is no longer needed.

Notebook paths are relative to the project root; the server refuses paths
outside it.

## Notebook conventions

- File names: `notebooks/sNN_<topic>.ipynb`, one per section.
- Structure: a top-level `# N. Section title` markdown cell, then one
  `## N.k Exercise title` block per exercise with its statement reference.
- Solve in order. Keep `Task` / `Explore` / `Explain` visibly separated: code
  and plots answer `Task`/`Explore`, markdown answers `Explain`.
- Keep `Explain` answers brief: a few sentences that answer the question, not a
  restatement of the task.
- `Explain` must quote the numbers the notebook actually computes, e.g.
  $P(\hat\theta=1/2)=0.66,\,0.80,\,0.99$, not adjectives like "very frequent":
  if a code cell prints it, the answer should use it.
- Qualify any claim that only holds on part of the grid or parameter range:
  "the Gaussian overlay is accurate at $m=20$ for $\theta=1/2$" is true, "at
  $m=20$ it looks Gaussian" is not.
- The user edits `Explain` cells by hand in VS Code. Re-read a markdown cell
  before changing it, and keep their wording where it is already correct.
- When a task says "reproduce the example in [MLE x.y]", reproduce that
  example's estimator exactly. In 1.1, for instance, the estimator is restricted
  to the five coins; do not substitute the unrestricted $\hat\theta=k/m$.
- For a discrete estimator, check the simulation against the exact PMF obtained
  by enumerating the outcomes, not only against a mean/variance formula.
- Every identity, gradient, duality gap or optimality condition that is used
  must be checked numerically right next to it:
  `assert np.allclose(lhs, rhs)` (or an explicit tolerance).
- Optimization exercises (sections 5–9): solve numerically as well as
  analytically and assert agreement with `scipy.optimize`; check residuals,
  dual feasibility and a non-negative duality gap.
- Seed every random experiment (`rng = np.random.default_rng(2026)`) so the
  executed outputs are reproducible.
- Plots must be labelled (axes, legend, title) and explained in the text; never
  leave a figure the reader cannot interpret.
- No network access or external datasets; generate data synthetically.
- The notebook `kernelspec` stays `python3`, which resolves to the pixi
  interpreter (3.12.x). A system Python run silently rewrites `language_info`;
  after any run, check that `language_info.version` is `3.12.*`.
- PDFs cannot be opened with the `read` tool: it fails with "this model does
  not support pdf input". Extract the text with the project script instead:
  `pixi run python tools/pdftext.py <file.pdf> > /tmp/<name>.txt` (zlib plus a
  small parser, no dependency). There is no `pdftotext` and no PDF library
  (`pypdf`, `pdfminer`, PyMuPDF); do not add one. The output is de-spaced
  (`p(yj )` for $p(y\mid\theta)$) but legible, and contains latin-1 bytes, so
  search it with `grep -a`.
- `scipy.special.gammaln` exists; `scipy.stats.gammaln` does not. When
  broadcasting a 1-D mask over a 2-D grid, pass `mask[:, None]`:
  `np.broadcast_to` alone aligns the mask to the last axis.
- A VS Code save can drop `execution_count` from individual cells while keeping
  their outputs; `validate_notebook` then reports them as "not executed". Re-run
  `execute_notebook` instead of trusting the stored outputs.
- Keep notebooks under a few MB. This directory is not a git repository, so
  there is no VCS safety net: re-read a cell before deleting or rewriting it.

## Section map

| Section | Title | Exercises | Notebook | Status |
| --- | --- | --- | --- | --- |
| 1 | A first look at maximum likelihood | 1.1–1.3 | `s01_mle_intro.ipynb` | done, reviewed |
| 2 | Log-likelihood landscapes for simple models | 2.1–2.5 | `s02_landscapes.ipynb` | done, Explain hand-edit in progress (2.3) |
| 3 | Convex sets | 3.1–3.3 | `s03_convex_sets.ipynb` | not started |
| 4 | Convex functions | 4.1–4.6 | `s04_convex_functions.ipynb` | not started |
| 5 | Linear programming | 5.1–5.3 | `s05_linear_programming.ipynb` | not started |
| 6 | Quadratic programming with linear constraints | 6.1–6.2 | `s06_qp_constraints.ipynb` | not started |
| 7 | The Lagrangian and the dual function | 7.1–7.5 | `s07_lagrangian_dual.ipynb` | not started |
| 8 | Strong duality and Slater's condition | 8.1–8.2 | `s08_strong_duality.ipynb` | not started |
| 9 | KKT conditions and solution methods | 9.1–9.4 | `s09_kkt_methods.ipynb` | not started |

## Current phase

Section 1 is done: `notebooks/s01_mle_intro.ipynb` is executed, validated and
reviewed. Section 2 is done: `notebooks/s02_landscapes.ipynb` is executed and
validated (27 cells, 16 code, 0 error outputs, `language_info` 3.12.16, all 16
code cells executed). Its `Explain` hand-editing has started — 2.3 is the
user's wording, 2.1, 2.2, 2.4 and 2.5 are still the drafted text. Sections 3–9
are not started; start one only when the user says so.

Note for section 2: a VS Code save on 2 Nov dropped `execution_count` on cells
3, 18 and 19 while keeping their outputs, so `validate_notebook` reported "not
executed"; the notebook was re-executed from the same sources and the printed
numbers are unchanged (2.1 `mu_hat = 0.8063`, 2.2 MSE `0.7417` vs `1.9596` at
`m = 2`, 2.4 precision form `-641.141118`, 2.5 L1 `(2.4931, 0.4321)`). Re-run
rather than trusting stored outputs if this reappears.

One section per session. Finish each section with `execute_notebook`, then
`validate_notebook`, then update the Status column above and this section:
this file is the only handoff between sessions.
