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
- Keep `Explain` answers short and conceptual: a few sentences that answer the
  question directly, typically $300$–$600$ characters. Do not restate the task.
- Do not justify an answer numerically and do not quote computed values or
  parameter examples in `Explain`; the numbers belong in the code, its printed
  output and the per-section reference notes below. State the reason, not the
  evidence.
- If a claim only holds on part of the parameter range, say so in one short
  clause; do not expand it into a paragraph.
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
  leave a figure the reader cannot interpret. Choose region fills against white
  — grey `0.86` reads as background, the epigraph shading is tan `#e6d3a3`.
  Label 3-D axes x, y and the quantity on the vertical axis, and label every
  colourbar with the quantity it codes.
- `ipywidgets` sliders use `continuous_update=False`: with continuous updates
  the inline backend rebuilds the whole figure at every pixel and the panel
  stutters. Build one `VBox([slider, widgets.Output()])` and redraw inside it
  with `clear_output(wait=True)` (helper `show_slider` in s04), not `interact`.
  A widget cell saves only its state, so pair it with a static small-multiples
  figure. If `metadata.widgets` goes stale — its model ids no longer match the
  `widget-view` outputs — a frontend renders the control more than once: delete
  `metadata.widgets` from the `.ipynb` and re-execute.
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
| 5 | Linear programming | 5.1–5.3 | `s05_linear_programming.ipynb` | done, Explain trimmed to brief answers |
| 6 | Quadratic programming with linear constraints | 6.1–6.2 | `s06_qp_constraints.ipynb` | done, Explain drafted (hand-edit pending) |
| 7 | The Lagrangian and the dual function | 7.1–7.5 | `s07_lagrangian_dual.ipynb` | done, Explain drafted (hand-edit pending) |
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
validated (35 cells, 22 code, 0 error outputs, `language_info` 3.12.16, 3.3 MB).
Its six `Explain` cells are drafted and await the user's hand-editing; they are
at indices 6, 12, 18, 24, 29, 34. Three widget cells (5, the $a$ of $x^a$; 17,
the $z$ of the $-\log\det$ slice; 23, the $a$ of the eigenvalue slice) save only
widget state, so each has a static small-multiples panel next to it and the
artifact shows the Explore without re-running.

Contents: 4.1 chords, tangents, epigraph and the $f''$ sign for $x^a$; 4.2
surfaces plus $\lambda_{\min}(H_f)$ colouring with the kinks masked; 4.3 the
$-\log\det$ slice and the ray formula of [CO 8.3]; 4.4 the eigenvalue surfaces
in 2-D and 3-D plus their 20-plane envelope; 4.5 $\operatorname{tr}(SX)$ on the
PSD cone and $h=-\log\det X+\operatorname{tr}(SX)$; 4.6 the [CO 9] rules and
Jensen.

4.4 uses the notebook variable $a$ for the slice ($X_{11}=a+x$, $X_{22}=a-x$,
$X_{12}=X_{21}=y$); the static panels are drawn at $a=0.6$. Cell 21 defines
`plot_lambda_surfaces(a)` and draws $\lambda_{\max}=a+r$, $\lambda_{\min}=a-r$
with $r=\|(x,y)\|$, plus a red base contour at $\lambda_{\min}=0$; the slider cell
23 calls the same function, so dragging $a$ redraws the 3-D panels (one redraw
per release, ~$0.1$ s each). mathtext has no `smallmatrix`, so the slice is
printed as $X_{ij}$ entries. Every 3-D axes is labelled x, y and the plotted
quantity, and every colourbar is labelled too.

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
Its three `Explain` cells (8, 15, 23) are now short conceptual answers written
to the brief-explanation rule; the numbers below are reference material only.
The 5.1 rotation and the 5.3 capacity panels each have a static small-multiples
figure next to the `ipywidgets` panel, because a widget output saves only its
state; both slider cells follow the s04/s06 Output pattern (one
`widgets.Output()`, redraw with `clear_output(wait=True)`,
`continuous_update=False`). The 5.1 static cell (5) defines
`optimal_face51(c)` with its own grid, so it does not depend on cell 4; the
slider cell (6) highlights the optimal edge in red whenever $c$ is exactly
normal to it — at $\theta=0$ on $x_1\le3$ and at $\theta=\arctan3$ on
$x_1+3x_2\le6$, while $\theta=71.5^\circ$ correctly degenerates to the vertex
(verified in a scratch kernel).

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

Section 6 is done: `notebooks/s06_qp_constraints.ipynb` is executed and
validated (16 cells, 10 code, 0 error outputs, `language_info` 3.12.16, 0.83 MB).
Its two `Explain` cells are at indices 10 (6.1) and 15 (6.2), both short
conceptual answers. The 6.1 code enumerates active sets, solves the
equality-constrained KKT system and checks stationarity, primal/dual
feasibility and complementary slackness against SLSQP; the 6.2 code solves the
KKT system, compares with `trust-constr`, checks symmetry and inertia, and
recovers the minimum-norm solution for $P=2I$, $q=0$. Cell 9 is the five-slider
`ipywidgets` panel for $\lambda_1,\lambda_2,\theta,q_1,q_2$; cells 7 and 8 are
the static small-multiples figures for moving $q$ and for $P$ becoming PSD.

