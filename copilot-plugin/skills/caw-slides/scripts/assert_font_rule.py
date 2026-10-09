#!/usr/bin/env python3
"""和文フォントルール・ゲート（caw-slides：和文 = MS Gothic / 英数 = Arial）。

スライド SVG のテキスト run を走査し、**CJK 文字（漢字・かな・全角記号）を含むのに
font-family に日本語フォントが無い** run を検出する。この種の run は SVG→pptx 変換時に
East-Asian 書体が既定の CJK フォント（例: Microsoft YaHei）に割り当てられ、漢字が
中国語体で描画される、または Arial 等では豆腐（□）になる＝フォントルール違反。
重なりゲート（assert_no_overlap）では拾えない authoring ミスを事前に潰す姉妹ゲート。

Usage
-----
    python3 assert_font_rule.py <path>        # .svg ファイル or SVG を含むディレクトリ

判定ロジックのテストは ``tests/test_assert_font_rule.py`` (pytest) を参照。

Notes
-----
判定は font-family 文字列に日本語フォント名（gothic / mincho / hiragino / meiryo /
ゴシック / 明朝 / ヒラギノ 等）が含まれるかで行う（実フォント解決はしない）。CJK を
含む run の font-family に日本語フォントが 1 つでもあれば PASS、無ければ違反。
祖先 (`<g>`/`<svg>`) からの font-family 継承・inline ``style`` 優先・``inherit`` を尊重する。
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterator

# font-family に含まれれば「日本語フォント指定あり」とみなすトークン（小文字比較）。
# "gothic" 単独だと Century/Franklin Gothic 等のラテン専用フォントを誤許可するため、
# 家系名を明示する。
JP_FONT_TOKENS: tuple[str, ...] = (
    "ms gothic", "ms pgothic", "ms ui gothic",
    "yu gothic", "yugothic",
    "hiragino",     # Hiragino Kaku Gothic ProN / Hiragino Sans / Hiragino Mincho
    "meiryo",
    "biz ud",       # BIZ UDGothic / BIZ UDMincho
    "kozuka",       # Kozuka Gothic / Kozuka Mincho
    "ipagothic", "ipaexgothic", "ipamincho", "ipaexmincho",
    "takao", "sazanami", "osaka",
    "mincho",       # MS Mincho / Yu Mincho（"gothic" ほど誤検出しない語）
    "noto sans jp", "noto sans cjk", "noto serif jp", "noto serif cjk",
    "source han",   # Source Han Sans / Serif
    "ゴシック", "明朝", "ヒラギノ", "メイリオ",  # 日本語表記（游ゴシック 等）
)

# CSS の継承キーワード（実フォント名でない）
CSS_INHERIT_KEYWORDS: frozenset[str] = frozenset({"inherit", "initial", "unset", "revert"})

# 日本語フォントを要する文字範囲（かな・漢字・全角・互換・拡張）
CJK_RANGES: tuple[tuple[int, int], ...] = (
    (0x3000, 0x30FF),   # 句読点・ひらがな・カタカナ・全角記号
    (0x31F0, 0x31FF),   # カタカナ音声拡張
    (0x3200, 0x33FF),   # 囲み CJK・CJK 互換（丸数字 ①②③ を含む）
    (0x3400, 0x9FFF),   # CJK 統合漢字（拡張 A 含む）
    (0xF900, 0xFAFF),   # CJK 互換漢字
    (0xFF00, 0xFFEF),   # 半角・全角形
    (0x20000, 0x2FFFD),  # CJK 拡張 B–F
)


def _localname(tag: str) -> str:
    """``{ns}tag`` 形式から名前空間を除いたローカル名を返す。"""
    return tag.rsplit("}", 1)[-1]


def _style_dict(el: ET.Element) -> dict[str, str]:
    """``style="a:b;c:d"`` 属性を辞書化する（無ければ空）。"""
    raw = el.get("style")
    if not raw:
        return {}
    out: dict[str, str] = {}
    for part in raw.split(";"):
        if ":" in part:
            key, value = part.split(":", 1)
            # CSS プロパティ名は大小無視 → 小文字で正規化（Font-Family 等を拾う）
            out[key.strip().lower()] = value.strip()
    return out


def _own_family(el: ET.Element) -> str | None:
    """要素自身が宣言する font-family を返す（inline ``style`` が属性より優先）。

    未指定・``inherit`` 系キーワードの場合は None（＝継承にフォールバック）。
    """
    family = _style_dict(el).get("font-family", el.get("font-family"))
    if family is None:
        return None
    if family.strip().lower() in CSS_INHERIT_KEYWORDS:
        return None
    return family


def _is_cjk(ch: str) -> bool:
    """日本語フォントを要する文字か（かな・漢字・全角・互換・拡張）。"""
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def _has_jp_font(family: str | None) -> bool:
    """font-family 文字列に日本語フォント名が含まれるか。"""
    if not family:
        return False
    low = family.lower()
    return any(token in low for token in JP_FONT_TOKENS)


def _cjk_chars(text: str) -> str:
    """text 中の CJK 文字を重複なく連結して返す（報告用・順序保持で O(n)）。"""
    return "".join(dict.fromkeys(ch for ch in text if _is_cjk(ch)))


@dataclass(frozen=True)
class Violation:
    """フォントルール違反の 1 run（不変）。"""

    text: str
    family: str | None
    cjk: str


def iter_runs(el: ET.Element, inherited_family: str | None) -> Iterator[tuple[str, str | None]]:
    """要素以下を再帰走査し ``(run テキスト, 実効 font-family)`` を yield する。

    実効 font-family は自身の宣言、無ければ継承値。子要素（``tspan``/``textPath``/``a``
    など text-content 全般）に降りる。子の tail テキスト（閉じタグ後）は親の書体に属する。
    """
    family = _own_family(el) or inherited_family
    if el.text and el.text.strip():
        yield (el.text, family)
    for child in el:
        yield from iter_runs(child, family)
        if child.tail and child.tail.strip():
            yield (child.tail, family)


def _resolve_ancestor_family(
    el: ET.Element | None, parents: dict[ET.Element, ET.Element]
) -> str | None:
    """el（含む）から祖先へ辿り、最初に宣言された font-family を返す。"""
    cur = el
    while cur is not None:
        family = _own_family(cur)
        if family is not None:
            return family
        cur = parents.get(cur)
    return None


def check_svg(svg_path: str) -> list[Violation]:
    """1 ファイルを検査し、CJK を含むのに日本語フォント指定が無い run を返す。"""
    root = ET.parse(svg_path).getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    violations: list[Violation] = []
    for el in root.iter():
        if _localname(el.tag) != "text":
            continue
        inherited = _resolve_ancestor_family(parents.get(el), parents)
        for text, family in iter_runs(el, inherited):
            if _has_jp_font(family):
                continue
            cjk = _cjk_chars(text)
            if cjk:
                violations.append(Violation(text=text.strip(), family=family, cjk=cjk))
    return violations


def resolve_svgs(path: str) -> list[str]:
    """引数のパスを SVG ファイル一覧に解決する。

    ``path`` が ``.svg`` ファイルならそれ 1 つ、ディレクトリなら直下の ``*.svg``
    （ソート）を返す。ディレクトリ直下に無い場合は ``svg/`` ``svg_output/``
    ``svg_final/`` の順に探索する（各種プロジェクト構成に対応）。
    """
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


def _snippet(text: str) -> str:
    return (text[:24] + "…") if len(text) > 24 else text


def check_path(path: str) -> int:
    """.svg ファイル or ディレクトリを検査。違反があれば非 0 を返す。"""
    files = resolve_svgs(path)
    if not files:
        print(f"[ERROR] no SVG found at {path}", file=sys.stderr)
        return 2

    total = 0
    print(f"[assert_font_rule] checking {len(files)} SVG file(s)...\n")
    for f in files:
        name = os.path.basename(f)
        try:
            violations = check_svg(f)
        except ET.ParseError as exc:
            total += 1
            print(f"[FAIL] {name}: XML parse error: {exc}")
            continue
        except (OSError, ValueError) as exc:
            total += 1
            print(f"[FAIL] {name}: read/parse error: {exc}")
            continue

        if not violations:
            print(f"[OK]   {name}")
            continue
        print(f"[FAIL] {name}")
        for v in violations:
            total += 1
            fam = v.family or "(unspecified)"
            print(f"   [ERROR] CJK {v.cjk!r} in non-JP font [{fam}]: {_snippet(v.text)!r}")

    print("\n" + "=" * 60)
    print(f"[SUMMARY] font-rule violations: {total}")
    if total:
        print("[RESULT] FAIL — 和文 run に日本語フォント（MS Gothic 等）を指定してください")
        return 1
    print("[RESULT] PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="和文フォントルール・ゲート (assert_font_rule)")
    parser.add_argument("path", help=".svg ファイル or SVG を含むディレクトリ")
    args = parser.parse_args(argv)
    return check_path(args.path)


if __name__ == "__main__":
    raise SystemExit(main())
