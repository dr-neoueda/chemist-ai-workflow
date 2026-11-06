"""prepare_video のテスト: H.264・yuv420p・音声なし・BT.709 のタグ 4 つ。"""
import shutil
import subprocess

import prepare_video as pv
import pytest


def test_command_tags_bt709_and_strips_audio():
    cmd = pv.ffmpeg_command("in.mp4", "out.mp4")
    joined = " ".join(cmd)
    for flag in ("-colorspace bt709", "-color_primaries bt709", "-color_trc bt709", "-color_range tv", "-an",
                 "-c:v libx264", "+faststart"):
        assert flag in joined
    assert "format=yuv420p" in joined


def test_speed_and_crop_go_into_the_filter_before_the_format():
    vf = pv.video_filter(speed=4, crop="960:960:100:0", width=None)
    assert vf.index("crop=960:960:100:0") < vf.index("setpts=PTS/4") < vf.index("format=yuv420p")


def test_speed_must_be_positive():
    with pytest.raises(ValueError):
        pv.video_filter(speed=0, crop=None, width=None)


@pytest.mark.skipif(shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None, reason="ffmpeg なし")
def test_real_conversion_tags_the_stream_and_writes_a_poster(tmp_path):
    src = tmp_path / "in.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=d=1:s=320x240:r=10", "-c:v", "libx264",
                    str(src)], check=True)
    out, poster = tmp_path / "out.mp4", tmp_path / "out.png"
    pv.prepare(src, out, poster=poster)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=pix_fmt,color_space,color_primaries,color_transfer,color_range",
                            "-of", "default=nw=1:nk=1", str(out)], capture_output=True, text=True, check=True).stdout
    assert probe.split() == ["yuv420p", "tv", "bt709", "bt709", "bt709"]
    assert poster.stat().st_size > 0
