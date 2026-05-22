"""Schematic research icons + composition builders for caw-slides.

化学・研究発表スライド向けの「概念イラスト」を一定品質で量産するための再利用
モジュール。matplotlib patches で描く線画アイコン群と、それらを並べる 3 つの
構図ビルダー（hub / cycle / converging）を提供する。

設計方針（style-guide §11bis に対応）:
- 各アイコンは ``icon(ax, x, y, s=1.0, color=...)`` の共通シグネチャ。``s`` は
  おおよその直径（データ座標 ~1.0）で、どの図でも同縮尺で混在できる。
- 構図ビルダーは matplotlib Figure を組んで PNG を保存し、``Path`` を返す。
  返り値を ``pptx_helpers.add_picture_fit`` に渡してスライドへ配置する。
- 配色は ``pptx_helpers.CATEGORICAL_HEX`` のカテゴリカル 7 色に揃える
  （青一色を避ける §0 ルール）。

イラスト vs チャートの使い分けは style-guide §11bis を参照。能力・規模・桁の
比較は本モジュールではなく定量チャート（log-log マップ等）で描くこと。
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import matplotlib

# headless PNG 出力専用モジュールなので Agg backend を使う（未設定時のみ静かに設定）。
if matplotlib.get_backend().lower() != "agg":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import (  # noqa: E402
    Circle,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)

import pptx_helpers as _h  # noqa: E402

# カテゴリカル配色（pptx_helpers と一致）
BLUE, ORANGE, GREEN, RED, CYAN, PURPLE, AMBER = _h.CATEGORICAL_HEX[:7]
GREY = "#888888"
DARK = "#222222"
NAVY = "#27508F"

# 構造線・補助の色（淡色）
_SPOKE = "#C9D3E0"
_ARC = "#9CC3A6"
_ARC_HEAD = "#6FAE83"
_CONVERGE = "#E08A8A"


# ---------------------------------------------------------------------------
# アイコン（線画 schematic）
# ---------------------------------------------------------------------------

def icon_researcher(ax: Axes, x: float, y: float, s: float = 1.0,
                    color: str = BLUE) -> None:
    """人（研究者・担当者）。頭の円 + 肩の台形。"""
    ax.add_patch(Circle((x, y + 0.55 * s), 0.24 * s, fc=color, ec="none", zorder=5))
    ax.add_patch(Polygon(
        [(x - 0.42 * s, y - 0.55 * s), (x + 0.42 * s, y - 0.55 * s),
         (x + 0.26 * s, y + 0.28 * s), (x - 0.26 * s, y + 0.28 * s)],
        closed=True, fc=color, ec="none", zorder=4))


def icon_flask(ax: Axes, x: float, y: float, s: float = 1.0,
               color: str = GREEN, fill_frac: float = 0.45) -> None:
    """三角フラスコ（実験・測定）。``fill_frac`` で液量を変える。"""
    ax.add_patch(Rectangle((x - 0.08 * s, y + 0.25 * s), 0.16 * s, 0.33 * s,
                           fc="none", ec=color, lw=2.4, zorder=5))
    body = [(x - 0.08 * s, y + 0.25 * s), (x - 0.34 * s, y - 0.45 * s),
            (x + 0.34 * s, y - 0.45 * s), (x + 0.08 * s, y + 0.25 * s)]
    ax.add_patch(Polygon(body, closed=True, fc="white", ec=color, lw=2.4, zorder=4))

    def half_w(yy: float) -> float:
        t = (yy - (y - 0.45 * s)) / (0.70 * s)
        return 0.34 * s + t * (0.08 * s - 0.34 * s)

    ly = y - 0.45 * s + 0.70 * s * fill_frac
    hw = half_w(ly)
    ax.add_patch(Polygon(
        [(x - 0.34 * s, y - 0.45 * s), (x + 0.34 * s, y - 0.45 * s),
         (x + hw, ly), (x - hw, ly)],
        closed=True, fc=color, ec="none", alpha=0.45, zorder=3))
    ax.plot([x - 0.13 * s, x + 0.13 * s], [y + 0.58 * s, y + 0.58 * s],
            color=color, lw=3.0, zorder=6)


def icon_molecule(ax: Axes, x: float, y: float, s: float = 1.0,
                  color: str = PURPLE) -> None:
    """ベンゼン環風の分子（計算・分子）。"""
    r = 0.36 * s
    pts = [(x + r * np.cos(a), y + r * np.sin(a))
           for a in np.linspace(np.pi / 2, 2 * np.pi + np.pi / 2, 7)]
    for i in range(6):
        ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                color=color, lw=2.2, zorder=4)
    for i in range(6):
        ax.add_patch(Circle(pts[i], 0.085 * s, fc=color, ec="none", zorder=5))
    ax.add_patch(Circle((x, y), 0.19 * s, fc="none", ec=color, lw=1.4, zorder=4))


def icon_document(ax: Axes, x: float, y: float, s: float = 1.0,
                  color: str = ORANGE) -> None:
    """文書（論文・申請書）。"""
    w, hh = 0.58 * s, 0.76 * s
    ax.add_patch(FancyBboxPatch((x - w / 2, y - hh / 2), w, hh,
                                boxstyle="round,pad=0.012", fc="white",
                                ec=color, lw=2.4, zorder=4))
    for dy in (0.22, 0.07, -0.08, -0.23):
        ax.plot([x - 0.17 * s, x + 0.17 * s], [y + dy * s, y + dy * s],
                color=color, lw=1.7, zorder=5)


def icon_chart(ax: Axes, x: float, y: float, s: float = 1.0,
               color: str = CYAN) -> None:
    """棒グラフ（データ整理・解析）。"""
    for i, hgt in enumerate((0.30, 0.55, 0.40, 0.72)):
        bx = x - 0.30 * s + i * 0.20 * s
        ax.add_patch(Rectangle((bx, y - 0.40 * s), 0.12 * s, hgt * s,
                               fc=color, ec="none", zorder=5))
    ax.plot([x - 0.40 * s, x + 0.42 * s], [y - 0.40 * s, y - 0.40 * s],
            color=GREY, lw=1.6, zorder=4)


def icon_slides(ax: Axes, x: float, y: float, s: float = 1.0,
                color: str = AMBER) -> None:
    """発表スライド（提示用ボード）。"""
    w, hh = 0.74 * s, 0.50 * s
    top = y + 0.10 * s
    ax.add_patch(FancyBboxPatch((x - w / 2, top - hh), w, hh,
                                boxstyle="round,pad=0.012", fc="white",
                                ec=color, lw=2.4, zorder=4))
    for i, hgt in enumerate((0.12, 0.22, 0.16)):
        bx = x - 0.18 * s + i * 0.16 * s
        ax.add_patch(Rectangle((bx, top - hh + 0.07 * s), 0.085 * s, hgt * s,
                               fc=color, ec="none", zorder=5))
    ax.plot([x, x], [top - hh, y - 0.32 * s], color=color, lw=2.2, zorder=4)
    ax.plot([x - 0.15 * s, x + 0.15 * s], [y - 0.32 * s, y - 0.32 * s],
            color=color, lw=2.2, zorder=4)


def icon_gear(ax: Axes, x: float, y: float, s: float = 1.0,
              color: str = BLUE) -> None:
    """歯車（計算・処理）。"""
    ax.add_patch(Circle((x, y), 0.29 * s, fc="white", ec=color, lw=2.6, zorder=4))
    ax.add_patch(Circle((x, y), 0.10 * s, fc=color, ec="none", zorder=5))
    for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        ax.plot([x + 0.29 * s * np.cos(a), x + 0.42 * s * np.cos(a)],
                [y + 0.29 * s * np.sin(a), y + 0.42 * s * np.sin(a)],
                color=color, lw=3.0, zorder=4)


def icon_magnifier(ax: Axes, x: float, y: float, s: float = 1.0,
                   color: str = RED) -> None:
    """ルーペ + チェック（レビュー・検証）。"""
    ax.add_patch(Circle((x - 0.05 * s, y + 0.05 * s), 0.21 * s, fc="white",
                        ec=color, lw=2.6, zorder=5))
    ax.plot([x + 0.10 * s, x + 0.30 * s], [y - 0.10 * s, y - 0.30 * s],
            color=color, lw=3.2, zorder=4)
    ax.plot([x - 0.14 * s, x - 0.05 * s, x + 0.09 * s],
            [y + 0.05 * s, y - 0.04 * s, y + 0.16 * s],
            color=color, lw=2.2, zorder=6)


def icon_laptop(ax: Axes, x: float, y: float, s: float = 1.0,
                color: str = DARK, screen: str = "#EAF2FC") -> None:
    """ノート PC（CLI・ツール）。"""
    w, hh = 0.74 * s, 0.48 * s
    base = y - hh / 2 + 0.12 * s
    ax.add_patch(FancyBboxPatch((x - w / 2, base), w, hh, boxstyle="round,pad=0.012",
                                fc=screen, ec=color, lw=2.4, zorder=4))
    ax.add_patch(Polygon(
        [(x - w / 2 - 0.10 * s, base), (x + w / 2 + 0.10 * s, base),
         (x + w / 2 + 0.20 * s, base - 0.12 * s),
         (x - w / 2 - 0.20 * s, base - 0.12 * s)],
        closed=True, fc=color, ec="none", zorder=5))


def icon_sparkle(ax: Axes, x: float, y: float, s: float = 1.0,
                 color: str = AMBER) -> None:
    """きらめき（AI・強調・成果）。"""
    pts = [(x, y + 0.42 * s), (x + 0.11 * s, y + 0.11 * s), (x + 0.42 * s, y),
           (x + 0.11 * s, y - 0.11 * s), (x, y - 0.42 * s), (x - 0.11 * s, y - 0.11 * s),
           (x - 0.42 * s, y), (x - 0.11 * s, y + 0.11 * s)]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="none", zorder=6))


#: 名前 → アイコン関数の登録表（文字列指定したいとき用）
ICONS: dict[str, Callable[..., None]] = {
    "researcher": icon_researcher, "flask": icon_flask, "molecule": icon_molecule,
    "document": icon_document, "chart": icon_chart, "slides": icon_slides,
    "gear": icon_gear, "magnifier": icon_magnifier, "laptop": icon_laptop,
    "sparkle": icon_sparkle,
}


# ---------------------------------------------------------------------------
# 共通ヘルパ
# ---------------------------------------------------------------------------

def label(ax: Axes, x: float, y: float, text: str, color: str = DARK,
          size: float = 17, weight: str = "bold") -> None:
    """アイコンの主ラベル（太字）。既定 17 ≒ スライド本文 20pt 相当（配置縮小込み）。"""
    ax.text(x, y, text, ha="center", va="center", fontsize=size,
            fontweight=weight, color=color, zorder=10)


def sublabel(ax: Axes, x: float, y: float, text: str, color: str = GREY,
             size: float = 13) -> None:
    """アイコンの補助ラベル（細字）。既定 13 ≒ 本文よりやや小。"""
    ax.text(x, y, text, ha="center", va="center", fontsize=size,
            fontweight="normal", color=color, zorder=10)


def new_figure(width: float, height: float) -> tuple[Figure, Axes]:
    """軸を消した等スケールの Figure を作る（日本語フォント設定込み）。"""
    _h._ensure_matplotlib_japanese()
    fig, ax = plt.subplots(figsize=(width, height), dpi=150)
    ax.axis("off")
    ax.set_aspect("equal")
    return fig, ax


def save_figure(fig: Figure, out_path: str | Path) -> Path:
    """透過 PNG として保存し、Path を返す（``add_picture_fit`` に渡す）。

    保存に失敗しても Figure は必ず閉じる（リーク防止）。``out_path`` は ``.png``。
    """
    out = Path(out_path)
    try:
        if out.suffix.lower() != ".png":
            raise ValueError(f"out_path must end with .png, got: {out.suffix!r}")
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout(pad=0.2)
        fig.savefig(out, dpi=150, transparent=True)
    finally:
        plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 構図ビルダー（PNG を返す）
# ---------------------------------------------------------------------------

def hub_diagram(center_label: str,
                nodes: list[tuple[str, str | None, Callable[..., None], str]],
                out_path: str | Path, *, center_sub: str | None = None,
                center_color: str = NAVY,
                figsize: tuple[float, float] = (7.6, 4.6), radius: float = 2.45,
                y_squash: float = 0.82, icon_size: float = 0.78) -> Path:
    """中心ノード + 放射状の周辺ノード（system-of-parts / 部署図）。

    Parameters
    ----------
    center_label : str
        中央ボックスの文字（例 "秘書"）。
    nodes : list of (label, sub, icon_fn, color)
        周辺ノード。``sub`` は補助ラベル（不要なら ``None``）。
    out_path : str or Path
        保存先 PNG パス。
    """
    if not nodes:
        raise ValueError("hub_diagram requires at least one node")
    fig, ax = new_figure(*figsize)
    try:
        angles = np.linspace(90, 90 - 360, len(nodes), endpoint=False)
        for (name, sub, icon, color), a in zip(nodes, angles):
            ar = np.deg2rad(a)
            cx, cy = radius * np.cos(ar), radius * y_squash * np.sin(ar)
            ax.plot([0, cx * 0.72], [0, cy * 0.72], color=_SPOKE, lw=2.4, zorder=1)
            icon(ax, cx, cy, s=icon_size, color=color)
            label(ax, cx, cy - 0.6, name, color=color, size=17)
            if sub:
                sublabel(ax, cx, cy - 0.95, sub, color=GREY, size=13)
        bw, bh = 1.8, 0.96
        ax.add_patch(FancyBboxPatch((-bw / 2, -bh / 2), bw, bh,
                                    boxstyle="round,pad=0.02", fc=center_color,
                                    ec="none", zorder=6))
        label(ax, 0, 0.14 if center_sub else 0.0, center_label, color="white", size=18)
        if center_sub:
            sublabel(ax, 0, -0.24, center_sub, color="#CBD6EA", size=13)
        m = radius + 0.95
        ax.set_xlim(-m, m)
        ax.set_ylim(-(radius * y_squash + 1.3), radius * y_squash + 0.9)
    except BaseException:
        plt.close(fig)
        raise
    return save_figure(fig, out_path)


def cycle_diagram(stations: list[tuple[str, str | None, Callable[..., None], str]],
                  out_path: str | Path, *, center_label: str | None = None,
                  center_sub: str | None = None,
                  figsize: tuple[float, float] = (7.6, 4.4), radius: float = 2.05,
                  gap_deg: float = 20, icon_size: float = 0.72) -> Path:
    """円環の各駅 + 駅間の隙間に弧矢印（時計回りの研究サイクル）。

    弧矢印は駅の角度 ± ``gap_deg`` を空けて隣駅手前に着地させる。駅を貫かない。
    ``center_label`` / ``center_sub`` は中央の 2 行タイトル（例 "研究" / "サイクル"）で、
    意図的に同じ大きさ・色で重ねる（補助ラベルではない）。
    """
    if not stations:
        raise ValueError("cycle_diagram requires at least one station")
    fig, ax = new_figure(*figsize)
    try:
        n = len(stations)
        base = np.linspace(90, 90 - 360, n, endpoint=False)
        step = 360 / n
        if gap_deg >= step / 2:
            raise ValueError(
                f"gap_deg ({gap_deg}) must be < half the station spacing "
                f"(360/{n}/2 = {step / 2:.1f}); reduce gap_deg or stations")
        for ang in base:
            a_s, a_e = ang - gap_deg, ang - step + gap_deg
            th = np.deg2rad(np.linspace(a_s, a_e, 24))
            ax.plot(radius * np.cos(th), radius * np.sin(th), color=_ARC, lw=2.8, zorder=1)
            ae, ab = np.deg2rad(a_e), np.deg2rad(a_e + 4)
            ax.add_patch(FancyArrowPatch(
                (radius * np.cos(ab), radius * np.sin(ab)),
                (radius * np.cos(ae), radius * np.sin(ae)),
                arrowstyle="-|>", mutation_scale=16, color=_ARC_HEAD, lw=0.6, zorder=2))
        for (name, sub, icon, color), ang in zip(stations, base):
            a = np.deg2rad(ang)
            cx, cy = radius * np.cos(a), radius * np.sin(a)
            icon(ax, cx, cy, s=icon_size, color=color)
            label(ax, cx, cy - 0.58, name, color=color, size=17)
            if sub:
                sublabel(ax, cx, cy - 0.88, sub, color=GREY, size=13)
        if center_label:
            label(ax, 0, 0.2 if center_sub else 0.0, center_label, color=NAVY, size=18)
        if center_sub:
            label(ax, 0, -0.3, center_sub, color=NAVY, size=18)
        m = radius + 0.9
        ax.set_xlim(-m, m)
        ax.set_ylim(-m, m)
    except BaseException:
        plt.close(fig)
        raise
    return save_figure(fig, out_path)


def converging_diagram(center: tuple[Callable[..., None], str],
                       items: list[tuple[str, Callable[..., None], str]],
                       out_path: str | Path, *, center_label: str | None = None,
                       figsize: tuple[float, float] = (7.6, 4.3),
                       center_size: float = 1.2) -> Path:
    """上弧に並ぶ要素が中心の人物へ矢印で収束（負荷・要求が押し寄せる図）。

    矢印は中心の頭の周囲（リム）に角度を散らして着地し、矢じりが重ならない。
    """
    if not items:
        raise ValueError("converging_diagram requires at least one item")
    fig, ax = new_figure(*figsize)
    try:
        center_icon, center_color = center
        rh_y = -0.55
        head = (0.0, rh_y + 0.55 * center_size)
        rim = 0.46 * center_size
        degs = np.array([90.0]) if len(items) == 1 else np.linspace(162, 18, len(items))
        rx, ry, cy0 = 3.0, 1.78, 0.55
        for (name, icon, color), deg in zip(items, degs):
            a = np.deg2rad(deg)
            cx, cy = rx * np.cos(a), cy0 + ry * np.sin(a)
            ux, uy = cx - head[0], cy - head[1]
            d = (ux * ux + uy * uy) ** 0.5
            ux, uy = ux / d, uy / d
            start = (cx - ux * 0.58, cy - uy * 0.58)
            end = (head[0] + ux * rim, head[1] + uy * rim)
            ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=17,
                                         color=_CONVERGE, lw=2.1, zorder=1))
            icon(ax, cx, cy, s=0.7, color=color)
            label(ax, cx, cy + 0.58, name, color=color, size=17)
        center_icon(ax, 0, rh_y, s=center_size, color=center_color)
        if center_label:
            label(ax, 0, rh_y - 0.92, center_label, color=center_color, size=17)
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-1.75, 2.8)
    except BaseException:
        plt.close(fig)
        raise
    return save_figure(fig, out_path)
