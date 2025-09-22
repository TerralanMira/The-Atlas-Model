#!/usr/bin/env python3
"""
dashboard/base.py — Visual Coherence Foundation
------------------------------------------------

A tiny, dependency-light rendering core for Atlas dashboards.

Goals
- No server, no heavy stack. Pure Python + matplotlib + numpy + Pillow(optional).
- Composable primitives (Canvas, Panel, Grid) for quick layouts.
- Drop-in helpers for common plots (line, heatmap, image tile).
- Save to disk; pages can be embedded into MkDocs or opened as static HTML.

Usage (from repo root):
    from dashboard.base import Canvas, Panel, GridLayout, plots

    # 1) Build a canvas
    cv = Canvas(width=1200, height=800, dpi=100, bgcolor="white")

    # 2) Define a grid (rows x cols)
    grid = GridLayout(rows=2, cols=2, pad=16)

    # 3) Add panels and draw
    p1 = Panel(title="Pulse Series")
    p2 = Panel(title="Layer Contribution")
    p3 = Panel(title="Self-Learning")
    p4 = Panel(title="Crystal Snapshot")

    cv.attach(grid.place(p1, row=0, col=0))
    cv.attach(grid.place(p2, row=0, col=1))
    cv.attach(grid.place(p3, row=1, col=0))
    cv.attach(grid.place(p4, row=1, col=1))

    # 4) Render some visuals
    import numpy as np
    xs = np.arange(30)
    ys = np.sin(xs / 4.0) * 0.2 + 0.6
    plots.line(p1.ax, xs, ys, xlabel="Step", ylabel="Atlas Coherence")

    vals = np.array([0.2, 0.8, 0.4, 0.6])
    plots.bars(p2.ax, ["Earth", "Crystal", "Water/Air", "Plasma"], vals, ylabel="Norm. Mean")

    sln = np.cumsum(np.random.randn(200)) / 100 + 0.5
    plots.line(p3.ax, np.arange(200), sln, xlabel="Step", ylabel="Coherence")

    # Provide a PNG path (created elsewhere) or a numpy image
    plots.image(p4.ax, "docs/assets/dashboard/crystal_lattice.png", title="Crystal Lattice")

    # 5) Save
    cv.save("docs/assets/dashboard/atlas_dashboard_page1.png")

Notes
- Fonts/colors intentionally simple and minimal (theme can be adjusted later).
- Designed to cooperate with scripts/dashboard_build.py or be used standalone.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-friendly
import matplotlib.pyplot as plt

try:
    from PIL import Image  # optional for image reading when not using plt.imread
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False


# ----------------------------
# Layout Primitives
# ----------------------------

@dataclass
class Panel:
    """
    A panel owns a matplotlib Axes and an optional title.
    You do not instantiate with an Axes; the Canvas binds it in attach().
    """
    title: str = ""
    ax: Optional[plt.Axes] = None

    def _bind(self, ax: plt.Axes):
        self.ax = ax
        if self.title:
            self.ax.set_title(self.title, fontsize=11, pad=8)


@dataclass
class GridLayout:
    """
    Simple grid layout in figure coordinates.
    - rows, cols: number of cells
    - pad: pixel padding between cells
    """
    rows: int
    cols: int
    pad: int = 12

    def place(self, panel: Panel, row: int, col: int, rowspan: int = 1, colspan: int = 1):
        """Return a BoundPanel that Canvas can attach."""
        return BoundPanel(panel, row, col, rowspan, colspan, self)


@dataclass
class BoundPanel:
    panel: Panel
    row: int
    col: int
    rowspan: int
    colspan: int
    layout: GridLayout


@dataclass
class Canvas:
    """
    A high-level figure wrapper that manages Panels and layout.
    """
    width: int = 1200
    height: int = 800
    dpi: int = 100
    bgcolor: str = "white"

    def __post_init__(self):
        self.figure = plt.figure(figsize=(self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.figure.patch.set_facecolor(self.bgcolor)
        self._attached: List[BoundPanel] = []

    def attach(self, bound: BoundPanel):
        """Attach a panel (BoundPanel) to this canvas; actual axes made on render()."""
        self._attached.append(bound)

    def render(self):
        """Create axes for each attached panel based on the grid layout."""
        for bound in self._attached:
            # compute axes rectangle for this bound
            left, bottom, w, h = self._compute_rect(bound)
            ax = self.figure.add_axes([left, bottom, w, h])
            # minimalist style
            ax.grid(True, alpha=0.12)
            ax.set_facecolor("#fafafa")
            bound.panel._bind(ax)

    def save(self, path: str | Path):
        """Render (if needed) and save PNG."""
        if not any(isinstance(a, plt.Axes) for a in self.figure.axes):
            self.render()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.figure.savefig(path, bbox_inches="tight")
        plt.close(self.figure)

    # ---- internals ----
    def _compute_rect(self, bound: BoundPanel) -> Tuple[float, float, float, float]:
        # padding in figure fraction
        pad_frac_x = bound.layout.pad / self.width
        pad_frac_y = bound.layout.pad / self.height

        # base cell width/height
        total_pad_x = pad_frac_x * (bound.layout.cols + 1)
        total_pad_y = pad_frac_y * (bound.layout.rows + 1)
        cell_w = (1.0 - total_pad_x) / bound.layout.cols
        cell_h = (1.0 - total_pad_y) / bound.layout.rows

        # starting cell left/bottom
        left = pad_frac_x + bound.col * (cell_w + pad_frac_x)
        bottom = 1.0 - (pad_frac_y + (bound.row + bound.rowspan) * (cell_h + pad_frac_y)) + pad_frac_y
        # span
        w = cell_w * bound.colspan + pad_frac_x * (bound.colspan - 1)
        h = cell_h * bound.rowspan + pad_frac_y * (bound.rowspan - 1)

        return left, bottom, w, h


# ----------------------------
# Plot Helpers
# ----------------------------

class plots:
    @staticmethod
    def line(ax: plt.Axes, x, y, xlabel: str = "", ylabel: str = "", title: Optional[str] = None):
        ax.plot(x, y)
        if title: ax.set_title(title, fontsize=11, pad=8)
        if xlabel: ax.set_xlabel(xlabel)
        if ylabel: ax.set_ylabel(ylabel)

    @staticmethod
    def bars(ax: plt.Axes, labels: List[str], values, ylabel: str = "", title: Optional[str] = None):
        idx = np.arange(len(labels))
        ax.bar(idx, values)
        ax.set_xticks(idx)
        ax.set_xticklabels(labels, rotation=12, ha="right")
        if title: ax.set_title(title, fontsize=11, pad=8)
        if ylabel: ax.set_ylabel(ylabel)

    @staticmethod
    def heatmap(ax: plt.Axes, data: np.ndarray, xlabel: str = "", ylabel: str = "", title: Optional[str] = None):
        im = ax.imshow(data, aspect="auto", origin="lower")
        ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if title: ax.set_title(title, fontsize=11, pad=8)
        if xlabel: ax.set_xlabel(xlabel)
        if ylabel: ax.set_ylabel(ylabel)

    @staticmethod
    def image(ax: plt.Axes, img: str | Path | np.ndarray, title: Optional[str] = None):
        if isinstance(img, (str, Path)):
            p = Path(img)
            if p.exists():
                try:
                    arr = plt.imread(p)
                except Exception:
                    if _HAS_PIL:
                        arr = np.asarray(Image.open(p).convert("RGBA"))
                    else:
                        raise
            else:
                # render a placeholder
                arr = np.ones((32, 32, 3), dtype=float)
        else:
            arr = img
        ax.imshow(arr)
        ax.axis("off")
        if title: ax.set_title(title, fontsize=11, pad=8)


# ----------------------------
# Convenience Builders
# ----------------------------

def build_quadrant_dashboard(
    pulse_xy: Tuple[np.ndarray, np.ndarray] | None = None,
    layer_labels_vals: Tuple[List[str], np.ndarray] | None = None,
    sln_xy: Tuple[np.ndarray, np.ndarray] | None = None,
    crystal_img: str | Path | None = None,
    out_path: str | Path = "docs/assets/dashboard/atlas_dashboard_page1.png"
):
    """
    Build a simple 2x2 dashboard image in one call.
    - TL: Pulse line
    - TR: Layer contribution bars
    - BL: Self-learning line
    - BR: Crystal snapshot
    """
    cv = Canvas(width=1400, height=900, dpi=110, bgcolor="white")
    grid = GridLayout(rows=2, cols=2, pad=16)

    p1 = Panel(title="Pulse — Atlas Coherence")
    p2 = Panel(title="Layer Contribution (normalized)")
    p3 = Panel(title="Self-Learning Coherence")
    p4 = Panel(title="Crystal Snapshot")

    cv.attach(grid.place(p1, 0, 0))
    cv.attach(grid.place(p2, 0, 1))
    cv.attach(grid.place(p3, 1, 0))
    cv.attach(grid.place(p4, 1, 1))

    # Render plots
    if pulse_xy is not None:
        x, y = pulse_xy
        plots.line(p1.ax, x, y, xlabel="Step", ylabel="Atlas Coherence")
    if layer_labels_vals is not None:
        labels, vals = layer_labels_vals
        plots.bars(p2.ax, labels, vals, ylabel="Norm. Mean")
    if sln_xy is not None:
        x, y = sln_xy
        plots.line(p3.ax, x, y, xlabel="Step", ylabel="Coherence")
    if crystal_img is not None:
        plots.image(p4.ax, crystal_img, title="Crystal Lattice")

    cv.save(out_path)
    return str(out_path)


# ----------------------------
# Minimal Self-Test (optional)
# ----------------------------

if __name__ == "__main__":
    # Generate a quick demo page with synthetic data
    xs = np.arange(30)
    ys = 0.6 + 0.2 * np.sin(xs / 5.0)

    labels = ["Earth", "Crystal", "Water/Air", "Plasma"]
    vals = np.array([0.3, 0.8, 0.5, 0.6])

    slx = np.arange(200)
    sly = 0.5 + 0.1 * np.cumsum(np.random.randn(200)) / 10

    out = build_quadrant_dashboard((xs, ys), (labels, vals), (slx, sly), crystal_img=None)
    print("Wrote", out)
