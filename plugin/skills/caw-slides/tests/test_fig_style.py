"""fig_style のテスト: 図の 1 inch = スライドの 100 px、目盛りは内向き、和文フォントの探し方。"""
import pytest

matplotlib = pytest.importorskip("matplotlib")

import fig_style as fs  # noqa: E402


@pytest.fixture(autouse=True)
def _keep_rcparams():
    with matplotlib.rc_context():
        yield


def test_pt_converts_slide_px_to_points():
    assert fs.pt(100) == pytest.approx(72)


def test_figure_size_matches_the_box_in_px():
    fig = fs.figure(640, 360)
    assert tuple(fig.get_size_inches()) == pytest.approx((6.4, 3.6))
    matplotlib.pyplot.close(fig)


def test_ticks_point_inward_on_both_axes():
    fig = fs.figure(300, 200)
    ax = fig.add_subplot()
    fs.style_axes(ax)
    assert ax.xaxis.get_major_ticks()[0]._tickdir == "in"
    assert ax.yaxis.get_major_ticks()[0]._tickdir == "in"
    matplotlib.pyplot.close(fig)


def test_find_japanese_font_prefers_ms_gothic_file(tmp_path):
    ttc = tmp_path / "msgothic.ttc"
    ttc.write_bytes(b"x")
    assert fs.find_japanese_font([tmp_path / "missing.ttc", ttc]) == ttc


def test_find_japanese_font_returns_none_when_absent(tmp_path):
    assert fs.find_japanese_font([tmp_path / "missing.ttc"]) is None


def test_installed_ms_gothic_is_used_without_a_file_path(monkeypatch, capsys):
    monkeypatch.setattr(fs, "has_ms_gothic", lambda: True)
    monkeypatch.setattr(fs, "find_japanese_font", lambda paths=None: None)
    fs.setup()
    assert capsys.readouterr().err == ""


def test_setup_warns_when_substituting_a_font(monkeypatch, capsys):
    monkeypatch.setattr(fs, "has_ms_gothic", lambda: False)
    monkeypatch.setattr(fs, "find_japanese_font", lambda paths=None: None)
    fs.setup()
    assert "MS ゴシック" in capsys.readouterr().err           # 黙って置き換えない
