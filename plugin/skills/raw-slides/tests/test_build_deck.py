"""build_deck のテスト: 検定に落ちたら配布先へ出さない・書き出しの後処理と出力検定・手編集の保護。"""
import zipfile

import build_deck as bd
import deck_chrome as dc
import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn


def _write(project, name, body):
    (project / "svg_output").mkdir(parents=True, exist_ok=True)
    (project / "svg_output" / name).write_text(dc.svg(body), encoding="utf-8")


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "slides" / "_src" / "demo"
    body = dc.header("赤外吸収") + '  <g id="content">\n' + dc.bullet(80, 190, "吸収は 1700 cm^{-1} に現れる")
    body += dc.callout(80, 300, 1120, 60, ["カルボニル ① の伸縮"]) + "  </g>\n" + dc.footer(1, 2)
    _write(root, "01_ir.svg", body)
    _write(root, "02_end.svg", dc.header("結論") + dc.footer(2, 2))
    return root


def _slides_xml(path):
    with zipfile.ZipFile(path) as z:
        return [z.read(n).decode("utf-8") for n in z.namelist() if n.startswith("ppt/slides/slide")]


def test_default_output_sits_next_to_src(project):
    assert bd.default_output(project) == project.parent.parent / "demo.pptx"


def test_build_writes_a_clean_deck(project):
    out = bd.build(project)
    assert out.exists()
    prs = Presentation(out)
    assert len(prs.slides) == 2
    assert not any("<p:transition" in x for x in _slides_xml(out))
    assert not any(s.shape_type == MSO_SHAPE_TYPE.GROUP for sl in prs.slides for s in sl.shapes)


def test_superscript_survives_to_the_pptx(project):
    out = bd.build(project)
    runs = [r for s in Presentation(out).slides[0].shapes if s.has_text_frame
            for p in s.text_frame.paragraphs for r in p.runs]
    assert any(r.text == "-1" and r._r.rPr.get("baseline") == "30000" for r in runs)


def test_circled_digit_run_gets_ms_gothic(project):
    out = bd.build(project)
    runs = [r for s in Presentation(out).slides[0].shapes if s.has_text_frame
            for p in s.text_frame.paragraphs for r in p.runs if "①" in r.text]
    assert runs and all(r._r.rPr.find(qn("a:ea")).get("typeface") == "MS Gothic" for r in runs)


def test_gate_failure_stops_before_writing_the_output(project):
    _write(project, "03_bad.svg", '<text x="80" y="200" font-size="18.67" font-family="Arial">日本語</text>')
    with pytest.raises(bd.BuildError, match="assert_font_rule"):
        bd.build(project)
    assert not bd.default_output(project).exists()


def test_margin_gate_is_on(project):
    _write(project, "03_wide.svg", dc.text(1150, 300, "余白の手前"))
    with pytest.raises(bd.BuildError, match="check_margins"):
        bd.build(project)


def test_missing_svg_output_is_a_clear_error(tmp_path):
    with pytest.raises(bd.BuildError, match="svg_output"):
        bd.build(tmp_path)


def test_hand_edited_output_is_not_overwritten(project):
    out = bd.build(project)
    edited = Presentation(out)
    edited.slides[0].shapes[0].text_frame.text = "手で直した"
    edited.save(out)
    before = out.read_bytes()
    with pytest.raises(bd.BuildError, match="手で"):
        bd.build(project)
    assert out.read_bytes() == before


def test_force_overwrites_a_hand_edited_output(project):
    out = bd.build(project)
    out.write_bytes(out.read_bytes() + b"\0")
    bd.build(project, force=True)
    assert bd.verify_output(out) == []


def test_unknown_existing_output_is_protected_too(project):
    out = bd.default_output(project)
    out.write_bytes(b"not built here")
    with pytest.raises(bd.BuildError, match="手で"):
        bd.build(project)


def test_rebuild_of_an_untouched_output_is_allowed(project):
    bd.build(project)
    bd.build(project)


