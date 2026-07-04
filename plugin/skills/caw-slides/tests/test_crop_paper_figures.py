"""crop_paper_figures のテスト（座標検証＋合成 PDF での切り抜きスモーク）。"""
import pytest

import crop_paper_figures as cpf


@pytest.mark.parametrize(
    "box",
    [
        (0.0, 0.0, 1.0, 1.0),
        (0.1, 0.2, 0.5, 0.6),
        (0.0, 0.0, 0.001, 0.001),
    ],
)
def test_validate_region_accepts_valid(box):
    cpf.validate_region(box)  # 例外なし


@pytest.mark.parametrize(
    "box",
    [
        (0.5, 0.0, 0.5, 1.0),   # x0 == x1
        (0.6, 0.0, 0.4, 1.0),   # x0 > x1
        (-0.1, 0.0, 0.5, 1.0),  # 負
        (0.0, 0.0, 1.1, 1.0),   # > 1
        (0.0, 0.8, 1.0, 0.2),   # y0 > y1
    ],
)
def test_validate_region_rejects_invalid(box):
    with pytest.raises(ValueError):
        cpf.validate_region(box)


def _make_pdf(path):
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.draw_rect(fitz.Rect(100, 100, 400, 400), fill=(0.8, 0.1, 0.1))
    doc.save(str(path))
    return str(path)


def test_crop_region_writes_png(tmp_path):
    pytest.importorskip("fitz")
    pytest.importorskip("PIL")
    pdf = _make_pdf(tmp_path / "src.pdf")
    out = tmp_path / "crop.png"
    cpf.crop_region(pdf, 1, (0.1, 0.1, 0.6, 0.6), str(out), dpi=100, trim=False)
    assert out.exists() and out.stat().st_size > 0
    from PIL import Image

    with Image.open(out) as im:
        assert im.width > 0 and im.height > 0


def test_crop_region_page_out_of_range(tmp_path):
    pytest.importorskip("fitz")
    pdf = _make_pdf(tmp_path / "src.pdf")
    with pytest.raises(ValueError):
        cpf.crop_region(pdf, 99, (0.1, 0.1, 0.6, 0.6), str(tmp_path / "x.png"), dpi=100, trim=False)


def test_render_page_writes_png(tmp_path):
    pytest.importorskip("fitz")
    pdf = _make_pdf(tmp_path / "src.pdf")
    out = tmp_path / "page.png"
    cpf.render_page(pdf, 1, str(out), dpi=80)
    assert out.exists() and out.stat().st_size > 0


def test_render_page_out_of_range(tmp_path):
    pytest.importorskip("fitz")
    pdf = _make_pdf(tmp_path / "src.pdf")
    with pytest.raises(ValueError):
        cpf.render_page(pdf, 99, str(tmp_path / "x.png"), dpi=80)
