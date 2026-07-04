#!/usr/bin/env python3
"""LaTeX 数式を透過 PNG にレンダする（caw-slides・ハイブリッド）。

スライドに数式を載せるとき、LaTeX を**透過 PNG** に変換して SVG に `<image>` として
埋め込む（native shape でなくラスタになるのは数式の性質上の割り切り）。

backend は 2 段:
  1. **matplotlib mathtext（オフライン・既定）**：ネット不要・第三者送信なし・追加依存なし
     （matplotlib は解析でも使う）。速度論・熱力学・量子化学の数式サブセットを広くカバー。
  2. **オンライン provider（フォールバック・任意）**：mathtext で解釈できない式（フル LaTeX・
     mhchem の `\\ce{}` 等）は codecogs に投げてフル LaTeX でレンダ。**式が第三者 API に送られる**
     ため、既定はオフラインのみ・online_fallback=True 明示時だけ使う。

フォールバックは **mathtext がその式を解釈できないとき（または matplotlib 未導入）だけ**発火する。
保存失敗（OSError）や引数不正はローカルエラーとして `LatexRenderError` にし、codecogs には送らない。

Usage
-----
    python3 render_latex.py "k = A e^{-E_a/RT}" out.png
    python3 render_latex.py "\\ce{2H2 + O2 -> 2H2O}" out.png --online   # フル LaTeX/化学式

依存: matplotlib（オフライン）／urllib(stdlib, オンライン)。
テストは tests/test_render_latex.py（pytest）。
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Literal, TypedDict

DEFAULT_COLOR = "#16283D"  # design-system.md の ink
DEFAULT_DPI = 300
DEFAULT_FONTSIZE = 24
CODECOGS_ENDPOINT = "https://latex.codecogs.com/png.image?"
_CODECOGS_HOST = "latex.codecogs.com"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"  # 8 byte 固定
_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class RenderResult(TypedDict):
    """render_latex の戻り値。"""

    backend: Literal["matplotlib", "codecogs"]
    path: str


class LatexRenderError(RuntimeError):
    """どの backend でもレンダできなかった（またはローカルエラー）。"""


class _MathtextUnsupported(Exception):
    """matplotlib mathtext がこの式を解釈できない＝online フォールバックの対象（内部用）。"""


def _validate_color(color: str) -> str:
    """``'#RRGGBB'`` 形式を検証して返す（LaTeX への注入・不正色を防ぐ）。

    Parameters
    ----------
    color : str
        6 桁 hex カラー（例 ``'#16283D'``）。

    Returns
    -------
    str
        検証済みの ``color``。

    Raises
    ------
    LatexRenderError
        6 桁 hex でないとき。
    """
    if not _HEX_COLOR_RE.match(color):
        raise LatexRenderError(f"color は '#RRGGBB' の 6 桁 hex（例 '#16283D'）にしてください: {color!r}")
    return color


def _render_matplotlib(latex: str, out_path: str, *, dpi: int, color: str, fontsize: int) -> None:
    """matplotlib mathtext でオフラインに透過 PNG を作る。

    mathtext がその式を解釈できない場合・matplotlib 未導入の場合は ``_MathtextUnsupported``。
    保存失敗（OSError）はそのまま propagate（フォールバック対象にしない）。
    """
    try:
        import matplotlib
    except ImportError as exc:
        raise _MathtextUnsupported(f"matplotlib 未導入: {exc}") from exc

    if matplotlib.get_backend().lower() != "agg":
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(0.1, 0.1))
    fig.patch.set_alpha(0.0)
    try:
        text = fig.text(0.5, 0.5, f"${latex}$", fontsize=fontsize, color=color, ha="center", va="center")
        try:
            fig.canvas.draw()  # mathtext のパースはここで走る
        except Exception as exc:  # mathtext 非対応（\ce 等）→ フォールバック対象
            raise _MathtextUnsupported(str(exc)) from exc
        bbox = text.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(out_path, dpi=dpi, transparent=True, bbox_inches=bbox, pad_inches=0.03)
    finally:
        plt.close(fig)


def codecogs_url(latex: str, *, dpi: int, color: str) -> str:
    """codecogs のレンダ URL を組み立てる（純関数・テスト可能）。

    Parameters
    ----------
    latex : str
        LaTeX 数式（``$`` 不要）。
    dpi : int
        レンダ解像度。
    color : str
        6 桁 hex カラー（検証される）。

    Returns
    -------
    str
        ``https://latex.codecogs.com/...`` の完全 URL（全メタ文字を percent-encode）。

    Raises
    ------
    LatexRenderError
        ``color`` が不正なとき。
    """
    hex_color = _validate_color(color)[1:]
    expr = r"\dpi{%d}\bg{transparent}{\color[HTML]{%s} %s}" % (dpi, hex_color, latex)
    return CODECOGS_ENDPOINT + urllib.parse.quote(expr, safe="")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """リダイレクトを禁止する（別ホスト/http への転送を防ぐ）。"""

    def redirect_request(self, *args: object, **kwargs: object) -> None:  # type: ignore[override]
        return None


def _render_codecogs(latex: str, out_path: str, *, dpi: int, color: str, timeout: float) -> None:
    """codecogs にフル LaTeX を投げて透過 PNG を得る（要ネットワーク）。

    https かつ ``latex.codecogs.com`` のみ許可し、リダイレクトを禁止する（SSRF/ダウングレード防止）。
    """
    url = codecogs_url(latex, dpi=dpi, color=color)
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != _CODECOGS_HOST:
        raise LatexRenderError(f"codecogs URL が想定外（https/{_CODECOGS_HOST} のみ許可）: {url!r}")
    req = urllib.request.Request(url, headers={"User-Agent": "caw-slides"})
    opener = urllib.request.build_opener(_NoRedirect)
    with opener.open(req, timeout=timeout) as resp:  # noqa: S310 (scheme/host 検証済み・redirect 禁止)
        data = resp.read()
    if not data.startswith(_PNG_SIGNATURE):
        raise LatexRenderError("codecogs が PNG を返しませんでした（式の LaTeX を確認）")
    Path(out_path).write_bytes(data)


def render_latex(
    latex: str,
    out_path: str,
    *,
    dpi: int = DEFAULT_DPI,
    color: str = DEFAULT_COLOR,
    fontsize: int = DEFAULT_FONTSIZE,
    online_fallback: bool = False,
    timeout: float = 20.0,
) -> RenderResult:
    """LaTeX を透過 PNG にレンダする（matplotlib → 任意で codecogs フォールバック）。

    Parameters
    ----------
    latex : str
        LaTeX 数式（``$`` 不要）。
    out_path : str
        出力 PNG パス。
    dpi, color, fontsize
        解像度 / 色（6 桁 hex）/ フォントサイズ。
    online_fallback : bool
        mathtext で不可なとき codecogs にフォールバックするか（式を第三者に送る）。
    timeout : float
        オンライン取得のタイムアウト秒。

    Returns
    -------
    RenderResult
        ``{"backend": "matplotlib"|"codecogs", "path": out_path}``。

    Raises
    ------
    LatexRenderError
        空入力・不正色・保存失敗、または mathtext 不可かつ（online_fallback=False もしくは
        オンラインも失敗）のとき。
    """
    if not latex or not latex.strip():
        raise LatexRenderError("空の LaTeX です")
    _validate_color(color)  # 入口で検証（両 backend を安全に）
    try:
        _render_matplotlib(latex, out_path, dpi=dpi, color=color, fontsize=fontsize)
        return {"backend": "matplotlib", "path": out_path}
    except _MathtextUnsupported as exc:
        if not online_fallback:
            raise LatexRenderError(
                f"matplotlib mathtext で不可（{exc}）。フル LaTeX が要るなら online_fallback=True / --online"
            ) from exc
        try:
            _render_codecogs(latex, out_path, dpi=dpi, color=color, timeout=timeout)
            return {"backend": "codecogs", "path": out_path}
        except LatexRenderError:
            raise  # 既に well-typed（再ラップしない）
        except Exception as online_exc:  # ネット障害等
            raise LatexRenderError(
                f"matplotlib 不可（{exc}）・codecogs も失敗（{online_exc}）"
            ) from online_exc
    except OSError as exc:  # PNG 保存失敗はローカルエラー（フォールバックしない）
        raise LatexRenderError(f"PNG 保存に失敗: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="LaTeX 数式を透過 PNG にレンダ (render_latex)")
    p.add_argument("latex", help="LaTeX 数式（$ は不要）")
    p.add_argument("out", help="出力 PNG パス")
    p.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    p.add_argument("--color", default=DEFAULT_COLOR)
    p.add_argument("--fontsize", type=int, default=DEFAULT_FONTSIZE)
    p.add_argument("--online", dest="online_fallback", action="store_true",
                   help="mathtext で不可なら codecogs にフォールバック（式が第三者に送られる）")
    args = p.parse_args(argv)
    try:
        result = render_latex(
            args.latex, args.out, dpi=args.dpi, color=args.color,
            fontsize=args.fontsize, online_fallback=args.online_fallback,
        )
    except LatexRenderError as exc:
        print(f"[render_latex] ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"[render_latex] {result['backend']} → {result['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
