"""見本デッキの通し検定: 図・表・添字・ノート・動画を含むデッキが全段を通る。"""
import importlib.util
import shutil
from pathlib import Path

import build_deck as bd
import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

pytest.importorskip("matplotlib")
SAMPLE = Path(__file__).resolve().parent.parent / "references" / "sample_deck.py"


@pytest.fixture(scope="module")
def deck(tmp_path_factory):
    project = tmp_path_factory.mktemp("work") / "slides" / "_src" / "sample"
    spec = importlib.util.spec_from_file_location("sample_deck", SAMPLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main(project)
    return bd.build(project)


def test_all_pages_are_built(deck):
    assert len(Presentation(deck).slides) == 5


def test_figure_is_a_picture_and_the_table_is_native_text(deck):
    shapes = Presentation(deck).slides[2].shapes
    assert any(s.shape_type == MSO_SHAPE_TYPE.PICTURE for s in shapes)
    assert any(s.has_text_frame and "測定" in s.text_frame.text for s in shapes)


def test_notes_are_present(deck):
    assert "固相" in Presentation(deck).slides[1].notes_slide.notes_text_frame.text


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg なし")
def test_video_is_autoplay_loop(deck):
    slide = Presentation(deck).slides[3]
    assert slide.element.xpath(".//a:videoFile")
    timing = slide.element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}timing")
    assert timing is not None


def test_output_verifies_clean(deck):
    assert bd.verify_output(deck) == []
