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
  restatement of the task. Aim at $700$–$1000$ characters (one to three short
  paragraphs), the length of the section 2 answers; section 3's first drafts
  were $2.5$–$2.8$k and had to be cut.
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
- Keep notebooks under a few MB. This directory is a git repository
  (`main`, one commit per finished section): the `.ipynb` files keep their
  outputs, so diffs are unreadable — review with `list_cells` / `notebook_summary`
  and re-read a cell before deleting or rewriting it.

## Section map

| Section | Title | Exercises | Notebook | Status |
| --- | --- | --- | --- | --- |
| 1 | A first look at maximum likelihood | 1.1–1.3 | `s01_mle_intro.ipynb` | done, reviewed |
| 2 | Log-likelihood landscapes for simple models | 2.1–2.5 | `s02_landscapes.ipynb` | done, 2.3 Explore has sliders; Explain hand-edit in progress |
| 3 | Convex sets | 3.1–3.3 | `s03_convex_sets.ipynb` | done, Explain drafted (hand-edit pending) |
| 4 | Convex functions | 4.1–4.6 | `s04_convex_functions.ipynb` | done, Explain drafted (hand-edit pending) |
| 5 | Linear programming | 5.1–5.3 | `s05_linear_programming.ipynb` | done, Explain drafted (hand-edit pending) |
| 6 | Quadratic programming with linear constraints | 6.1–6.2 | `s06_qp_constraints.ipynb` | not started |
| 7 | The Lagrangian and the dual function | 7.1–7.5 | `s07_lagrangian_dual.ipynb` | not started |
| 8 | Strong duality and Slater's condition | 8.1–8.2 | `s08_strong_duality.ipynb` | not started |
| 9 | KKT conditions and solution methods | 9.1–9.4 | `s09_kkt_methods.ipynb` | not started |

## Current phase

Section 1 is done: `notebooks/s01_mle_intro.ipynb` is executed, validated and
reviewed. Section 2 is done: `notebooks/s02_landscapes.ipynb` is executed and
validated (30 cells, 18 code, 0 error outputs, `language_info` 3.12.16, all 18
code cells executed, 1.4 MB). Its `Explain` hand-editing has started — 2.3 is
the user's wording, 2.1, 2.2, 2.4 and 2.5 are still the drafted text. `Explain`
cells are at indices 7, 12, 19, 24, 29.

2.3 `Explore` ("vary $m$ and the true parameter") is answered by three cells
after the 2×2 panel (markdown 16, code 17, code 18). Cell 17 measures the
overlay error over $\hat\theta\pm2\,\mathrm{se}$ on a grid of $m$ and of the
true parameter: log-log slopes $-1.540$ (Poisson) and $-1.576$ (exponential)
against the $-3/2$ of the cubic term, exactly $0$ for the Gaussian, Poisson
error $0.00717\to0.00193$ as the true $\lambda$ goes $1\to10$ at $m=60$, and
exponential error identical to 12 digits for $\lambda=0.5\ldots4$ (scale
family). Cell 18 is the `ipywidgets` panel (sliders for $m$, both $\lambda$s,
$\theta$, $\mu$, $\sigma$); it re-seeds on every redraw and its saved output is
only the widget state, so the figure appears only when the cell runs. Both new
cells use their own `default_rng`, so the notebook-level `rng` stream and the
2.4/2.5 numbers are unchanged.

Section 3 is done: `notebooks/s03_convex_sets.ipynb` is executed and validated
(21 cells, 14 code, 0 error outputs, `language_info` 3.12.16, 1.3 MB). Its three
`Explain` cells are drafted as full answers and await the user's hand-editing.
Contents: 3.1 `segment_violations(membership, x, y, n)` plus five membership
tests (disc, annulus, crescent, union of two disjoint discs, intersection of
two overlapping discs) and deterministic witness pairs; 3.2 halfspace,
pentagon, hull, ellipsoid, the three norm balls, the $p=1/2$ "ball", the 3-D
simplex, an affine image of each and an indefinite $Q$; 3.3 the PSD cone
boundary $z^2=xy$, PSD segments, the $\operatorname{tr}X=1$ slice and the
$\det X\ge1$ set.

