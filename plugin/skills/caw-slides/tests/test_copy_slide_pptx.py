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
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
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
