#!/usr/bin/env python3
"""ローカル画像を SVG に data-URI 埋め込みする（caw-slides）。

ユーザーが `work/presentations/figures/` に置いた画像（顕微鏡写真・装置スクショ・手描き
スキーム・外部プロット等）や、論文図の切り抜き・解析の出力をスライドに載せるための補助。

SVG に `<image href="work/presentations/figures/foo.png" .../>` と書いておき、**変換前に
data-URI へインライン化**する（vendored 変換器は create_pptx_with_native_svg 直呼びだと
外部ファイル href を埋め込まないため）。**アスペクト比を保つ**配置ヘルパも提供する（潰れた
画像は品質を下げるため）。

Usage
-----
    python3 embed_image.py inline  <in.svg> <out.svg> [--base-dir DIR] [--allow-outside]
    python3 embed_image.py datauri <image>

依存: data-URI 化は stdlib のみ。画像サイズ取得（fit 用）は Pillow。
テストは tests/test_embed_image.py（pytest）。
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys

# <image ...( )href="..."> / xlink:href。属性名直前に空白を要求（data-href 等の誤一致を防ぐ）。
# クォートは group2 で捕捉し閉じを backref、`=` 周りの空白も許す。
_HREF_RE = re.compile(
    r'(<image\b[^>]*?[ \t\r\n](?:xlink:href|href)\s*=\s*)(["\'])([^"\']*)\2'
)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_SKIP_PREFIXES = ("data:", "http://", "https://")  # 小文字で比較
_MIME_BY_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"}


def _sniff_mime(raw: bytes, path: str) -> str:
    """内容（magic bytes）から MIME を判定し、不明なら拡張子、それでも不明なら ValueError。"""
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    head = raw[:512].lstrip()
    if head.startswith(b"<?xml") or head.startswith(b"<svg") or b"<svg" in raw[:512]:
        return "image/svg+xml"
    ext = os.path.splitext(path)[1].lower()
    if ext in _MIME_BY_EXT:
        return _MIME_BY_EXT[ext]
    raise ValueError(f"未対応の画像形式です（PNG/JPEG/GIF/WEBP/SVG のみ）: {path}")


def data_uri(path: str) -> str:
    """画像ファイルを ``data:<mime>;base64,...`` の data-URI にする。

    Parameters
    ----------
    path : str
        画像ファイルパス。

    Returns
    -------
    str
        data-URI 文字列（MIME は内容の magic bytes から判定）。

    Raises
    ------
    FileNotFoundError
        ファイルが無いとき（埋め込み漏れを表面化させる）。
    ValueError
        未対応の画像形式のとき。
    """
    with open(path, "rb") as fh:  # 無ければ FileNotFoundError
        raw = fh.read()
    mime = _sniff_mime(raw, path)
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def image_size(path: str) -> tuple[int, int]:
    """画像の (幅, 高さ) px を返す（Pillow）。アスペクト維持配置に使う。

    Parameters
    ----------
    path : str
        画像ファイルパス。

    Returns
    -------
    tuple[int, int]
        ``(width, height)``（px）。
    """
    from PIL import Image

    with Image.open(path) as im:
        return int(im.width), int(im.height)


def fit_box(
    iw: float, ih: float, max_w: float, max_h: float, *, allow_upscale: bool = False
) -> tuple[float, float]:
    """元画像 (iw, ih) をアスペクト比を保って (max_w, max_h) に収めた (w, h) を返す。

    既定では**拡大しない**（ラスタ画像を引き伸ばすと画質が落ちるため。box より小さい画像は
    等倍で置く）。``allow_upscale=True`` で box いっぱいまで拡大を許す。

    Raises
    ------
    ValueError
        寸法が非正のとき。
    """
    if iw <= 0 or ih <= 0 or max_w <= 0 or max_h <= 0:
        raise ValueError("寸法は正の値にしてください")
    scale = min(max_w / iw, max_h / ih)
    if not allow_upscale:
        scale = min(scale, 1.0)
    return iw * scale, ih * scale


def _resolve_ref(ref: str, base_dir: str, allow_outside: bool) -> str:
    """href 参照をローカルパスに解決する（base_dir 外・絶対パスは allow_outside 時のみ）。"""
    base = os.path.abspath(base_dir)
    if os.path.isabs(ref):
        if not allow_outside:
            raise ValueError(f"絶対パス {ref!r} は --allow-outside 指定時のみ許可")
        return ref
    cand = os.path.abspath(os.path.join(base_dir, ref))
    if not allow_outside and cand != base and not cand.startswith(base + os.sep):
        raise ValueError(f"href {ref!r} が base_dir 外に出ます（--allow-outside で許可）")
    return cand


def inline_image_hrefs(svg_text: str, base_dir: str = ".", *, allow_outside: bool = False) -> str:
    """SVG 内の ``<image href="local">`` を data-URI に置換する。

    ``data:`` / ``http(s)://``（大小無視）の href はそのまま。**コメント内の `<image>` は無視**。
    相対パスは ``base_dir`` 起点で解決し、既定では base_dir 外・絶対パスを拒否（``allow_outside``）。
    ローカルファイルが無ければ ``FileNotFoundError``（埋め込み漏れを検出）。
    """
    def _repl(m: re.Match[str]) -> str:
        pre, quote, ref = m.group(1), m.group(2), m.group(3)
        if ref.lower().startswith(_SKIP_PREFIXES):
            return m.group(0)
        path = _resolve_ref(ref, base_dir, allow_outside)
        return pre + quote + data_uri(path) + quote

    # コメント領域は verbatim 保持し、その外側だけ置換する
    parts = _COMMENT_RE.split(svg_text)
    comments = _COMMENT_RE.findall(svg_text)
    out: list[str] = []
    for i, seg in enumerate(parts):
        out.append(_HREF_RE.sub(_repl, seg))
        if i < len(comments):
            out.append(comments[i])
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ローカル画像を SVG に data-URI 埋め込み (embed_image)")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_in = sub.add_parser("inline", help="SVG 内の全ローカル image href を data-URI 化")
    p_in.add_argument("in_svg")
    p_in.add_argument("out_svg")
    p_in.add_argument("--base-dir", default=".")
    p_in.add_argument("--allow-outside", action="store_true", help="base_dir 外・絶対パスを許可")

    p_du = sub.add_parser("datauri", help="1 枚の画像の data-URI を出力")
    p_du.add_argument("image")

    args = ap.parse_args(argv)
    try:
        if args.mode == "inline":
            with open(args.in_svg, encoding="utf-8") as fh:
                svg = fh.read()
            out = inline_image_hrefs(svg, base_dir=args.base_dir, allow_outside=args.allow_outside)
            with open(args.out_svg, "w", encoding="utf-8") as fh:
                fh.write(out)
            print(f"[embed_image] inlined → {args.out_svg}")
        elif args.mode == "datauri":
            print(data_uri(args.image))
        else:  # argparse の required=True で到達しない
            raise RuntimeError(f"未対応のモード: {args.mode!r}")  # pragma: no cover
    except (OSError, ValueError) as exc:
        print(f"[embed_image] ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
