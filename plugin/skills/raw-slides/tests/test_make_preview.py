"""make_preview のテスト: プレビューの画素サイズを検定し、ブラウザが無ければ止まる。"""
import make_preview as mp
import pytest
from PIL import Image


def test_wrong_size_preview_is_rejected(tmp_path):
    png = tmp_path / "x.png"
    Image.new("RGB", (1600, 1600)).save(png)
    with pytest.raises(mp.PreviewError, match="1280"):
        mp.check_size(png)


def test_right_size_preview_passes(tmp_path):
    png = tmp_path / "x.png"
    Image.new("RGB", (1280, 720)).save(png)
    mp.check_size(png)


def test_find_browser_uses_the_first_existing_candidate(tmp_path):
    exe = tmp_path / "chrome"
    exe.write_text("")
    assert mp.find_browser([tmp_path / "none", exe], names=[]) == str(exe)


def test_missing_browser_is_a_clear_error(tmp_path):
    with pytest.raises(mp.PreviewError, match="Chrome"):
        mp.find_browser([tmp_path / "none"], names=[])


def test_stale_png_is_not_accepted_when_the_browser_writes_nothing(tmp_path, monkeypatch):
    svg, png = tmp_path / "x.svg", tmp_path / "x.png"
    svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
    Image.new("RGB", (1280, 720)).save(png)
    monkeypatch.setattr(mp.subprocess, "run", lambda *a, **k: mp.subprocess.CompletedProcess(a, 0, b"", b""))
    with pytest.raises(mp.PreviewError, match="書かれなかった"):
        mp.render("browser", svg, png)


def test_real_render_is_1280x720(tmp_path):
    try:
        browser = mp.find_browser()
    except mp.PreviewError:
        pytest.skip("ブラウザなし")
    svg = tmp_path / "日本語 名.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">'
                   '<rect x="0" y="0" width="100" height="100" fill="#16283D"/></svg>', encoding="utf-8")
    mp.render(browser, svg, tmp_path / "out.png")
    assert (tmp_path / "out.png").exists()
