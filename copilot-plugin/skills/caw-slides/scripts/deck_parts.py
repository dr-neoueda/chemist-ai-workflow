"""スライド SVG の図形部品（caw-slides）。表・図枠・矢印・バッジ。

中央揃えのラベルは MS Gothic 1 本で tspan を使わない。変換器が中央・右揃えの ``tspan`` の幅を誤測するため。
"""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

from deck_chrome import BLUE, BODY, DIVIDER, FRAME, GREY, HAIRLINE, JP, NAVY, body_size, fmt_size, text, wash
from PIL import Image

Cell = str | tuple[str, str] | tuple[str, str, bool]  # 文字 / (文字, 色) / (文字, 色, 太字)

FRAME_PAD = 10        # 図の枠と画像のあいだ [px]
XML_SPECIAL = set("&<>\"'")   # SVG の属性で置き換えられ、svg_quality_checker が画像を見つけられなくなる


def centred(x: float, y: float, label: str, *, size: float = 15, fill: str = NAVY, bold: bool = False,
            fine: bool = False) -> str:
    """中央揃えの 1 行（フォント 1 本・tspan なし）。"""
    size = body_size(size, fine=fine)
    weight = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x}" y="{y}" font-size="{fmt_size(size)}" fill="{fill}"{weight} font-family="{JP}" '
            f'text-anchor="middle">{escape(label)}</text>')


def badge(cx: float, cy: float, label: str, *, colour: str = NAVY, r: int = 16, size: float = 19) -> str:
    """塗りの円に白い短いラベル（番号や 1 文字）。"""
    return (f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="{colour}"/>\n'
            f'    {centred(cx, cy + size * 0.36, label, size=size, fill="#FFFFFF", bold=True)}\n')


def frame(x: float, y: float, w: float, h: float, *, stroke: str = FRAME, width: float = 1,
          fill: str = "#FFFFFF") -> str:
    """細い枠。動画の置き場などに使う。"""
    return (f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"/>\n')


def figure(png: str | Path, x: float, y: float, *, w: float | None = None,
           h: float | None = None) -> tuple[str, int, int]:
    """細い枠つきの図。外形の幅か高さの片方を渡す。箱の縦横比は PNG から取るので図が歪まない。

    Parameters
    ----------
    png : str | Path
        画像のパス。SVG からは ``../images/<名前>`` で参照する。
    x, y : float
        枠の左上 [px]。
    w, h : float | None
        枠の外形の幅または高さ [px]。どちらか一方。

    Returns
    -------
    tuple[str, int, int]
        断片、外形の幅、外形の高さ。

    Raises
    ------
    ValueError
        ``w`` と ``h`` を両方渡した、または両方渡さなかった。画像の名前に ``& < > " '`` がある。
    """
    if (w is None) == (h is None):
        raise ValueError("figure: w と h のどちらか一方を渡す")
    name = Path(png).name
    if XML_SPECIAL & set(name):
        raise ValueError(f"figure: 画像の名前 {name} に記号 & < > \" ' を使わない（名前を変える）")
    with Image.open(png) as im:
        ratio = im.width / im.height
    if w is not None:
        image_w = w - 2 * FRAME_PAD
        image_h = image_w / ratio
    else:
        image_h = h - 2 * FRAME_PAD
        image_w = image_h * ratio
    outer_w, outer_h = round(image_w + 2 * FRAME_PAD), round(image_h + 2 * FRAME_PAD)
    markup = (f'    <rect x="{x}" y="{y}" width="{outer_w}" height="{outer_h}" fill="#FFFFFF" stroke="{FRAME}" '
              f'stroke-width="1"/>\n'
              f'    <image href="../images/{name}" x="{x + FRAME_PAD}" y="{y + FRAME_PAD}" '
              f'width="{image_w:.1f}" height="{image_h:.1f}" preserveAspectRatio="xMidYMid meet"/>\n')
    return markup, outer_w, outer_h


def arrow(x1: float, y1: float, x2: float, y2: float, *, colour: str = NAVY, width: float = 2.5,
          head: float = 10) -> str:
    """直線の矢印。矢じりは塗りの三角形（marker は変換器を通すと安定しない）。"""
    angle = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(angle), y2 - head * math.sin(angle)
    px, py = head * 0.55 * math.sin(angle), -head * 0.55 * math.cos(angle)
    return (f'    <line x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{colour}" stroke-width="{width}"/>\n'
            f'    <polygon points="{x2},{y2} {bx + px:.1f},{by + py:.1f} {bx - px:.1f},{by - py:.1f}" '
            f'fill="{colour}"/>\n')


def _cell(value: Cell) -> tuple[str, str, bool]:
    if isinstance(value, str):
        return value, BODY, False
    if len(value) == 2:
        return value[0], value[1], False
    return value[0], value[1], value[2]


def table(x: float, y: float, columns: list[int], head: list[str], rows: list[list[Cell]], *, width: float = 1120,
          row_h: int = 44, size: float = 16, highlight: int | None = None) -> str:
    """表。上端に紺の 2 px の線、灰色の列名、細い行間の線、薄い地の行は 1 行まで。

    Parameters
    ----------
    x, y : float
        左上 [px]。
    columns : list[int]
        各列の左端の ``x`` からの距離 [px]。
    head : list[str]
        列名。
    rows : list[list[Cell]]
        各行のセル。
    width : float
        幅 [px]。
    row_h : int
        行の高さ [px]。表の下端は ``y + 36 + row_h * len(rows)``。
    size : float
        本文の文字の大きさ [px]。
    highlight : int | None
        薄い地を敷く行の番号。

    Returns
    -------
    str
        表の断片。

    Raises
    ------
    ValueError
        行のセル数が列数と違う。
    """
    size = body_size(size)
    out = [f'    <rect x="{x}" y="{y}" width="{width}" height="2" fill="{NAVY}"/>']
    head_y = y + 28
    for offset, label in zip(columns, head, strict=True):
        out.append(f'    {text(x + offset, head_y, label, size=size, fill=GREY)}')
    row_y = y + 36
    for k, row in enumerate(rows):
        if highlight == k:
            out.append(f'    <rect x="{x}" y="{row_y}" width="{width}" height="{row_h}" fill="{wash(BLUE)}"/>')
        baseline = round(row_y + row_h / 2 + size * 0.36)
        for offset, value in zip(columns, row, strict=True):
            label, colour, bold = _cell(value)
            out.append(f'    {text(x + offset, baseline, label, size=size, fill=colour, bold=bold)}')
        row_y += row_h
        out.append(f'    <line x1="{x}" y1="{row_y}" x2="{x + width}" y2="{row_y}" stroke="{HAIRLINE}" stroke-width="1"/>')
    return "\n".join(out) + "\n"


def rule(x1: float, y1: float, x2: float, y2: float, *, colour: str = DIVIDER, width: float = 1) -> str:
    """区切り線。"""
    return f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}"/>\n'
