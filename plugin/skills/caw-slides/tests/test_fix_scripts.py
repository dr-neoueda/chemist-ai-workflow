"""fix_scripts のテスト: 変換器が捨てる baseline-shift を行単位で pptx へ戻す。"""
from pathlib import Path

import fix_scripts as fx
import pytest
from pptx import Presentation
from pptx.presentation import Presentation as PptxPresentation
from pptx.util import Pt

SVG_TEXT = ('<svg xmlns="http://www.w3.org/2000/svg"><text x="80" y="200" font-size="20">cm'
            '<tspan baseline-shift="super" font-size="14">-1</tspan> の吸収</text></svg>')


def _deck(tmp_path, runs):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    para = slide.shapes.add_textbox(0, 0, 1000, 1000).text_frame.paragraphs[0]
    for text, size in runs:
        run = para.add_run()
        run.text, run.font.size = text, Pt(size)
    path = tmp_path / "deck.pptx"
    prs.save(path)
    (tmp_path / "svg").mkdir(exist_ok=True)
    return path, tmp_path / "svg"


def test_script_run_gets_baseline_and_line_size(tmp_path):
    path, svgs = _deck(tmp_path, [("cm", 15), ("-1", 10.5), (" の吸収", 15)])
    (svgs / "01.svg").write_text(SVG_TEXT, encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 1
    run = Presentation(path).slides[0].shapes[0].text_frame.paragraphs[0].runs[1]
    assert run.font.size == Pt(15)
    assert run._r.rPr.get("baseline") == "30000"


def test_deck_without_scripts_is_left_alone(tmp_path):
    path, svgs = _deck(tmp_path, [("本文", 15)])
    (svgs / "01.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>本文</text></svg>', encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 0


def test_unmatched_line_stops_without_saving(tmp_path):
    path, svgs = _deck(tmp_path, [("別の文", 15)])
    (svgs / "01.svg").write_text(SVG_TEXT, encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(fx.ScriptMismatch, match="1 行 1"):
        fx.fix_scripts(path, svgs)
    assert path.read_bytes() == before


def test_slide_count_mismatch_is_an_error(tmp_path):
    path, svgs = _deck(tmp_path, [("本文", 15)])
    with pytest.raises(fx.ScriptMismatch, match="枚"):
        fx.fix_scripts(path, svgs)


def test_ideographic_space_matches_the_converted_space(tmp_path):
    """変換器は全角空白を半角へ置き換えるので、照合の前に空白をそろえる。"""
    path, svgs = _deck(tmp_path, [("1", 9.8), ("所属大学院 ", 14)])
    (svgs / "01.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><text font-size="18"><tspan baseline-shift="super" '
                                 'font-size="12">1</tspan>所属大学院　</text></svg>', encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 1


TWO_SAME = ('<svg xmlns="http://www.w3.org/2000/svg"><text font-size="20">cm-1</text>'
            '<text font-size="20">cm<tspan baseline-shift="super" font-size="14">-1</tspan></text></svg>')


def _two_paragraph_deck(tmp_path):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    for runs in ([("cm-1", 15)], [("cm", 15), ("-1", 10.5)]):
        para = slide.shapes.add_textbox(0, 0, 1000, 1000).text_frame.paragraphs[0]
        for text, size in runs:
            run = para.add_run()
            run.text, run.font.size = text, Pt(size)
    path = tmp_path / "deck.pptx"
    prs.save(path)
    (tmp_path / "svg").mkdir()
    return path, tmp_path / "svg"


def test_same_text_without_script_does_not_steal_the_line(tmp_path):
    path, svgs = _two_paragraph_deck(tmp_path)
    (svgs / "01.svg").write_text(TWO_SAME, encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 1
    runs = Presentation(path).slides[0].shapes[1].text_frame.paragraphs[0].runs
    assert runs[1]._r.rPr.get("baseline") == "30000"


def test_same_text_lines_with_different_shifts_keep_their_order(tmp_path):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    for _ in range(2):
        para = slide.shapes.add_textbox(0, 0, 1000, 1000).text_frame.paragraphs[0]
        for text, size in (("H", 15), ("2", 10.5)):
            run = para.add_run()
            run.text, run.font.size = text, Pt(size)
    path = tmp_path / "deck.pptx"
    prs.save(path)
    (tmp_path / "svg").mkdir()
    (tmp_path / "svg" / "01.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><text>H<tspan baseline-shift="super" font-size="10">2</tspan></text>'
        '<text>H<tspan baseline-shift="sub" font-size="10">2</tspan></text></svg>', encoding="utf-8")
    assert fx.fix_scripts(path, tmp_path / "svg") == 2
    shapes = Presentation(path).slides[0].shapes
    assert [s.text_frame.paragraphs[0].runs[1]._r.rPr.get("baseline") for s in shapes] == ["30000", "-25000"]


def test_differing_count_of_same_text_lines_is_ambiguous(tmp_path):
    path, svgs = _deck(tmp_path, [("cm", 15), ("-1", 10.5)])
    (svgs / "01.svg").write_text(TWO_SAME, encoding="utf-8")
    with pytest.raises(fx.ScriptMismatch):
        fx.fix_scripts(path, svgs)


def test_failure_on_a_later_slide_saves_nothing(tmp_path):
    prs = Presentation()
    for body in ("cm-1", "別の文"):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        para = slide.shapes.add_textbox(0, 0, 1000, 1000).text_frame.paragraphs[0]
        if body == "cm-1":
            for text, size in (("cm", 15), ("-1", 10.5)):
                run = para.add_run()
                run.text, run.font.size = text, Pt(size)
        else:
            run = para.add_run()
            run.text, run.font.size = body, Pt(15)
    path = tmp_path / "deck.pptx"
    prs.save(path)
    (tmp_path / "svg").mkdir()
    for name in ("01.svg", "02.svg"):
        (tmp_path / "svg" / name).write_text(SVG_TEXT.replace(" の吸収", ""), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(fx.ScriptMismatch):
        fx.fix_scripts(path, tmp_path / "svg")
    assert path.read_bytes() == before


def test_svg_indentation_inside_text_does_not_break_matching(tmp_path):
    path, svgs = _deck(tmp_path, [("cm", 15), ("-1", 10.5)])
    (svgs / "01.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><text font-size="20">\n    cm'
                                 '<tspan baseline-shift="super" font-size="14">-1</tspan>\n  </text></svg>', encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 1


def test_paragraph_without_sizes_is_a_mismatch_not_a_crash(tmp_path):
    path, svgs = _deck(tmp_path, [])
    prs = Presentation(path)
    prs.slides[0].shapes[0].text_frame.paragraphs[0].add_run().text = "cm-1"
    prs.save(path)
    (svgs / "01.svg").write_text(SVG_TEXT.replace(" の吸収", ""), encoding="utf-8")
    with pytest.raises(fx.ScriptMismatch):
        fx.fix_scripts(path, svgs)


def test_small_plain_run_with_the_same_text_keeps_its_place(tmp_path):
    """添字は行の中の位置でも照合する。同じ文字の小さい run に取られない（Codex 2026-11-01）。"""
    path, svgs = _deck(tmp_path, [("2", 10.5), (" H", 15), ("2", 10.5)])
    (svgs / "01.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><text><tspan font-size="14">2</tspan> H'
                                 '<tspan baseline-shift="super" font-size="14">2</tspan></text></svg>', encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 1
    runs = Presentation(path).slides[0].shapes[0].text_frame.paragraphs[0].runs
    assert runs[0]._r.rPr.get("baseline") is None and runs[2]._r.rPr.get("baseline") == "30000"


def test_spaces_around_a_script_do_not_stop_the_run(tmp_path):
    path, svgs = _deck(tmp_path, [("cm", 15), (" -1", 10.5)])
    (svgs / "01.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>cm<tspan baseline-shift="super" '
                                 'font-size="14">  -1  </tspan></text></svg>', encoding="utf-8")
    assert fx.fix_scripts(path, svgs) == 1


def test_failed_write_leaves_the_deck_untouched(tmp_path, monkeypatch):
    """書き込みの途中で落ちても元の pptx は壊れない（Codex 2026-11-01）。"""
    path, svgs = _deck(tmp_path, [("cm", 15), ("-1", 10.5), (" の吸収", 15)])
    (svgs / "01.svg").write_text(SVG_TEXT, encoding="utf-8")
    before = path.read_bytes()

    def fail_midway(self, target):
        Path(target).write_bytes(b"partial")
        raise OSError("disk full")

    monkeypatch.setattr(PptxPresentation, "save", fail_midway)
    with pytest.raises(OSError, match="disk full"):
        fx.fix_scripts(path, svgs)
    assert path.read_bytes() == before
    assert [p.name for p in tmp_path.iterdir() if p.is_file()] == ["deck.pptx"]