Section 3 numbers, for reference when re-running: 3.1 failures 157/300 annulus,
61/300 crescent, 162/300 union, 0/300 disc and intersection; witnesses outside
$C$ for $0.251\le\lambda\le0.750$ (annulus), $0.206$–$0.794$ (crescent),
$0.401$–$0.600$ (union); overlapping discs gap $0.7211>0.6$. 3.2 zero failures
for every convex set and its image, $p=1/2$ fails 13/200 (16/200 after the map),
$\sum\sqrt{|x_i|}=1.4142$ at the midpoint, affine residual $1.1\times10^{-16}$,
indefinite $Q$ gives $4.5>1$ at $(3,0)$ with 93.5% of the segment outside. 3.3
min eigenvalue over 200 000 combinations $9.286\times10^{-5}$, slice radius
$0.500000000000$, min det over 400 000 combinations $1.004249515513$, and
$\operatorname{diag}(2,0.4)/(0.4,2)$ with midpoint det $1.44$ for
$\{\det X\le1\}$.

Section 4 is done: `notebooks/s04_convex_functions.ipynb` is executed and
validated (34 cells, 21 code, 0 error outputs, `language_info` 3.12.16, 2.7 MB).
Its six `Explain` cells are drafted and await the user's hand-editing; they are
at indices 6, 12, 18, 23, 28, 33. Three widget cells (5, the $a$ of $x^a$; 17,
the $z$ of the $-\log\det$ slice; 22, the $a$ of the eigenvalue slice) save only
widget state, so each has a static small-multiples panel next to it and the
artifact shows the Explore without re-running.

Contents: 4.1 chords, tangents, epigraph and the $f''$ sign for $x^a$; 4.2
surfaces plus $\lambda_{\min}(H_f)$ colouring with the kinks masked; 4.3 the
$-\log\det$ slice and the ray formula of [CO 8.3]; 4.4 the eigenvalue surfaces
and their 20-plane envelope; 4.5 $\operatorname{tr}(SX)$ on the PSD cone and
$h=-\log\det X+\operatorname{tr}(SX)$; 4.6 the [CO 9] rules and Jensen.

Section 4 numbers, for reference when re-running: 4.1 $f''$ for
$a=-1,0,0.5,1,2$ ranges over $[0.25,31.25]$, $0$, $[-0.988,-0.088]$, $0$, $2$
(convex, both, concave, both, convex). 4.2 masked kinks 81/1681 points
($\|x\|_1$), 81 ($\|x\|_\infty$), 41 ($\max$), 1 (origin, $\|x\|_2$);
$\lambda_{\min}=0$ for the piecewise-linear functions and for the rank-one 2-D
log-sum-exp, $1.423$ for $\|Ax+b\|_2^2$, $-1$ for $x_1x_2$; log-sum-exp minus
$\max$ in $[0.0025,0.6931]=\log2$; the Hessian of $\pm\log$-sum-exp at $0$ has
eigenvalues $\{0,0.5\}$ and $\{-0.5,0\}$. 4.3 formula error $7.8\times10^{-15}$,
$g''\in[1.03,143.24]$, blow-ups at $t=-1/\lambda_i$ ($\lambda=-1.150,0.522$ for
the 2×2 example). 4.4 closed form $a\pm\sqrt{x^2+y^2}$ to $4.4\times10^{-16}$,
20-plane envelope gap $0.0244$, subadditivity slack $-3.4\times10^{-4}$,
$\lambda_{\min}$ concavity slack $-2.1\times10^{-4}$, one-sided derivatives
$\pm1$ at $X=I$. 4.5 minimiser $S^{-1}$ to $1.3\times10^{-8}$,
$h=2.494696=\log\det S+2$, $\operatorname{tr}(SX)\in[1.9\times10^{-2},128.6]$
over 2000 PSD pairs, Hessian spectra $[-4.53,-1.27,-0.38]$ in $\Theta=S^{-1}$,
$[-1.68,-0.47,-0.14]$ in $\Sigma=S$, $[+0.005,+0.015,+0.053]$ at $\Sigma=4S$.
4.6 worst segment-test violation $4.4\times10^{-16}$ for $\max$, Jensen
$f(EX)=2.8577\le Ef(X)=3.5118$ with $EX=1.05$, $(h\circ g)''(0)=-2$.

