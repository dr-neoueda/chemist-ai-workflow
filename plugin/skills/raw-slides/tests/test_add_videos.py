"""add_videos のテスト: 自動再生・ループの p:timing と、二重貼りの拒否。"""
import json

import add_videos as av
import pytest
from lxml import etree
from PIL import Image
from pptx import Presentation

P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"


def test_timing_plays_on_open_and_loops():
    root = etree.fromstring(av.timing_xml([(11, 10000)]))
    assert root.find(f".//{P}cmd").get("cmd") == "playFrom(0.0)"
    assert root.find(f".//{P}video/{P}cMediaNode/{P}cTn").get("repeatCount") == "indefinite"


def test_second_video_on_a_slide_starts_with_the_first_and_ids_are_unique():
    root = etree.fromstring(av.timing_xml([(11, 10000), (12, 8000)]))
    nodes = [c.get("nodeType") for c in root.iter(f"{P}cTn") if c.get("presetClass") == "mediacall"]
    assert nodes == ["afterEffect", "withEffect"]
    ids = [c.get("id") for c in root.iter(f"{P}cTn")]
    assert len(ids) == len(set(ids))


@pytest.fixture
def project(tmp_path):
    prs = Presentation()
    prs.slides.add_slide(prs.slide_layouts[6])
    prs.slides.add_slide(prs.slide_layouts[6])
    deck = tmp_path / "deck.pptx"
    prs.save(deck)
    (tmp_path / "svg_output").mkdir()
    (tmp_path / "svg_output" / "01_a.svg").write_text("<svg/>")
    (tmp_path / "svg_output" / "02_b.svg").write_text("<svg/>")
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "v.mp4").write_bytes(b"\x00" * 64)
    Image.new("RGB", (16, 9)).save(tmp_path / "images" / "p.png")
    spec = [{"slide": "02_b", "mp4": "v.mp4", "poster": "p.png", "x": 80, "y": 180, "w": 320, "h": 180}]
    (tmp_path / "videos.json").write_text(json.dumps(spec), encoding="utf-8")
    return tmp_path, deck


def test_video_lands_on_the_named_slide_at_the_px_position(project, monkeypatch):
    root, deck = project
    monkeypatch.setattr(av, "duration_ms", lambda path: 10000)
    assert av.add_videos(deck, root) == 1
    slide = Presentation(deck).slides[1]
    movie = slide.shapes[-1]
    assert (movie.left, movie.width) == (80 * 9525, 320 * 9525)
    assert slide.element.find(f"{P}timing") is not None


def test_running_twice_is_refused(project, monkeypatch):
    root, deck = project
    monkeypatch.setattr(av, "duration_ms", lambda path: 10000)
    av.add_videos(deck, root)
    with pytest.raises(ValueError, match="動画"):
        av.add_videos(deck, root)


def test_unknown_slide_name_is_an_error(project, monkeypatch):
    root, deck = project
    monkeypatch.setattr(av, "duration_ms", lambda path: 10000)
    (root / "videos.json").write_text(json.dumps([{"slide": "99_x", "mp4": "v.mp4", "poster": "p.png",
                                                   "x": 0, "y": 0, "w": 1, "h": 1}]), encoding="utf-8")
    with pytest.raises(ValueError, match="99_x"):
        av.add_videos(deck, root)


def test_missing_spec_means_no_videos(project):
    root, deck = project
    (root / "videos.json").unlink()
    assert av.add_videos(deck, root) == 0


def test_two_videos_share_one_timing_that_targets_both_movies(project, monkeypatch):
    root, deck = project
    monkeypatch.setattr(av, "duration_ms", lambda path: 10000)
    spec = [{"slide": "02_b", "mp4": "v.mp4", "poster": "p.png", "x": 80, "y": 180, "w": 320, "h": 180},
            {"slide": "02_b", "mp4": "v.mp4", "poster": "p.png", "x": 500, "y": 180, "w": 320, "h": 180}]
    (root / "videos.json").write_text(json.dumps(spec), encoding="utf-8")
    av.add_videos(deck, root)
    slide = Presentation(deck).slides[1]
    assert len(slide.element.findall(f"{P}timing")) == 1
    movies = {str(s.shape_id) for s in slide.shapes if s.shape_type is not None and "MEDIA" in str(s.shape_type)}
    targets = {t.get("spid") for t in slide.element.iter(f"{P}spTgt")}
    assert len(movies) == 2 and targets == movies


def test_ffprobe_failure_names_the_file(tmp_path):
    if av.shutil.which("ffprobe") is None:
        pytest.skip("ffprobe なし")
    bad = tmp_path / "broken.mp4"
    bad.write_bytes(b"not a video")
    with pytest.raises(ValueError, match="broken.mp4"):
        av.duration_ms(bad)
