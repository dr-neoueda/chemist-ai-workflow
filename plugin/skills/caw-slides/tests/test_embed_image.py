"""embed_image のテスト（data-URI 化・アスペクト fit・href インライン・堅牢な regex）。"""
import base64

import pytest

import embed_image as ei

# 1x1 透過 PNG（PIL 不要でファイルを用意する用）
_PNG_1x1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
_JPEG_MAGIC = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x00\x00"


def _png(tmp_path, name="a.png"):
    p = tmp_path / name
    p.write_bytes(_PNG_1x1)
    return p


# --- data_uri / MIME -------------------------------------------------------

def test_data_uri_png(tmp_path):
    p = _png(tmp_path)
    uri = ei.data_uri(str(p))
    assert uri.startswith("data:image/png;base64,")
    assert base64.b64decode(uri.split(",", 1)[1]) == _PNG_1x1


def test_data_uri_mime_from_magic_beats_extension(tmp_path):
    """PNG 内容の .jpg は magic bytes 優先で image/png（拡張子に騙されない）。"""
    p = tmp_path / "misnamed.jpg"
    p.write_bytes(_PNG_1x1)
    assert ei.data_uri(str(p)).startswith("data:image/png;base64,")


def test_data_uri_jpeg_magic(tmp_path):
    p = tmp_path / "b.jpg"
    p.write_bytes(_JPEG_MAGIC)
    assert ei.data_uri(str(p)).startswith("data:image/jpeg;base64,")


def test_data_uri_svg(tmp_path):
    p = tmp_path / "c.svg"
    p.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    assert ei.data_uri(str(p)).startswith("data:image/svg+xml;base64,")


def test_data_uri_unsupported_raises(tmp_path):
    p = tmp_path / "d.bin"
    p.write_bytes(b"\x00\x01\x02\x03not an image")
    with pytest.raises(ValueError):
        ei.data_uri(str(p))


def test_data_uri_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ei.data_uri(str(tmp_path / "nope.png"))


# --- fit_box ---------------------------------------------------------------

@pytest.mark.parametrize(
    "iw,ih,mw,mh,ew,eh",
    [
        (1000, 500, 400, 400, 400, 200),   # 横長 → 幅で制限
        (500, 1000, 400, 400, 200, 400),   # 縦長 → 高さで制限
        (200, 200, 400, 400, 200, 200),    # 小さい → 拡大せず（既定）
    ],
)
def test_fit_box_preserves_aspect_no_upscale(iw, ih, mw, mh, ew, eh):
    w, h = ei.fit_box(iw, ih, mw, mh)
    assert (round(w), round(h)) == (ew, eh)


def test_fit_box_allow_upscale():
    w, h = ei.fit_box(200, 100, 400, 400, allow_upscale=True)
    assert (round(w), round(h)) == (400, 200)


def test_fit_box_rejects_nonpositive():
    with pytest.raises(ValueError):
        ei.fit_box(0, 100, 400, 400)


# --- inline_image_hrefs（regex 堅牢性）--------------------------------------

@pytest.mark.parametrize(
    "attr",
    [
        'href="fig.png"',
        "href='fig.png'",
        'href = "fig.png"',
        "xlink:href='fig.png'",
        'xlink:href="fig.png"',
    ],
)
def test_inline_matches_quote_and_spacing_variants(tmp_path, attr):
    _png(tmp_path, "fig.png")
    svg = f"<svg><image {attr} x='1'/></svg>"
    out = ei.inline_image_hrefs(svg, base_dir=str(tmp_path))
    assert "data:image/png;base64," in out
    assert "fig.png" not in out


def test_inline_ignores_data_href_attr(tmp_path):
    """data-href（カスタム属性）は書き換えず、本物の href だけ埋める。"""
    _png(tmp_path, "bar.png")
    svg = '<svg><image data-href="thumb.png" href="bar.png"/></svg>'
    out = ei.inline_image_hrefs(svg, base_dir=str(tmp_path))
    assert 'data-href="thumb.png"' in out  # 触らない
    assert 'href="data:image/png;base64,' in out


def test_inline_multiple_images_one_line(tmp_path):
    _png(tmp_path, "a.png")
    _png(tmp_path, "b.png")
    svg = '<svg><image href="a.png"/><image href="b.png"/></svg>'
    out = ei.inline_image_hrefs(svg, base_dir=str(tmp_path))
    assert out.count("data:image/png;base64,") == 2


def test_inline_ignores_commented_image(tmp_path):
    """コメント内の <image> は読み込まない（存在しなくても例外にならない）。"""
    _png(tmp_path, "real.png")
    svg = '<svg><!-- <image href="ghost.png"/> --><image href="real.png"/></svg>'
    out = ei.inline_image_hrefs(svg, base_dir=str(tmp_path))
    assert '<!-- <image href="ghost.png"/> -->' in out  # コメント verbatim
    assert out.count("data:image/png;base64,") == 1


@pytest.mark.parametrize(
    "ref",
    ["data:image/png;base64,AAAA", "http://x/y.png", "https://x/y.png",
     "HTTPS://x/y.png", "DATA:image/png;base64,AAAA"],
)
def test_inline_skips_remote_and_data(ref):
    svg = f'<svg><image href="{ref}"/></svg>'
    assert ei.inline_image_hrefs(svg) == svg  # 変化なし


def test_inline_missing_file_raises(tmp_path):
    svg = '<svg><image href="missing.png"/></svg>'
    with pytest.raises(FileNotFoundError):
        ei.inline_image_hrefs(svg, base_dir=str(tmp_path))


def test_inline_rejects_traversal(tmp_path):
    svg = '<svg><image href="../outside.png"/></svg>'
    with pytest.raises(ValueError):
        ei.inline_image_hrefs(svg, base_dir=str(tmp_path))


def test_inline_rejects_absolute_without_allow_outside(tmp_path):
    svg = '<svg><image href="/etc/hosts"/></svg>'
    with pytest.raises(ValueError):
        ei.inline_image_hrefs(svg, base_dir=str(tmp_path))


def test_inline_allow_outside_permits_absolute(tmp_path):
    p = _png(tmp_path, "abs.png")
    svg = f'<svg><image href="{p}"/></svg>'
    out = ei.inline_image_hrefs(svg, base_dir="/nonexistent", allow_outside=True)
    assert "data:image/png;base64," in out


# --- image_size / CLI ------------------------------------------------------

def test_image_size_with_pillow(tmp_path):
    pytest.importorskip("PIL.Image")
    from PIL import Image

    p = tmp_path / "sz.png"
    Image.new("RGBA", (320, 200), (0, 0, 0, 0)).save(p)
    assert ei.image_size(str(p)) == (320, 200)


def test_main_datauri(tmp_path, capsys):
    p = _png(tmp_path)
    assert ei.main(["datauri", str(p)]) == 0
    assert capsys.readouterr().out.startswith("data:image/png;base64,")


def test_main_inline(tmp_path):
    _png(tmp_path, "fig.png")
    src = tmp_path / "in.svg"
    src.write_text('<svg><image href="fig.png"/></svg>', encoding="utf-8")
    dst = tmp_path / "out.svg"
    assert ei.main(["inline", str(src), str(dst), "--base-dir", str(tmp_path)]) == 0
    assert "data:image/png;base64," in dst.read_text(encoding="utf-8")


def test_main_inline_missing_returns_1(tmp_path):
    src = tmp_path / "in.svg"
    src.write_text('<svg><image href="nope.png"/></svg>', encoding="utf-8")
    assert ei.main(["inline", str(src), str(tmp_path / "out.svg"), "--base-dir", str(tmp_path)]) == 1
