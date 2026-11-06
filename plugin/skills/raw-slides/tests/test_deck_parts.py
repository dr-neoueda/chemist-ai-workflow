"""deck_parts のテスト: 中央寄せは単一フォント、表・図枠・矢印の組み立て。"""
import xml.etree.ElementTree as ET

import deck_parts as dp
import pytest
from PIL import Image

SVG = "{http://www.w3.org/2000/svg}"


def _parse(fragment: str) -> ET.Element:
    return ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{fragment}</svg>')


def test_centred_label_has_no_tspans():
    root = _parse(dp.centred(100, 100, "Fe-N 結合"))
    node = next(root.iter(f"{SVG}text"))
    assert node.get("text-anchor") == "middle" and not list(node.iter(f"{SVG}tspan"))


def test_table_has_one_highlight_row_and_navy_rule():
    frag = dp.table(80, 180, [0, 300], ["手法", "値"], [["DFT", "1.2"], ["MP2", ("1.1", dp.BLUE, True)]], highlight=1)
    rects = list(_parse(frag).iter(f"{SVG}rect"))
    assert len(rects) == 2 and rects[0].get("fill") == dp.NAVY


def test_table_rejects_a_row_with_the_wrong_number_of_cells():
    with pytest.raises(ValueError):
        dp.table(80, 180, [0, 300], ["手法", "値"], [["DFT"]])


def test_figure_box_keeps_the_png_aspect(tmp_path):
    png = tmp_path / "fig.png"
    Image.new("RGB", (400, 200), "white").save(png)
    markup, outer_w, outer_h = dp.figure(png, 80, 180, w=420)
    image = next(_parse(markup).iter(f"{SVG}image"))
    assert image.get("href") == "../images/fig.png"
    assert float(image.get("width")) / float(image.get("height")) == pytest.approx(2.0, rel=1e-3)
    assert (outer_w, outer_h) == (420, 220)


def test_figure_needs_exactly_one_of_width_or_height(tmp_path):
    png = tmp_path / "fig.png"
    Image.new("RGB", (10, 10)).save(png)
    with pytest.raises(ValueError):
        dp.figure(png, 0, 0)
    with pytest.raises(ValueError):
        dp.figure(png, 0, 0, w=10, h=10)


def test_arrow_head_is_a_polygon_not_a_marker():
    root = _parse(dp.arrow(0, 0, 100, 0))
    assert list(root.iter(f"{SVG}polygon")) and not list(root.iter(f"{SVG}marker"))


def test_figure_rejects_a_file_name_the_gates_cannot_follow(tmp_path):
    """``R&D.png`` は SVG で ``&amp;`` になり、svg_quality_checker が画像を見つけられない（実ゲートで確認）。"""
    png = tmp_path / "R&D.png"
    Image.new("RGB", (40, 20)).save(png)
    with pytest.raises(ValueError, match="R&D.png"):
        dp.figure(png, 80, 200, w=400)
