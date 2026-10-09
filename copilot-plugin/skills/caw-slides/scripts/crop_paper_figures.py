#!/usr/bin/env python3
"""論文 PDF から図表領域を高解像度で切り抜く（caw-slides）。

論文紹介スライドで、原論文の図（Figure / Scheme / Table）を PNG に切り出し、
自作の図表と混ぜてスライドに載せるための補助。PyMuPDF のベクタ描画を指定 DPI で
ラスタ化する（拡大でなく高精細）。

2 モード:
  region : バウンディングボックス（ページ比率 0..1）を高 DPI で切り抜き
  page   : ページ全体を描画（まず図の座標を目視で当たりを付ける用）

Usage:
  # ページを描画して座標の当たりを付ける
  python crop_paper_figures.py page   <pdf> <page_no> <out.png> [--dpi 150]

  # 領域を切り抜く（ページ幅/高さの比率・原点は左上）
  python crop_paper_figures.py region <pdf> <page_no> <x0> <y0> <x1> <y1> <out.png> [--dpi 300]

Notes:
  - page_no は 1 始まり。
  - 比率座標なので呼び出しは解像度非依存。
  - 既定で周囲の余白をトリムする（--no-trim で残す）。
  - PyMuPDF（fitz）は関数内で deferred import（module import は依存不要＝テストが skip 可能）。
    トリム時のみ Pillow を使う。
"""
from __future__ import annotations

import argparse
import sys
from typing import Any


def _require_fitz() -> Any:
    """PyMuPDF を deferred import する（未導入時は分かりやすい ImportError）。"""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover
        raise ImportError("PyMuPDF is required: pip install PyMuPDF") from exc
    return fitz


def validate_region(box: tuple[float, float, float, float]) -> None:
    """比率座標の妥当性を検証する（不正なら ValueError）。"""
    x0, y0, x1, y1 = box
    if not (0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0):
        raise ValueError(
            "fractional coords must satisfy 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1"
        )


def _trim_white(pix: Any) -> Any:
    """PyMuPDF pixmap（fitz.Pixmap）から周囲の白を除いた PIL 画像を返す。"""
    from PIL import Image, ImageChops

    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        pad = 6
        left = max(bbox[0] - pad, 0)
        top = max(bbox[1] - pad, 0)
        right = min(bbox[2] + pad, img.width)
        bottom = min(bbox[3] + pad, img.height)
        img = img.crop((left, top, right, bottom))
    return img


def render_page(pdf: str, page_no: int, out: str, dpi: int) -> None:
    if dpi <= 0:
        raise ValueError(f"dpi must be positive, got {dpi}")
    fitz = _require_fitz()
    with fitz.open(pdf) as doc:
        if not (1 <= page_no <= doc.page_count):
            raise ValueError(f"page {page_no} out of range (1..{doc.page_count})")
        pix = doc[page_no - 1].get_pixmap(dpi=dpi)
        pix.save(out)
        print(f"[page] {out} {pix.width}x{pix.height} (page {page_no}/{doc.page_count}, {dpi} dpi)")


def crop_region(
    pdf: str,
    page_no: int,
    box: tuple[float, float, float, float],
    out: str,
    dpi: int,
    trim: bool,
) -> None:
    validate_region(box)
    if dpi <= 0:
        raise ValueError(f"dpi must be positive, got {dpi}")
    x0, y0, x1, y1 = box
    fitz = _require_fitz()
    with fitz.open(pdf) as doc:
        if not (1 <= page_no <= doc.page_count):
            raise ValueError(f"page {page_no} out of range (1..{doc.page_count})")
        page = doc[page_no - 1]
        r = page.rect
        clip = fitz.Rect(
            r.x0 + x0 * r.width,
            r.y0 + y0 * r.height,
            r.x0 + x1 * r.width,
            r.y0 + y1 * r.height,
        )
        pix = page.get_pixmap(dpi=dpi, clip=clip)
        if trim:
            img = _trim_white(pix)
            img.save(out)
            w, h = img.size
        else:
            pix.save(out)
            w, h = pix.width, pix.height
        print(f"[region] {out} {w}x{h} (page {page_no}, box {box}, {dpi} dpi)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    p_page = sub.add_parser("page", help="render a whole page")
    p_page.add_argument("pdf")
    p_page.add_argument("page_no", type=int)
    p_page.add_argument("out")
    p_page.add_argument("--dpi", type=int, default=150)

    p_reg = sub.add_parser("region", help="crop a fractional bounding box")
    p_reg.add_argument("pdf")
    p_reg.add_argument("page_no", type=int)
    p_reg.add_argument("x0", type=float)
    p_reg.add_argument("y0", type=float)
    p_reg.add_argument("x1", type=float)
    p_reg.add_argument("y1", type=float)
    p_reg.add_argument("out")
    p_reg.add_argument("--dpi", type=int, default=300)
    p_reg.add_argument("--no-trim", dest="trim", action="store_false")

    args = ap.parse_args(argv)
    try:
        if args.mode == "page":
            render_page(args.pdf, args.page_no, args.out, args.dpi)
        else:
            crop_region(
                args.pdf, args.page_no, (args.x0, args.y0, args.x1, args.y1), args.out, args.dpi, args.trim
            )
    except (ValueError, ImportError, OSError) as exc:
        print(f"[crop_paper_figures] ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
