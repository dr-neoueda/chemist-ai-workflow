"""ungroup_pptx の検定: グループが 0 になり、葉の図形の数と絶対位置が変わらないこと。"""
from __future__ import annotations

from pathlib import Path

import pytest
import ungroup_pptx as ug
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pptx.util import Emu


def _leaves(shapes) -> list:
    out = []
    for sh in shapes:
        out += _leaves(sh.shapes) if sh.shape_type == MSO_SHAPE_TYPE.GROUP else [sh]
    return out


def _groups(prs) -> int:
    return sum(1 for sl in prs.slides for sh in sl.shapes if sh.shape_type == MSO_SHAPE_TYPE.GROUP)


def _deck(tmp_path: Path) -> Path:
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(100), Emu(100), Emu(50), Emu(50))
    outer = slide.shapes.add_group_shape()
    outer.shapes.add_shape(MSO_SHAPE.OVAL, Emu(1000), Emu(2000), Emu(300), Emu(400))
    inner = outer.shapes.add_group_shape()
    inner.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(5000), Emu(6000), Emu(700), Emu(800))
    inner.shapes.add_textbox(Emu(9000), Emu(9500), Emu(1000), Emu(500)).text_frame.text = "文字"
    path = tmp_path / "in.pptx"
    prs.save(path)
    return path


def test_nested_groups_are_flattened_and_positions_kept(tmp_path: Path) -> None:
    src = _deck(tmp_path)
    before = [(s.left, s.top, s.width, s.height) for s in _leaves(Presentation(src).slides[0].shapes)]
    out = tmp_path / "out.pptx"
    report = ug.ungroup(src, out)
    prs = Presentation(out)
    assert _groups(prs) == 0 and report["groups_removed"] == 2
    after = [(s.left, s.top, s.width, s.height) for s in prs.slides[0].shapes]
    assert after == before                                   # 順（重なりの順）も位置も同じ
    assert prs.slides[0].shapes[-1].text_frame.text == "文字"


def test_scaled_group_applies_the_group_transform(tmp_path: Path) -> None:
    src = _deck(tmp_path)
    prs = Presentation(src)
    grp = next(s for s in prs.slides[0].shapes if s.shape_type == MSO_SHAPE_TYPE.GROUP)
    xfrm = grp._element.grpSpPr.find(ug.qn("a:xfrm"))
    ext, ch_off = xfrm.find(ug.qn("a:ext")), xfrm.find(ug.qn("a:chOff"))
    ext.set("cx", str(2 * int(xfrm.find(ug.qn("a:chExt")).get("cx"))))   # 横だけ 2 倍に引き伸ばしたグループ
    x0 = int(xfrm.find(ug.qn("a:off")).get("x"))
    prs.save(src)
    out = tmp_path / "out.pptx"
    ug.ungroup(src, out)
    oval = Presentation(out).slides[0].shapes[1]
    assert oval.left == x0 + 2 * (1000 - int(ch_off.get("x"))) and oval.width == 600 and oval.height == 400


def test_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ug.ungroup(tmp_path / "none.pptx", tmp_path / "out.pptx")


def test_each_unflattenable_group_is_reported_once(tmp_path: Path) -> None:
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    for k in range(3):
        grp = slide.shapes.add_group_shape()
        grp.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(100 * k), Emu(100), Emu(50), Emu(50))
        grp._element.grpSpPr.find(qn("a:xfrm")).set("rot", "5400000")
    src, out = tmp_path / "in.pptx", tmp_path / "out.pptx"
    prs.save(src)
    report = ug.ungroup(src, out)
    assert len(report["skipped"]) == 3
    assert len({group_id for _, group_id, _ in report["skipped"]}) == 3
