"""copy_slide_pptx の検定: 1 枚を別の pptx へ写す（文字・図形・画像・位置・id）、画像の差し替え、ノート。"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path

import copy_slide_pptx as cs
import pytest
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.util import Emu


def _png(colour: tuple[int, int, int], size: tuple[int, int] = (40, 20)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, colour).save(buf, format="PNG")
    return buf.getvalue()


def _src(tmp_path: Path) -> Path:
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_textbox(Emu(100), Emu(200), Emu(3000), Emu(400)).text_frame.text = "補足 9"
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(500), Emu(600), Emu(700), Emu(800))
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0x1F, 0x77, 0xB4)
    s.shapes.add_picture(io.BytesIO(_png((200, 30, 30))), Emu(9000), Emu(9500), Emu(4000), Emu(2000))
    path = tmp_path / "src.pptx"
    prs.save(path)
    return path


def _dst(tmp_path: Path) -> Path:
    prs = Presentation()
    prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_textbox(Emu(1), Emu(1), Emu(2), Emu(2)).text_frame.text = "既存"
    path = tmp_path / "dst.pptx"
    prs.save(path)
    return path


def _blob_sha(shape) -> str:
    return hashlib.sha1(shape.image.blob).hexdigest()


def test_copy_keeps_text_shapes_pictures_and_positions(tmp_path: Path) -> None:
    src, dst = Presentation(_src(tmp_path)), Presentation(_dst(tmp_path))
    new = cs.copy_slide(src.slides[0], dst)
    out = tmp_path / "out.pptx"
    dst.save(out)
    got = Presentation(out)
    assert len(got.slides) == 2 and got.slides[0].shapes[0].text_frame.text == "既存"
    a, b = list(src.slides[0].shapes), list(got.slides[1].shapes)
    assert [(s.shape_type, s.left, s.top, s.width, s.height) for s in a] == [(s.shape_type, s.left, s.top, s.width, s.height) for s in b]
    assert b[0].text_frame.text == "補足 9"
    pa = next(s for s in a if s.shape_type == MSO_SHAPE_TYPE.PICTURE)
    pb = next(s for s in b if s.shape_type == MSO_SHAPE_TYPE.PICTURE)
    assert _blob_sha(pa) == _blob_sha(pb)
    ids = [s.shape_id for s in got.slides[1].shapes]
    assert len(ids) == len(set(ids)) and new is not None


def test_unsupported_relationship_is_refused(tmp_path: Path) -> None:
    src = Presentation(_src(tmp_path))
    tb = src.slides[0].shapes[0]
    tb.text_frame.paragraphs[0].runs[0].hyperlink.address = "https://example.com"
    with pytest.raises(ValueError):
        cs.copy_slide(src.slides[0], Presentation(_dst(tmp_path)))


def test_replace_picture_by_geometry_and_refuses_a_miss(tmp_path: Path) -> None:
    prs = Presentation(_src(tmp_path))
    slide = prs.slides[0]
    new_png = _png((10, 200, 10))
    name = cs.replace_picture(slide, (9000, 9500, 4000, 2000), new_png)
    pic = next(s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE)
    assert pic.name == name and pic.image.blob == new_png and (pic.left, pic.top, pic.width, pic.height) == (9000, 9500, 4000, 2000)
    with pytest.raises(LookupError):
        cs.replace_picture(slide, (9000 + 3 * cs.GEOMETRY_TOLERANCE_EMU, 9500, 4000, 2000), new_png)   # 3 px ずれ


def test_set_notes_replaces_the_text(tmp_path: Path) -> None:
    prs = Presentation(_src(tmp_path))
    cs.set_notes(prs.slides[0], "1 行目\n\n2 行目")
    assert prs.slides[0].notes_slide.notes_text_frame.text == "1 行目\n\n2 行目"


def _deck_with(tmp_path: Path, names: list[str], fname: str) -> Path:
    prs = Presentation()
    for n in names:
        prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_textbox(Emu(10), Emu(10), Emu(3000), Emu(400)).text_frame.text = n
    path = tmp_path / fname
    prs.save(path)
    return path


def test_replace_slide_keeps_the_order_and_count(tmp_path: Path) -> None:
    dst = Presentation(_deck_with(tmp_path, ["A", "B", "C"], "dst3.pptx"))
    src = Presentation(_deck_with(tmp_path, ["X"], "src1.pptx"))
    cs.replace_slide(dst, 2, src.slides[0])                 # 2 枚目（1 から数える）を X に
    out = tmp_path / "out3.pptx"
    dst.save(out)
    got = [s.shapes[0].text_frame.text for s in Presentation(out).slides]
    assert got == ["A", "X", "C"]


def test_copy_shapes_into_an_existing_slide_and_move_a_region(tmp_path: Path) -> None:
    src = Presentation(_src(tmp_path))
    dst = Presentation(_deck_with(tmp_path, ["既存"], "dst1.pptx"))
    before = len(dst.slides[0].shapes)
    n = cs.copy_shapes(src.slides[0], dst.slides[0], lambda s: s.shape_type != MSO_SHAPE_TYPE.PICTURE)
    assert n == 2 and len(dst.slides[0].shapes) == before + 2
    ids = [s.shape_id for s in dst.slides[0].shapes]
    assert len(ids) == len(set(ids))
    moved = cs.move_shapes(dst.slides[0], lambda s: s.top >= 600, Emu(1000))      # 矩形（600）だけ下へ
    rect = next(s for s in dst.slides[0].shapes if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE)
    assert moved == 1 and rect.top == 1600 and dst.slides[0].shapes[0].top == 10


def test_prepend_notes_line_keeps_the_rest_and_replaces_an_old_time_line(tmp_path: Path) -> None:
    prs = Presentation(_src(tmp_path))
    s = prs.slides[0]
    cs.set_notes(s, "本文 1\n\n本文 2")
    cs.prepend_notes_line(s, "0:00~1:30", replace_if=r"^\d+:\d{2}~\d+:\d{2}$")
    assert s.notes_slide.notes_text_frame.text == "0:00~1:30\n本文 1\n\n本文 2"
    cs.prepend_notes_line(s, "0:10~1:40", replace_if=r"^\d+:\d{2}~\d+:\d{2}$")     # 2 回目は置き換え（重ねない）
    assert s.notes_slide.notes_text_frame.text == "0:10~1:40\n本文 1\n\n本文 2"


def test_replace_slide_retargets_links_from_other_slides(tmp_path: Path) -> None:
    """他の枚からのリンクは新しい枚を指す（古い枚を指したままだと、見えない古い枚へ飛ぶ。Codex 2026-11-01）。"""
    prs = Presentation(_dst(tmp_path))
    old = prs.slides.add_slide(prs.slide_layouts[6])
    link = prs.slides[0].shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(0), Emu(0), Emu(9), Emu(9))
    link.click_action.target_slide = old
    new = cs.replace_slide(prs, 2, Presentation(_src(tmp_path)).slides[0])
    out = tmp_path / "out.pptx"
    prs.save(out)
    new_id = new.slide_id
    again = Presentation(out)
    assert again.slides[0].shapes[-1].click_action.target_slide.slide_id == new_id


def _with_picture_background(prs_path: Path, png: bytes) -> None:
    prs = Presentation(prs_path)
    slide = prs.slides[0]
    _, rid = slide.part.get_or_add_image_part(io.BytesIO(png))
    slide._element.cSld.insert(0, parse_xml(
        f'<p:bg {nsdecls("p", "a", "r")}><p:bgPr><a:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch>'
        '</a:blipFill><a:effectLst/></p:bgPr></p:bg>'))
    prs.save(prs_path)


def test_copy_slide_brings_the_picture_of_the_background(tmp_path: Path) -> None:
    """背景の画像も入れ直す（r:embed だけ写すと写し先に無い関係を指して PowerPoint が修復を求める。Codex 2026-11-01）。"""
    png = _png((9, 120, 9))
    src_path = _src(tmp_path)
    _with_picture_background(src_path, png)
    dst = Presentation(_dst(tmp_path))
    new = cs.copy_slide(Presentation(src_path).slides[0], dst)
    blip = new._element.cSld.find(cs.qn("p:bg")).find(".//" + cs.qn("a:blip"))
    assert new.part.related_part(blip.get(cs.qn("r:embed"))).blob == png


def _connected_slide(tmp_path: Path) -> Path:
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    a = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(0), Emu(0), Emu(100), Emu(100))
    b = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(500), Emu(0), Emu(100), Emu(100))
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(0), Emu(0), Emu(9), Emu(9))
    line.begin_connect(a, 3)
    line.end_connect(b, 1)
    path = tmp_path / "connected.pptx"
    prs.save(path)
    return path


def _endpoints(slide) -> tuple[str | None, str | None]:
    line = next(s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.LINE)
    st, end = [line._element.find(".//" + cs.qn(t)) for t in ("a:stCxn", "a:endCxn")]
    return (None if st is None else st.get("id"), None if end is None else end.get("id"))


def test_copied_connector_follows_the_renumbered_shapes(tmp_path: Path) -> None:
    """id を振り直したら結線の相手も付け替える（そのままだと別の図形へつながる。Codex 2026-11-01）。"""
    dst = Presentation(_dst(tmp_path))
    target = dst.slides[0]
    cs.copy_shapes(Presentation(_connected_slide(tmp_path)).slides[0], target)
    rectangles = [s for s in target.shapes if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE]
    assert _endpoints(target) == (str(rectangles[0].shape_id), str(rectangles[1].shape_id))


def test_connector_end_whose_shape_stays_behind_is_detached(tmp_path: Path) -> None:
    dst = Presentation(_dst(tmp_path))
    target = dst.slides[0]
    src = Presentation(_connected_slide(tmp_path)).slides[0]
    first = next(s for s in src.shapes if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE)
    cs.copy_shapes(src, target, keep=lambda s: s.shape_id != first.shape_id)
    rectangle = next(s for s in target.shapes if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE)
    assert _endpoints(target) == (None, str(rectangle.shape_id))