Section 6 numbers, for reference when re-running: 6.1 base $P$ has eigenvalues
$1,3$ and the unconstrained minimiser $(4.2,2.4)$ is outside the pentagon; the
constrained optimum is $(2.2625,1.4750)$ on $2x_1+x_2=6$ with multiplier
$0.9605$ and value $-9.554967$. For the same rotated $P$ with $\lambda_2=0$ the
optimum is $(2,2)$ with both $2x_1+x_2=6$ and $x_1+2x_2=6$ active. 6.2 KKT and `trust-constr` agree to $7.3\times10^{-11}$; KKT
eigenvalues $[-2.3846,-0.7537,0.7429,1.2901,2.3043,4.2870,8.7646]$, so the
matrix is symmetric indefinite; the $P=2I$, $q=0$ solution matches
$A^\top(AA^\top)^{-1}b$ to $2.8\times10^{-17}$ and is orthogonal to
$\operatorname{null}(A)$ to $1.5\times10^{-17}$.

Section 7 is done: `notebooks/s07_lagrangian_dual.ipynb` is executed and
validated (23 cells, 11 code, 0 error outputs, `language_info` 3.12.16, 1.08 MB).
Its five `Explain` cells are drafted and await the user's hand-editing; they are
at indices 8 (7.1), 11 (7.2), 14 (7.3), 17 (7.4), 22 (7.5). Cell 21 is the
two-slider (`a_1`,`a_2`) `ipywidgets` panel for the halfspace projection (path
$x(\lambda)$ plus $g(\lambda)$ against $p^\star$); it is paired with the static
small-multiples figure in cell 20 ($a$ outside / $a$ inside / the two-halfspace
surface), because a widget output saves only its state. The widget cell follows
the s04/s05/s06 Output pattern and its saved output leaves no `metadata.widgets`.

Contents: 7.1 the surface $L(x,\lambda)$ over $x\in[-4,4],\lambda\in[0,3]$, the
curves $L(\cdot,\lambda)$ with the extended objective $f_0+I_{\mathbb{R}_-}$, and
the Explore ($\lambda=10,100$; $\lambda f_1$ vs the indicator). 7.2 the dual
$g(\lambda)=\inf_x L$ numerically and analytically with $p^\star$, and each curve
marked at its minimiser. 7.3 the set $G=\{(f_1,f_0)\}$ in the $(u,t)$ plane with
supporting lines $t+\lambda u=g(\lambda)$, for the convex example, the non-convex
$f_0=x^4-3x^2+x$ with the deep well feasible, and the same $f_0$ with a mirrored
constraint that makes the gap visible. 7.4 the three formulations
$1-x$, $-\log x$, $(1-x)^3$ of $x\ge1$: $L$-curves and duals with $p^\star$. 7.5
the closed-form projection dual, verified against SLSQP for one and two halfspaces.

Section 7 numbers, for reference when re-running: 7.1 $\max|g_{\rm num}-g_{\rm an}|
=1.3\times10^{-15}$, $\sup_{\lambda\ge0}\lambda f_1=0$ on $x\le0$ and $+\infty$ on
$x>0$. 7.2 $d^\star=g(1)=0=p^\star$, gap $0$. 7.3 convex gap $0$; deep-well-feasible
$p^\star=d^\star=-3.5139$ (constraint inactive); mirrored case $p^\star=-1.0702$,
$d^\star=-1.7573$, gap $0.6870$. 7.4 (a) $g=\lambda-\lambda^2/4$, (b)
$g=\tfrac\lambda2-\tfrac\lambda2\log\tfrac\lambda2$, both with $\lambda^\star=2$,
$d^\star=1$; (c) grid $g(4)$ runs $-4.6\times10^{2}\to-8.2\times10^{5}$ as the scan
range widens, i.e.\ $-\infty$, so $d^\star=0$ and the gap is $1$. 7.5 outside
$a=(3.5,2.5)$: $\lambda^\star=3$, $x^\star=(2,1)$, $g=p^\star=4.5$; inside
$a=(0.8,0.5)$: $\lambda^\star=0$, $x^\star=a$, gap $0$; two halfspaces
$C=[[1,1],[0,1]]$, $d=(3,2)$ give one active $\lambda^\star=(0.7,0)$ and vertex
$\lambda^\star=(2,2)$, both matching the SLSQP projection to $\le3\times10^{-7}$
with gap $\le10^{-13}$. (The two-halfspace Gram is $CC^\top$, not $C^\top C$; the
test matrix was symmetric so it hid the error until an asymmetric pair exposed it.)

Sections 8–9 are not started; start one only when the user says so.

Note for section 2: a VS Code save on 2 Nov dropped `execution_count` on cells
3, 21 and 22 while keeping their outputs, so `validate_notebook` reported "not
executed"; the notebook was re-executed from the same sources and the printed
numbers are unchanged (2.1 `mu_hat = 0.8063`, 2.2 MSE `0.7417` vs `1.9596` at
`m = 2`, 2.4 precision form `-641.141118`, 2.5 L1 `(2.4931, 0.4321)`). Re-run
rather than trusting stored outputs if this reappears.

One section per session. Finish each section with `execute_notebook`, then
`validate_notebook`, then update the Status column above and this section:
this file is the only handoff between sessions.
