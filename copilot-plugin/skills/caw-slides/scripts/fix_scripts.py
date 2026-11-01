#!/usr/bin/env python3
"""書き出した pptx の上付き・下付きを復元する（caw-slides）。

変換器は SVG の ``baseline-shift`` を処理しない。``<tspan baseline-shift="super" font-size="11">1</tspan>`` は pptx では
基線に並んだ小さい文字になる（¹H が 1H に、cm⁻¹ が cm−1 になる）。ブラウザのプレビューとゲートでは気づけない。

照合は行単位で行う。SVG の ``<text>`` を全文が一致する pptx の段落と組にして、その段落の縮小された run にだけ順に当てる。
同じ文面の行が複数あれば出現順で組にし、数が合わなければ止める（上付きの無い同文の行に取られないように）。
``baseline`` は上付き +30 %・下付き −25 %、文字の大きさは行の大きさへ戻す（PowerPoint が自分で縮めるので、
縮めたままだと二重に小さくなる）。行か添字が 1 つでも見つからなければ保存しない。
行の中の添字は文字だけでなく位置（前にある空白以外の文字数）でも照合し、同じ文字の小さい run に取られないようにする。

Usage
-----
    python3 fix_scripts.py <deck.pptx> <svg_output ディレクトリ>
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.presentation import Presentation as PresentationType
from pptx.shapes.shapetree import SlideShapes
from pptx.slide import Slide
from pptx.text.text import _Paragraph

SVG_NS = "{http://www.w3.org/2000/svg}"
SHIFT = {"super": "30000", "sub": "-25000"}       # DrawingML の baseline、1/1000 %


class ScriptMismatch(Exception):
    """SVG の上付き・下付きが pptx の中で見つからない。"""


@dataclass(frozen=True)
class Script:
    """添字 1 つ。文字、向き、行の中でこの添字より前にある空白以外の文字数。"""
    text: str
    shift: str
    offset: int


@dataclass(frozen=True)
class Line:
    """SVG の 1 行。全文と、添字を順に持つ（添字が無ければ空）。"""
    text: str
    scripts: tuple[Script, ...]


def _normal(line: str) -> str:
    """照合用の文字列。変換器は全角空白を半角へ置き換え、SVG の字下げも捨てるので、空白をそろえてから比べる。"""
    return re.sub(r"\s+", " ", line.replace("\u3000", " ")).strip()


def _ink(text: str) -> int:
    """空白以外の文字数。変換器が手を入れない部分なので、行の中の位置はこれで数える。"""
    return len("".join(text.split()))


def _segments(node: ET.Element, shift: str | None = None) -> Iterator[tuple[str, str | None]]:
    """``<text>`` の中の断片を (文字, 向き) で文書の順に返す。"""
    own = node.get("baseline-shift")
    here = own if own in SHIFT else shift
    if node.text:
        yield node.text, here
    for child in node:
        yield from _segments(child, here)
        if child.tail:
            yield child.tail, here


def svg_lines(svg: Path) -> list[Line]:
    """SVG のすべての行を出現順に取り出す。"""
    out = []
    for node in ET.parse(svg).getroot().iter(f"{SVG_NS}text"):
        scripts, offset = [], 0
        for piece, shift in _segments(node):
            if shift is not None and _ink(piece):
                scripts.append(Script(_normal(piece), shift, offset))
            offset += _ink(piece)
        out.append(Line(_normal("".join(node.itertext())), tuple(scripts)))
    return out


def paragraphs(shapes: SlideShapes) -> Iterator[_Paragraph]:
    """グループの中まで辿って段落を返す。"""
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from paragraphs(shape.shapes)
        elif shape.has_text_frame:
            yield from shape.text_frame.paragraphs


def apply(para: _Paragraph, line: Line) -> None:
    """行の添字を段落の縮小された run へ順に当てる。全部当たらなければ止める。"""
    base = max((r.font.size for r in para.runs if r.font.size is not None), default=None)
    if base is None:
        raise ScriptMismatch(f"{line.text!r}: 文字の大きさを持つ run が無い")
    queue = list(line.scripts)
    offset = 0
    for run in para.runs:
        if (queue and offset == queue[0].offset and _normal(run.text) == queue[0].text
                and run.font.size is not None and run.font.size < base):
            run.font.size = base
            run._r.get_or_add_rPr().set("baseline", SHIFT[queue.pop(0).shift])
        offset += _ink(run.text)
    if queue:
        raise ScriptMismatch(f"{line.text!r}: 添字 {queue} が縮小された run に見つからない")


def fix_slide(slide: Slide, lines: list[Line]) -> int:
    """1 枚を直し、当てた添字の数を返す。同じ文面の行は出現順に組にする。"""
    scripted = {ln.text for ln in lines if ln.scripts}
    pending = {text: [ln for ln in lines if ln.text == text] for text in scripted}
    for para in paragraphs(slide.shapes):
        queue = pending.get(_normal("".join(r.text for r in para.runs)))
        if queue is None:
            continue
        if not queue:
            raise ScriptMismatch(f"同じ文面の段落が SVG より多い: {para.text!r}")
        line = queue.pop(0)
        if line.scripts:
            apply(para, line)
    left = [ln.text for queue in pending.values() for ln in queue]
    if left:
        raise ScriptMismatch(f"pptx に見つからない行: {left}。dy で行を積んだ <text> は 1 段落にまとまるので、"
                             "1 行 1 <text> で書き直す")
    return sum(len(ln.scripts) for ln in lines)


def _save_over(prs: PresentationType, path: Path) -> None:
    """隣に書いてから入れ替える。書き込みに失敗しても元の pptx は壊れない。"""
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        prs.save(str(tmp))
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def fix_scripts(pptx_path: str | Path, svg_dir: str | Path) -> int:
    """上付き・下付きを復元して上書き保存し、当てた添字の数を返す。

    Parameters
    ----------
    pptx_path : str | Path
        書き出した pptx。
    svg_dir : str | Path
        元の SVG のディレクトリ。名前順がスライドの順。

    Returns
    -------
    int
        当てた添字の数。

    Raises
    ------
    ScriptMismatch
        枚数が合わない、または行・添字が見つからない。このとき保存しない。
    """
    prs = Presentation(str(pptx_path))
    per_slide = [svg_lines(svg) for svg in sorted(Path(svg_dir).glob("*.svg"))]
    if len(per_slide) != len(prs.slides):
        raise ScriptMismatch(f"SVG {len(per_slide)} 枚に対して pptx は {len(prs.slides)} 枚")
    total = sum(fix_slide(slide, lines) for slide, lines in zip(prs.slides, per_slide, strict=True))
    if total:
        _save_over(prs, Path(pptx_path))
    return total


def main(argv: list[str] | None = None) -> int:
    """CLI。"""
    parser = argparse.ArgumentParser(description="pptx の上付き・下付きを復元する")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("svg_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        total = fix_scripts(args.pptx, args.svg_dir)
    except ScriptMismatch as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"  上付き・下付き: {total} 個に baseline を設定")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