The 4.2 "undefined" points are found by comparing the finite-difference
Hessian at $h$ and $h/2$; that test is what draws the kink lines, so do not
replace it with a hard-coded mask.

Section 5 is done: `notebooks/s05_linear_programming.ipynb` is executed and
validated (24 cells, 16 code, 0 error outputs, `language_info` 3.12.16, 0.6 MB).
Its three `Explain` cells are drafted and await the user's hand-editing; they
are at indices 8, 15, 23. The 5.1 rotation and the 5.3 capacity panels each have
a static small-multiples figure next to the `ipywidgets` panel, because a widget
output saves only its state.

Contents: 5.1 vertex enumeration, level lines, rotating $c$, unbounded and
infeasible variants; 5.2 standard form with three slacks, the dual by hand,
random feasible pairs and shadow prices; 5.3 the max-flow LP, the four cuts, the
dual $\mu$ that is the cut indicator, and a larger random graph.

Section 5 numbers, for reference when re-running: 5.1 vertices carry
$0,4,9,11$, optimum $(3,1)$, threshold $\arctan3=71.565051^\circ$; unbounded
status 3 (keep only $x_1\le3$), infeasible status 2 (add $x_1\ge5$), dropping
$x_1\le3$ alone gives $p^\star=12$ at $(4,0)$. 5.2 dual
$\min 4\lambda_1+6\lambda_2+3\lambda_3$ s.t.
$\lambda_1+\lambda_2+\lambda_3\ge3$, $\lambda_1+3\lambda_2\ge2$; both values
$11$; marginals $(0,0.667,2.333)$; the two `linprog` calls return different ends
of the optimal face, $(2,0,1)$ and $(0,2/3,7/3)$; $+1$ on a RHS changes
$p^\star$ by $(0,0,1)$, $-1$ by $(2,0.667,2.333)$; random pairs satisfy
$c^\top x\le10.905<11.146\le b^\top\lambda$, smallest gap $2.199$. 5.3 flow
$f=(4,2,1,3,3)=6$, cuts $6,7,9,8$, min cut $\{s\}$, $\mu=(1,1,0,0,0)$,
`networkx` agrees; the 8-node/22-edge random graph gives flow = cut = $26$. The
flow is not unique: $f_{12}=1,2,3$ with $f_{2t}=3,4,5$. No single removal of the
three original 5.1 constraints unbounds the LP, so the notebook keeps only
$x_1\le3$; the `Explain` qualifies this.

Sections 6–9 are not started; start one only when the user says so.

Note for section 2: a VS Code save on 2 Nov dropped `execution_count` on cells
3, 21 and 22 while keeping their outputs, so `validate_notebook` reported "not
executed"; the notebook was re-executed from the same sources and the printed
numbers are unchanged (2.1 `mu_hat = 0.8063`, 2.2 MSE `0.7417` vs `1.9596` at
`m = 2`, 2.4 precision form `-641.141118`, 2.5 L1 `(2.4931, 0.4321)`). Re-run
rather than trusting stored outputs if this reappears.

One section per session. Finish each section with `execute_notebook`, then
`validate_notebook`, then update the Status column above and this section:
this file is the only handoff between sessions.