def test_verify_output_reports_a_transition(tmp_path, project):
    out = bd.build(project)
    bad = tmp_path / "bad.pptx"
    with zipfile.ZipFile(out) as zin, zipfile.ZipFile(bad, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "ppt/slides/slide1.xml":
                data = data.replace(b"</p:sld>", b"<p:transition/></p:sld>")
            zout.writestr(item, data)
    assert any("切り替え" in p for p in bd.verify_output(bad))


def test_verify_output_reports_a_wrong_east_asian_font(tmp_path, project):
    out = bd.build(project)
    prs = Presentation(out)
    run = next(r for s in prs.slides[0].shapes if s.has_text_frame for p in s.text_frame.paragraphs
               for r in p.runs if "吸収" in r.text)
    run._r.rPr.find(qn("a:ea")).set("typeface", "Microsoft YaHei")
    bad = tmp_path / "bad.pptx"
    prs.save(bad)
    assert any("MS Gothic" in p for p in bd.verify_output(bad))


def test_small_text_is_counted_for_review(project):
    _write(project, "03_note.svg", dc.text(80, 660, "出典: 誌名 2024, 1, 1", size=13, fine=True))
    out = bd.build(project)
    assert set(bd.small_text_count(out)) == {1, 2, 3}          # ページ番号の 2 枚と注の 1 枚


def test_failed_postprocess_leaves_no_work_file(project):
    (project / "videos.json").write_text('[{"slide": "99_x", "mp4": "a", "poster": "b", "x": 0, "y": 0, "w": 1, "h": 1}]',
                                          encoding="utf-8")
    with pytest.raises(bd.BuildError, match="99_x"):
        bd.build(project)
    assert not (project / bd.WORK_NAME).exists()
    assert not bd.default_output(project).exists()


def test_notes_reach_the_slide(project):
    (project / "notes").mkdir()
    (project / "notes" / "01_ir.md").write_text("カルボニルの話から始める", encoding="utf-8")
    out = bd.build(project)
    assert "カルボニル" in Presentation(out).slides[0].notes_slide.notes_text_frame.text


def test_failed_gate_leaves_an_existing_output_byte_identical(project):
    out = bd.build(project)
    before = out.read_bytes()
    _write(project, "03_bad.svg", '<text x="80" y="200" font-size="18.67" font-family="Arial">日本語</text>')
    with pytest.raises(bd.BuildError):
        bd.build(project)
    assert out.read_bytes() == before


def test_output_locked_by_powerpoint_is_a_clear_error_and_keeps_the_old_file(project, monkeypatch):
    out = bd.build(project)
    before = out.read_bytes()
    real_replace = bd.os.replace

    def locked(src, dst):
        if str(dst) == str(out):      # 後処理の作業ファイルの置き換えは通す
            raise PermissionError("in use")
        real_replace(src, dst)

    monkeypatch.setattr(bd.os, "replace", locked)
    with pytest.raises(bd.BuildError, match="PowerPoint"):
        bd.build(project)
    assert out.read_bytes() == before
    assert not list(out.parent.glob("*.tmp"))


def test_unexpected_postprocess_error_becomes_a_build_error(project):
    (project / "videos.json").write_text('[{"unknown": 1}]', encoding="utf-8")
    with pytest.raises(bd.BuildError, match="後処理"):
        bd.build(project)


def test_two_outputs_are_tracked_separately(project, tmp_path):
    first, second = tmp_path / "a.pptx", tmp_path / "b.pptx"
    bd.build(project, first)
    bd.build(project, second)
    bd.build(project, first)                  # b を作った後でも a は手編集扱いにならない


def test_folder_outside_src_needs_an_explicit_output(tmp_path):
    project = tmp_path / "deck"
    _write(project, "01.svg", dc.header("題") + dc.footer(1, 1))
    with pytest.raises(bd.BuildError, match="-o"):
        bd.build(project)


def test_stale_work_file_is_not_reused(project, monkeypatch):
    (project / bd.WORK_NAME).write_bytes(b"stale")
    monkeypatch.setattr(bd, "convert", lambda project_, out: None)
    with pytest.raises(bd.BuildError):
        bd.build(project)
    assert not bd.default_output(project).exists()


def test_unwritable_state_does_not_report_a_delivered_deck_as_failed(project, monkeypatch, capsys):
    out = bd.default_output(project)
    real_write = bd.Path.write_text

    def refuse_state(self, *args, **kwargs):
        if self.name == bd.STATE_FILE:
            raise PermissionError("read only")
        return real_write(self, *args, **kwargs)

    monkeypatch.setattr(bd.Path, "write_text", refuse_state)
    assert bd.build(project) == out and out.exists()
    assert "--force" in capsys.readouterr().out


def test_corrupt_state_counts_as_unknown_and_protects_the_output(project):
    out = bd.build(project)
    (project / bd.STATE_FILE).write_text("{broken", encoding="utf-8")
    with pytest.raises(bd.BuildError, match="手で"):
        bd.build(project)
    assert out.exists()
