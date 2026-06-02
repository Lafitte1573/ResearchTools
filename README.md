# research-skills

A collection of Claude Code skills for research-paper figures and charts. Each skill turns a visual input into runnable, editable source code via a tight **draft → render → compare → refine** loop — the fastest way to a faithful reproduction is to actually run the script and iterate on the rendered output.

| Skill | What it does | Best for |
|---|---|---|
| [**image-to-latex**](image-to-latex/) | Image → compilable LaTeX (`.tex` → `.pdf` → `.png`) | Taxonomy trees, math, tables, code blocks, flowcharts, theorem boxes, mixed pages |
| [**image-to-chart**](image-to-chart/) | Chart image → runnable Python (`.py` → `.png`) | Scatter, bar, line, heatmap, distribution, multi-panel grids, radar / network / PCA |

## Why a feedback loop matters

Matplotlib, seaborn, and LaTeX are large, opinionated tools with many equivalent ways to draw the same chart. Tiny differences in `cmap`, `alpha`, `edgecolor`, package choice, or `tight_layout` vs. `constrained_layout` produce visibly different output. **The fastest path to a good result is to actually run the script, look at the rendered image, and iterate.** Both skills' compile scripts are sub-second — use them freely. Most figures converge in 2–4 iterations.

---

## image-to-latex

Turn any image into compilable LaTeX. Triggers on *“recreate this in LaTeX”*, *“用 LaTeX 写出来”*, *“复现这张图”*, *“重画”*.

### Example: paper taxonomy → LaTeX forest

A typical use case is reproducing a hierarchical taxonomy figure from a survey paper. Source: a phone-camera shot of a survey figure.

![LLM Role-Playing taxonomy](image-to-latex/examples/taxonomy-llm-role-playing.png)

Claude reads `references/tree.md`, drafts a `.tex` using the `forest` package, and runs:

```bash
$ ./image-to-latex/scripts/compile_and_preview.sh tree.tex
[1/1]  pdflatex tree.tex
Output written on tree.pdf (1 page, 63185 bytes).
[2/2]  sips -s format png tree.pdf --out tree.png
tree.png  ✓
```

The result is a rendered LaTeX figure you can drop into your own paper. Source: [`taxonomy-llm-role-playing.tex`](image-to-latex/examples/taxonomy-llm-role-playing.tex) (4.6 KB, compiles in ~1 s with `pdflatex`).

### Example: LLMs survey taxonomy (deeper tree, 4 L1 branches)

![LLMs survey taxonomy](image-to-latex/examples/taxonomy-llms-survey.png)

Same `forest` + `xcolor` machinery, just different colors and a deeper tree. Source: [`taxonomy-llms-survey.tex`](image-to-latex/examples/taxonomy-llms-survey.tex) (3.8 KB).

See the full [image-to-latex README](image-to-latex/README.md) for the worked-example tree, the visual feedback loop diagram, and the per-content-type reference table (tree, table, math, code-and-quote, flowchart, mixed-page).

---

## image-to-chart

Turn any chart image into runnable Python (matplotlib + seaborn). Triggers on *“recreate this chart in Python”*, *“reproduce this figure with matplotlib”*, *“用 Python 复现这张图”*, *“写代码画出这个图”*, *“给我 plot 代码”*.

### Example: scatter + correlation heatmap (2-panel)

Source: a Valorant-style performance chart with a viridis scatter on top and a 9×9 Reds correlation matrix on the bottom.

![Scatter + heatmap](image-to-chart/examples/chart_scatter_heatmap.png)

Claude reads `references/scatter.md` and `references/heatmap.md`, drafts `chart.py` using `plt.subplots(2, 1, ...)`, and runs:

```bash
$ ./image-to-chart/scripts/compile_and_preview.sh chart.py
[1/1]  python3 chart.py
✓ output.png  (1420x1823, 200 dpi)
```

Source: [`chart_scatter_heatmap.py`](image-to-chart/examples/chart_scatter_heatmap.py) (3.5 KB).

### Example: horizontal bar + lollipop (PUBG weapon stats)

Source: a 2-panel figure with 15 weapons — Damage Per Second (left, colored by weapon type) and Kill Efficiency (right, lollipop chart colored by fire mode).

![Bar + lollipop](image-to-chart/examples/chart_bar_lollipop.png)

Source: [`chart_bar_lollipop.py`](image-to-chart/examples/chart_bar_lollipop.py) (5.4 KB).

See the full [image-to-chart README](image-to-chart/README.md) for the worked examples, the visual feedback loop diagram, and the per-chart-type reference table (scatter, bar, line, heatmap, distribution, multi-panel, specialized, styling).

---

## Installation

Each skill is a self-contained directory. Pick one (or both) and copy it into `~/.claude/skills/`:

```bash
# from the cloned repo
cp -r image-to-latex    ~/.claude/skills/
cp -r image-to-chart    ~/.claude/skills/

# OR from a packaged .skill zip
unzip image-to-chart.skill -d ~/.claude/skills/image-to-chart
```

Claude Code picks them up automatically — no restart required.

### Python packages (for image-to-chart)

```bash
pip install matplotlib seaborn pandas numpy
# Optional, only if the figure needs them:
pip install networkx scikit-learn
```

### TeX packages (for image-to-latex)

```bash
# macOS
brew install --cask mactex
# Linux
sudo apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
```

---

## Repository layout

```
research-skills/
├── image-to-latex/
│   ├── SKILL.md                # the manifest Claude reads to decide when to trigger
│   ├── README.md               # full description, examples, feedback loop
│   ├── references/             # per-content-type guides (tree, table, math, ...)
│   ├── scripts/                # compile_and_preview.sh + grade.py
│   ├── assets/                 # starting templates
│   └── examples/               # worked end-to-end reproductions (.tex + .png)
└── image-to-chart/
    ├── SKILL.md
    ├── README.md
    ├── references/             # per-chart-type guides (scatter, bar, line, ...)
    ├── scripts/                # compile_and_preview.sh + grade.py
    ├── assets/                 # starting templates (.py)
    └── examples/               # worked end-to-end reproductions (.py + .png)
```

## License

MIT.
