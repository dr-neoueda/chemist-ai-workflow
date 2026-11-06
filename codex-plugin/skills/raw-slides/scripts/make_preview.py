#!/usr/bin/env python3
"""スライドの SVG をブラウザで PNG にする（raw-slides）。目視 QA 専用で、配布先には置かない。

ブラウザは viewBox を守り、``../images/*.png`` と実際のフォントを描くので、ゲートが見ない重なり（文字と画像・文字と枠）が
絵で分かる。出力の画素サイズは必ず検定する。1280x720 でないプレビューは中身の一部を黙って隠すことがあり、
切れた側に何も無いのか切れているのかは、その画像だけ見ても区別できない。

Usage
-----
    python3 make_preview.py <デッキのフォルダ> <出力先> [枚の名前の先頭 ...]
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

from PIL import Image

SIZE = (1280, 720)
TIMEOUT_S = 120      # ブラウザが固まったときに無期限に待たない
BROWSER_PATHS = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
    Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
    Path(os.environ.get("LOCALAPPDATA", "C:/Users/Default/AppData/Local")) / "Google/Chrome/Application/chrome.exe",
    Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
    Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Microsoft/Edge/Application/msedge.exe",
)
BROWSER_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge")


class PreviewError(Exception):
    """プレビューを作れない、または QA に使えない。"""


def find_browser(paths: Iterable[Path] = BROWSER_PATHS, names: Iterable[str] = BROWSER_NAMES) -> str:
    """Chrome 系のブラウザを探して実行ファイルのパスを返す。

    Raises
    ------
    PreviewError
        見つからない。
    """
    for path in paths:
        if Path(path).exists():
            return str(path)
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    raise PreviewError("Chrome / Edge が見つからない。プレビューにはどちらかを導入する")


def check_size(png: Path) -> None:
    """プレビューの画素サイズが 1280x720 かを検定する。"""
    with Image.open(png) as im:
        size = im.size
    if size != SIZE:
        raise PreviewError(f"{png.name}: プレビューが {size} で 1280x720 でない。この画像で QA しない")


def render(browser: str, svg: Path, png: Path) -> None:
    """SVG を 1 枚 PNG にする。

    前回の PNG を先に消す（書かれなかったときに古い画像で QA しないため）。起動中のブラウザに相乗りしないよう作業用の
    プロファイルを渡し、Windows の表示倍率で画素数が変わらないよう倍率を 1 に固定する。
    """
    png.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        done = subprocess.run([browser, "--headless", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                               "--force-device-scale-factor=1", f"--screenshot={png}",
                               f"--window-size={SIZE[0]},{SIZE[1]}", "--default-background-color=FFFFFFFF",
                               svg.resolve().as_uri()], capture_output=True, timeout=TIMEOUT_S)
    if not png.exists():
        raise PreviewError(f"{svg.name}: プレビューが書かれなかった。{done.stderr.decode('utf-8', 'replace')[-300:]}")
    check_size(png)


def main(argv: list[str] | None = None) -> int:
    """CLI。"""
    parser = argparse.ArgumentParser(description="スライドの SVG をプレビュー PNG にする")
    parser.add_argument("project", type=Path, help="デッキのフォルダ（svg_output/ を持つ）")
    parser.add_argument("out", type=Path, help="PNG の出力先（scratchpad など）")
    parser.add_argument("prefixes", nargs="*", help="この文字列で始まる枚だけ")
    args = parser.parse_args(argv)
    svgs = sorted((args.project / "svg_output").glob("*.svg"))
    if args.prefixes:
        svgs = [s for s in svgs if any(s.name.startswith(p) for p in args.prefixes)]
    if not svgs:
        print(f"[ERROR] {args.project / 'svg_output'} に対象の SVG が無い", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        browser = find_browser()
        for svg in svgs:
            png = args.out / f"{svg.stem}.png"
            render(browser, svg, png)
            print(f"  {png}")
    except (PreviewError, subprocess.TimeoutExpired) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
