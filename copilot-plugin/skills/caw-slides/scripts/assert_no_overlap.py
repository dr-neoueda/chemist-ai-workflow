#!/usr/bin/env python3
"""SVG レイアウト衝突ゲート（caw-slides ``assert_no_overlap``）。

各スライド SVG のテキスト行について、近似バウンディングボックスを起こし
(1) キャンバス外へのはみ出し (2) テキスト同士の有意な重なり を検出する。
図パネル (``<rect>``) の上にテキストを載せる意図的な配置は誤検出しないよう、
**テキスト行同士** の重なりのみを対象とする。

Usage
-----
    python3 assert_no_overlap.py <path>       # .svg ファイル or SVG を含むディレクトリ

判定ロジックのテストは ``tests/test_assert_no_overlap.py`` (pytest) を参照。

Notes
-----
文字幅はフォントメトリクスを持たずに近似する（CJK ≈ 1.0em / 英数記号 ≈ 0.55em）。
粗い重なり・はみ出しの検出には十分で、依存ライブラリを増やさない設計。
SVG は名前空間有無・属性/``style`` 両記法（inline style を優先）・位置指定 tspan(x/y/dy)・
先頭テキストを扱う。``transform`` 付きテキストは座標が不定で検証できないため **hard 違反**
とする（caw-slides は text に transform を使わず explicit x/y で配置する規約）。キャンバスは
既定 1280x720（ppt169）。

既知の制約（設計上の割り切り）: フォント関連プロパティ（font-size / font-weight /
letter-spacing / text-anchor）の祖先 ``<g>`` からの継承と ``<tspan dx=...>`` の相対 X は
解決しない。caw-slides の authoring 規約はこれらを ``<text>`` 要素に直接書くため、実運用で
過小評価しない。
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable

# --- レイアウト定数（ppt169 = 1280x720 px キャンバス）------------------------
CANVAS_W: float = 1280.0  # px
CANVAS_H: float = 720.0  # px
CANVAS_MARGIN: float = 2.0  # px, はみ出し許容（丸め誤差吸収）

# 文字幅の近似係数（× font-size）
WIDTH_CJK: float = 1.0  # 全角
WIDTH_LATIN: float = 0.55  # 半角英数記号
WIDTH_SPACE: float = 0.28  # 半角スペース
BOLD_FACTOR: float = 1.03
ASCENT_FACTOR: float = 0.80  # baseline から上端
DESCENT_FACTOR: float = 0.22  # baseline から下端
DEFAULT_FONT_SIZE: float = 16.0  # px, font-size 未指定時

# 重なり判定のしきい値
OVERLAP_MIN_PX: float = 4.0  # x,y 両方向でこの px 以上重なって初めて計上
OVERLAP_WARN_RATIO: float = 0.20  # min(area) に対する重なり面積比: WARN
OVERLAP_HARD_RATIO: float = 0.40  # 同上: ERROR（ゲート fail）

_NUM_RE = re.compile(r"[-+]?\d*\.?\d+")
_BOLD_TOKENS = frozenset({"bold", "bolder"})


def _localname(tag: str) -> str:
    """``{ns}tag`` 形式から名前空間を除いたローカル名を返す。"""
    return tag.rsplit("}", 1)[-1]


def _num(raw: object, fallback: float = 0.0) -> float:
    """先頭の数値トークンを float 化する（``80px`` → 80, ``normal`` → fallback）。"""
    if raw is None:
        return fallback
    match = _NUM_RE.match(str(raw).strip())
    return float(match.group()) if match else fallback


def _style_dict(el: ET.Element) -> dict[str, str]:
    """``style="a:b;c:d"`` 属性を辞書化する（無ければ空）。"""
    raw = el.get("style")
    if not raw:
        return {}
    out: dict[str, str] = {}
    for part in raw.split(";"):
        if ":" in part:
            key, value = part.split(":", 1)
            # CSS プロパティ名は大小無視 → 小文字で正規化（Font-Size 等を拾う）
            out[key.strip().lower()] = value.strip()
    return out


def _prop(el: ET.Element, name: str, fallback: str | None = None) -> str | None:
    """表示プロパティを取得。inline ``style`` が属性より優先（CSS/SVG 準拠）、無ければ fallback。"""
    style = _style_dict(el)
    if name in style:
        return style[name]
    return el.get(name, fallback)


def _is_bold(value: str | None) -> bool:
    if not value:
        return False
    token = value.strip().lower()
    if token in _BOLD_TOKENS:
        return True
    return token.isdigit() and int(token) >= 600


def _is_cjk(ch: str) -> bool:
    """全角幅とみなす文字か（CJK 統合漢字・かな・全角記号・句読点）。"""
    cp = ord(ch)
    return (
        0x3000 <= cp <= 0x30FF  # 句読点・ひらがな・カタカナ
        or 0x3400 <= cp <= 0x9FFF  # CJK 統合漢字（拡張A含む）
        or 0xFF00 <= cp <= 0xFFEF  # 全角英数・半角カナ
    )


def estimate_text_width(text: str, font_size: float, *, bold: bool, letter_spacing: float) -> float:
    """テキスト行の描画幅を近似する（px）。

    Parameters
    ----------
    text : str
        行の全文字列。
    font_size : float
        フォントサイズ（px）。
    bold : bool
        太字なら僅かに広げる。
    letter_spacing : float
        文字間隔（px）。文字数 - 1 の隙間に加算。

    Returns
    -------
    float
        推定幅（px）。
    """
    width = 0.0
    for ch in text:
        if ch == " ":
            factor = WIDTH_SPACE
        elif _is_cjk(ch):
            factor = WIDTH_CJK
        else:
            factor = WIDTH_LATIN
        width += factor * font_size
    if bold:
        width *= BOLD_FACTOR
    if len(text) > 1 and letter_spacing:
        width += letter_spacing * (len(text) - 1)
    return width


@dataclass(frozen=True)
class TextLine:
    """1 行のテキストの近似バウンディングボックス（不変）。"""

    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def area(self) -> float:
        return max(0.0, self.x1 - self.x0) * max(0.0, self.y1 - self.y0)


def _line_box(
    x: float, y_baseline: float, text: str, font_size: float, anchor: str, letter_spacing: float, bold: bool
) -> TextLine:
    """アンカーを考慮して 1 行のボックスを作る。"""
    width = estimate_text_width(text, font_size, bold=bold, letter_spacing=letter_spacing)
    if anchor == "middle":
        x0 = x - width / 2.0
    elif anchor == "end":
        x0 = x - width
    else:  # start
        x0 = x
    y0 = y_baseline - ASCENT_FACTOR * font_size
    y1 = y_baseline + DESCENT_FACTOR * font_size
    return TextLine(x0=x0, y0=y0, x1=x0 + width, y1=y1, text=text)


@dataclass
class _LineState:
    """行を組み立てる際の可変な作業状態。

    意図的に mutable（``extract_text_lines`` の builder 内でのみ ``text`` を累積する用途。
    その scope 外へ漏らさない。不変ハウスルールの意図的な例外）。
    """

    x: float
    y: float
    text: str
    font_size: float
    bold: bool


def extract_text_lines(text_el: ET.Element) -> list[TextLine]:
    """1 つの ``<text>`` 要素から、描画される全行のボックスを起こす。

    子を順に走査し、位置指定 ``<tspan x= / y= / dy=>`` で行を折り返す。装飾のみの
    インライン ``<tspan>`` と先頭テキスト・tail テキストは現在行にマージする。
    ``y`` は絶対指定、``dy`` は前行からの相対で累積する。
    """
    base_x = _num(_prop(text_el, "x"), 0.0)
    base_y = _num(_prop(text_el, "y"), 0.0)
    base_fs = _num(_prop(text_el, "font-size"), DEFAULT_FONT_SIZE)
    anchor = _prop(text_el, "text-anchor", "start") or "start"
    ls = _num(_prop(text_el, "letter-spacing"), 0.0)
    base_bold = _is_bold(_prop(text_el, "font-weight"))

    lines: list[TextLine] = []
    cur = _LineState(x=base_x, y=base_y, text=(text_el.text or ""), font_size=base_fs, bold=base_bold)

    def flush() -> None:
        if cur.text.strip():
            lines.append(_line_box(cur.x, cur.y, cur.text, cur.font_size, anchor, ls, cur.bold))

    for child in text_el:
        if _localname(child.tag) != "tspan":
            continue
        content = "".join(child.itertext())
        cbold = base_bold or _is_bold(_prop(child, "font-weight"))
        cfs = _num(_prop(child, "font-size"), base_fs)
        is_positional = ("x" in child.attrib) or ("y" in child.attrib) or ("dy" in child.attrib)
        if is_positional:
            flush()
            new_x = _num(child.get("x"), base_x) if "x" in child.attrib else base_x
            if "y" in child.attrib:
                new_y = _num(child.get("y"), cur.y)
            else:
                new_y = cur.y + _num(child.get("dy"), 0.0)
            cur = _LineState(x=new_x, y=new_y, text=content, font_size=cfs, bold=cbold)
        else:
            cur.text += content
        if child.tail:
            cur.text += child.tail
    flush()
    return lines


def _under_transform(el: ET.Element, parents: dict[ET.Element, ET.Element]) -> bool:
    """要素または祖先に ``transform`` が付いているか。"""
    cur: ET.Element | None = el
    while cur is not None:
        if cur.get("transform"):
            return True
        cur = parents.get(cur)
    return False


def parse_svg_lines(svg_path: str) -> tuple[list[TextLine], list[str]]:
    """SVG から全テキスト行のボックスを抽出。``transform`` 付きは警告のみ返す。"""
    root = ET.parse(svg_path).getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    lines: list[TextLine] = []
    warnings: list[str] = []
    for text_el in root.iter():
        if _localname(text_el.tag) != "text":
            continue
        if _under_transform(text_el, parents):
            content = "".join(text_el.itertext()).strip()
            warnings.append(f"transform present; skipped {content[:24]!r}")
            continue
        lines.extend(extract_text_lines(text_el))
    return lines, warnings


def _intersection(a: TextLine, b: TextLine) -> tuple[float, float]:
    """2 ボックスの重なり幅・高さ（px）を返す（負なら重ならない）。"""
    ox = min(a.x1, b.x1) - max(a.x0, b.x0)
    oy = min(a.y1, b.y1) - max(a.y0, b.y0)
    return ox, oy


def find_out_of_canvas(lines: Iterable[TextLine]) -> list[TextLine]:
    """キャンバス外へはみ出す行を返す。"""
    bad = []
    for ln in lines:
        if (
            ln.x0 < -CANVAS_MARGIN
            or ln.y0 < -CANVAS_MARGIN
            or ln.x1 > CANVAS_W + CANVAS_MARGIN
            or ln.y1 > CANVAS_H + CANVAS_MARGIN
        ):
            bad.append(ln)
    return bad


def find_overlaps(lines: list[TextLine]) -> list[tuple[TextLine, TextLine, float, str]]:
    """テキスト行同士の有意な重なりを返す ``(a, b, ratio, severity)``。"""
    hits = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            a, b = lines[i], lines[j]
            ox, oy = _intersection(a, b)
            if ox < OVERLAP_MIN_PX or oy < OVERLAP_MIN_PX:
                continue
            inter = ox * oy
            denom = min(a.area, b.area)
            # denom == 0 は退化ボックス（空白のみの行など）。上流の strip() ガードで
            # 既に除外済みのため ratio 0.0（＝非計上）で意図どおり。
            ratio = inter / denom if denom > 0 else 0.0
            if ratio >= OVERLAP_HARD_RATIO:
                hits.append((a, b, ratio, "ERROR"))
            elif ratio >= OVERLAP_WARN_RATIO:
                hits.append((a, b, ratio, "WARN"))
    return hits


def check_svg(svg_path: str) -> tuple[list[TextLine], list[tuple[TextLine, TextLine, float, str]], list[str]]:
    """1 ファイルを検査し (はみ出し行, 重なり, 警告) を返す。"""
    lines, warnings = parse_svg_lines(svg_path)
    return find_out_of_canvas(lines), find_overlaps(lines), warnings


def resolve_svgs(path: str) -> list[str]:
    """引数のパスを SVG ファイル一覧に解決する（assert_font_rule と同じ規則）。"""
    if os.path.isfile(path):
        return [path] if path.lower().endswith(".svg") else []
    if os.path.isdir(path):
        direct = sorted(glob.glob(os.path.join(path, "*.svg")))
        if direct:
            return direct
        for sub in ("svg", "svg_output", "svg_final"):
            found = sorted(glob.glob(os.path.join(path, sub, "*.svg")))
            if found:
                return found
    return []


def _snippet(ln: TextLine) -> str:
    txt = ln.text.strip()
    return (txt[:24] + "…") if len(txt) > 24 else txt


def check_path(path: str) -> int:
    """.svg ファイル or ディレクトリを検査。ハード違反があれば非 0 を返す。"""
    files = resolve_svgs(path)
    if not files:
        print(f"[ERROR] no SVG found at {path}", file=sys.stderr)
        return 2

    hard = 0
    warn = 0
    print(f"[assert_no_overlap] checking {len(files)} SVG file(s)...\n")
    for f in files:
        name = os.path.basename(f)
        try:
            oob, overlaps, warns = check_svg(f)
        except ET.ParseError as exc:
            hard += 1
            print(f"[FAIL] {name}: XML parse error: {exc}")
            continue
        except (OSError, ValueError) as exc:
            hard += 1
            print(f"[FAIL] {name}: read/parse error: {exc}")
            continue

        errs = [o for o in overlaps if o[3] == "ERROR"]
        warns_ov = [o for o in overlaps if o[3] == "WARN"]
        if not oob and not errs and not warns_ov and not warns:
            print(f"[OK]   {name}")
            continue
        print(f"[FAIL] {name}" if (oob or errs or warns) else f"[WARN] {name}")
        for ln in oob:
            hard += 1
            print(
                f"   [ERROR] off-canvas: {_snippet(ln)!r} "
                f"bbox=({ln.x0:.0f},{ln.y0:.0f})-({ln.x1:.0f},{ln.y1:.0f})"
            )
        for a, b, ratio, _sev in errs:
            hard += 1
            print(f"   [ERROR] overlap {ratio:.0%}: {_snippet(a)!r} × {_snippet(b)!r}")
        # transform 付き text は座標が測定不能 → 検証できないので hard 扱い（false green を避ける）。
        # caw-slides は text に transform を使わず explicit x/y で配置する規約なので、
        # ここに来ること自体が規約外の authoring を示す。
        for msg in warns:
            hard += 1
            print(f"   [ERROR] unmeasurable (transform on text): {msg}")
        for a, b, ratio, _sev in warns_ov:
            warn += 1
            print(f"   [warn]  overlap {ratio:.0%}: {_snippet(a)!r} × {_snippet(b)!r}")

    print("\n" + "=" * 60)
    print(f"[SUMMARY] hard violations: {hard}   warnings: {warn}")
    if hard:
        print("[RESULT] FAIL — レイアウト衝突を解消してください")
        return 1
    print("[RESULT] PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SVG レイアウト衝突ゲート (assert_no_overlap)")
    parser.add_argument("path", help=".svg ファイル or SVG を含むディレクトリ")
    args = parser.parse_args(argv)
    return check_path(args.path)


if __name__ == "__main__":
    raise SystemExit(main())
