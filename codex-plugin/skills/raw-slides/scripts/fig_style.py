#!/usr/bin/env python3
"""スライドに載せる matplotlib 図の共通書式（raw-slides）。

図の 1 inch をスライドの 100 px にそろえる。スライドに貼る箱の px をそのまま図の大きさにし、文字もスライドの px で
指定すれば、貼った後の文字の大きさが SVG の文字とそろう。目盛りは縦横とも内向き。
英数は Arial、和文は MS ゴシック。色は ``deck_chrome`` の定数をそのまま使う。

Usage
-----
    import fig_style as fs
    fs.setup()
    fig = fs.figure(640, 360)
    ax = fig.add_subplot()
    ...
    fs.style_axes(ax)
    fs.save(fig, "images/fig_rate.png")
"""
from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from deck_chrome import BLUE, BODY, DIVIDER, GOLD, GREEN, GREY, NAVY, RED  # noqa: E402,F401
from matplotlib import font_manager  # noqa: E402

MS_GOTHIC_PATHS = (
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msgothic.ttc",
    Path("/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts/msgothic.ttc"),
)
FALLBACK_FAMILIES = ("Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Noto Sans CJK JP", "IPAexGothic")
PX_PER_INCH = 100          # 図の 1 inch = スライドの 100 px
PT_PER_PX = 72 / PX_PER_INCH
DPI = 300                  # スライドの 1 px = 画像の 3 px


def pt(px: float) -> float:
    """スライドの px で書いた文字の大きさを matplotlib の pt にする。"""
    return px * PT_PER_PX


def find_japanese_font(paths: Iterable[Path] | None = None) -> Path | None:
    """MS ゴシックのファイルを探す。無ければ ``None``。"""
    for path in (MS_GOTHIC_PATHS if paths is None else paths):
        if Path(path).exists():
            return Path(path)
    return None


def has_ms_gothic() -> bool:
    """matplotlib が MS ゴシックをすでに知っているか。"""
    return any(f.name == "MS Gothic" for f in font_manager.fontManager.ttflist)


def setup() -> None:
    """英数 Arial・和文 MS ゴシックを既定にする。MS ゴシックが無ければ警告を出して代わりの和文フォントを使う。"""
    path = None if has_ms_gothic() else find_japanese_font()
    if path is not None:
        font_manager.fontManager.addfont(str(path))
    if has_ms_gothic():
        families = ["Arial", "MS Gothic"]
    else:
        print("[fig_style] MS ゴシックが見つからない。図の和文は別のフォントになり、スライドの文字と字形が変わる",
              file=sys.stderr)
        families = ["Arial", *FALLBACK_FAMILIES]
    matplotlib.rcParams.update({
        "font.family": families,   # 1 文字ずつ順に探す
        "axes.edgecolor": BODY,
        "axes.linewidth": 1.0,
        "xtick.color": BODY,
        "ytick.color": BODY,
        "text.color": NAVY,
        "savefig.facecolor": "white",
    })


def style_axes(ax: plt.Axes, *, label_px: float = 14) -> None:
    """目盛りを縦横とも内向きにする。"""
    ax.tick_params(direction="in", which="both", labelsize=pt(label_px))


def figure(width_px: float, height_px: float) -> plt.Figure:
    """スライドに貼る箱と同じ px の図。"""
    return plt.figure(figsize=(width_px / PX_PER_INCH, height_px / PX_PER_INCH), dpi=DPI)


def save(fig: plt.Figure, out: str | Path) -> Path:
    """余白を足さずに保存する（箱の px と図の px を一致させるため ``bbox_inches`` は使わない）。"""
    out = Path(out)
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    return out
