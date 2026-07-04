"""render_latex のテスト（matplotlib オフライン + codecogs URL/セキュリティ）。"""
import io
from pathlib import Path

import pytest

import render_latex as rl

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _is_png(path: Path | str) -> bool:
    with open(path, "rb") as fh:
        return fh.read(8) == _PNG_SIGNATURE


def test_codecogs_url_is_pure_and_encodes():
    url = rl.codecogs_url("k = A", dpi=300, color="#16283D")
    assert url.startswith(rl.CODECOGS_ENDPOINT)
    assert "300" in url  # dpi
    assert "16283D" in url  # color（# は除去）
    assert "%23" not in url  # 生の # は入れない
    assert "transparent" in url


def test_codecogs_url_rejects_bad_color_injection():
    """color に `}` を入れて wrapper を壊す注入を弾く。"""
    with pytest.raises(rl.LatexRenderError):
        rl.codecogs_url("x", dpi=300, color="#abc}\\textbf{")
    with pytest.raises(rl.LatexRenderError):
        rl.codecogs_url("x", dpi=300, color="notahex")


def test_empty_latex_raises():
    with pytest.raises(rl.LatexRenderError):
        rl.render_latex("", "/tmp/x.png")
    with pytest.raises(rl.LatexRenderError):
        rl.render_latex("   ", "/tmp/x.png")


def test_invalid_color_raises_in_render(tmp_path):
    with pytest.raises(rl.LatexRenderError):
        rl.render_latex("k=A", str(tmp_path / "x.png"), color="red")


def test_matplotlib_renders_math_to_transparent_png(tmp_path):
    pytest.importorskip("matplotlib")
    out = tmp_path / "eq.png"
    result = rl.render_latex("k = A e^{-E_a/RT}", str(out), dpi=120)
    assert result["backend"] == "matplotlib"
    assert out.exists() and out.stat().st_size > 0
    assert _is_png(out)


def test_matplotlib_handles_common_chem_math(tmp_path):
    """熱力学・量子化学の数式サブセットは mathtext で通ること。"""
    pytest.importorskip("matplotlib")
    for i, expr in enumerate([r"\Delta G = \Delta H - T\Delta S", r"\langle \psi | H | \psi \rangle"]):
        out = tmp_path / f"e{i}.png"
        assert rl.render_latex(expr, str(out), dpi=120)["backend"] == "matplotlib"
        assert _is_png(out)


def test_rendered_png_is_transparent(tmp_path):
    pytest.importorskip("matplotlib")
    pytest.importorskip("PIL")
    from PIL import Image

    out = tmp_path / "t.png"
    rl.render_latex("x = 1", str(out), dpi=120)
    with Image.open(out) as im:
        assert im.mode in ("RGBA", "LA") or "transparency" in im.info


def test_unsupported_latex_without_fallback_raises(tmp_path):
    """mhchem の \\ce{} は mathtext 非対応 → online_fallback=False なら LatexRenderError。"""
    pytest.importorskip("matplotlib")
    out = tmp_path / "chem.png"
    with pytest.raises(rl.LatexRenderError):
        rl.render_latex(r"\ce{2H2 + O2 -> 2H2O}", str(out), online_fallback=False)


def test_online_fallback_uses_codecogs(monkeypatch, tmp_path):
    """フォールバック時、codecogs にダウンロードを試みる（ネットはモック）。"""
    pytest.importorskip("matplotlib")
    called = {}

    def fake_codecogs(latex, out_path, *, dpi, color, timeout):
        called["latex"] = latex
        called["url"] = rl.codecogs_url(latex, dpi=dpi, color=color)
        Path(out_path).write_bytes(_PNG_SIGNATURE)  # 正しい 8 byte シグネチャ

    monkeypatch.setattr(rl, "_render_codecogs", fake_codecogs)
    out = tmp_path / "chem.png"
    result = rl.render_latex(r"\ce{H2O}", str(out), online_fallback=True)
    assert result["backend"] == "codecogs"
    assert called["latex"] == r"\ce{H2O}"
    assert rl.CODECOGS_ENDPOINT in called["url"]
    assert _is_png(out)


def test_double_failure_raises_single_latexerror(monkeypatch, tmp_path):
    """online フォールバックも失敗したら LatexRenderError（二重ラップしない）。"""
    pytest.importorskip("matplotlib")

    def boom(latex, out_path, *, dpi, color, timeout):
        raise rl.LatexRenderError("network down")

    monkeypatch.setattr(rl, "_render_codecogs", boom)
    with pytest.raises(rl.LatexRenderError):
        rl.render_latex(r"\ce{H2O}", str(tmp_path / "x.png"), online_fallback=True)


def test_codecogs_rejects_non_png(monkeypatch, tmp_path):
    """codecogs が PNG でない応答を返したら LatexRenderError（署名検証）。"""

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            self.close()

    class _Opener:
        def open(self, req, timeout=None):
            return _Resp(b"<html>error</html>")

    monkeypatch.setattr(rl.urllib.request, "build_opener", lambda *a, **k: _Opener())
    with pytest.raises(rl.LatexRenderError):
        rl._render_codecogs("x", str(tmp_path / "x.png"), dpi=200, color="#16283D", timeout=5)


def test_codecogs_rejects_non_codecogs_host(monkeypatch, tmp_path):
    """URL が codecogs 以外に差し替えられたら弾く（SSRF 防止）。"""
    monkeypatch.setattr(rl, "codecogs_url", lambda *a, **k: "https://evil.example.com/x.png")
    with pytest.raises(rl.LatexRenderError):
        rl._render_codecogs("x", str(tmp_path / "x.png"), dpi=200, color="#16283D", timeout=5)


def test_main_cli_success(tmp_path):
    pytest.importorskip("matplotlib")
    out = tmp_path / "cli.png"
    assert rl.main(["k = A", str(out)]) == 0
    assert _is_png(out)


def test_main_cli_error_returns_1(tmp_path):
    pytest.importorskip("matplotlib")
    # \ce は mathtext 不可 かつ --online なし → return 1
    assert rl.main([r"\ce{H2O}", str(tmp_path / "x.png")]) == 1
