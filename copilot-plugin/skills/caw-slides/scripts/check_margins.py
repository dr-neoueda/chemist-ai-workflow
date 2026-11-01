#!/usr/bin/env python3
"""右余白 1200 を越える文字を検出する（caw-slides）。

``assert_no_overlap`` はキャンバスの端（1280）を越えた文字しか落とさない。1200 と 1280 のあいだの文字は
検定に通るのに右へ寄って見える。幅は字種ごとの推定で、問題になる場合を拾うには十分。

Usage
-----
    python3 check_margins.py <SVG を含むディレクトリ>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARGIN = 1200
WIDE, NARROW = 1.0, 0.56   # 字送り（文字の大きさに対する比）
# text-anchor を読む。右揃えのページ番号は余白の線ちょうどに置くので、読まないと全ページで誤検出する
TEXT = re.compile(r"<text ([^>]*)>(.*?)</text>", re.S)
ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')
TAG = re.compile(r"<[^>]+>")


def advance(s: str, size: float) -> float:
    """文字列の幅の推定 [px]。"""
    return sum(size * (NARROW if ch.isascii() else WIDE) for ch in s)


def check(root: Path) -> list[str]:
    """``root`` の SVG を調べ、余白を越える文字の説明の一覧を返す。"""
    found = []
    for svg in sorted(Path(root).glob("*.svg")):
        for match in TEXT.finditer(svg.read_text(encoding="utf-8")):
            attrs = dict(ATTR.findall(match.group(1)))
            if "x" not in attrs or "font-size" not in attrs:
                continue
            x, size = float(attrs["x"]), float(attrs["font-size"])
            plain = TAG.sub("", match.group(2))
            width = advance(plain, size)
            anchor = attrs.get("text-anchor", "start")
            end = x if anchor == "end" else x + (width / 2 if anchor == "middle" else width)
            if end > MARGIN:
                found.append(f"{svg.name}: x={x} 推定右端={end:.0f} (+{end - MARGIN:.0f}) {plain[:44]!r}")
    return found


def main(argv: list[str] | None = None) -> int:
    """CLI。問題なし 0、越えあり 1、対象が無い 2（0 件と区別する）。"""
    sys.stdout.reconfigure(errors="replace")   # cp932 に無い文字（— ≈）で検定そのものが落ちないように
    parser = argparse.ArgumentParser(description="右余白 1200 を越える文字を検出する")
    parser.add_argument("path", type=Path, help="SVG を含むディレクトリ")
    args = parser.parse_args(argv)
    if not args.path.is_dir() or not any(args.path.glob("*.svg")):
        print(f"[ERROR] no SVG found at {args.path}", file=sys.stderr)
        return 2
    found = check(args.path)
    for line in found:
        print(f"  {line}")
    print(f"\n  余白 {MARGIN} を越える text: {len(found)} 件")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
