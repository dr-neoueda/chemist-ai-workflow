#!/usr/bin/env python3
"""caw-slides の見本デッキの生成器。新しいデッキはこの形を手本に書く（架空の例でデータも架空）。

    python3 sample_deck.py <デッキのフォルダ>     # svg_output/・images/・notes/ を作る
    python3 ../scripts/build_deck.py <デッキのフォルダ>

書き方の要点:
- 値は DATA の 1 か所に置き、図・表・本文が同じ値を読む（手で写さない）
- 数値で形が決まる図は matplotlib、模式図と表は SVG の図形と文字
- 並びは PAGES の 1 か所で決める。番号はそこから引く（手で振らない）
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import deck_chrome as dc  # noqa: E402
import deck_parts as dp  # noqa: E402

R = 8.314e-3  # kJ/(mol K)
EA = 120.0    # kJ/mol（架空）
LN_A = 26.4   # ln(A / s^-1)（架空）
DATA = [(393, 350.0), (413, 61.0), (433, 12.0)]  # (温度 K, 半減期 min)（架空）


def rate_per_s(temperature: float) -> float:
    """Arrhenius 式の速度定数 [1/s]。"""
    return math.exp(LN_A - EA / (R * temperature))


def half_life_min(temperature: float) -> float:
    """Arrhenius 式の半減期 [min]。"""
    return math.log(2) / rate_per_s(temperature) / 60


def fig_arrhenius(out: Path) -> Path:
    """アレニウスプロット。大きさはスライドに貼る箱の px と同じ。"""
    import fig_style as fs

    fs.setup()
    fig = fs.figure(520, 340)
    ax = fig.add_axes((0.17, 0.17, 0.78, 0.78))
    x = [1000 / t for t, _ in DATA]
    y = [math.log(math.log(2) / (h * 60)) for _, h in DATA]
    ax.plot(x, y, "o", color=dc.BLUE)
    ends = (DATA[0][0], DATA[-1][0])
    ax.plot([1000 / t for t in ends], [math.log(rate_per_s(t)) for t in ends], color=dc.NAVY, linewidth=1.2)
    ax.set_xlabel("1000 / T (K$^{-1}$)", fontsize=fs.pt(14))
    ax.set_ylabel("ln(k / s$^{-1}$)", fontsize=fs.pt(14))
    fs.style_axes(ax)
    return fs.save(fig, out)


def s_cover(n: int, total: int, images: Path) -> str:
    return dc.cover(["結晶中の転位反応の速度論", "（見本デッキ）"], authors="○著者 太郎^{1}・共著 花子^{2}",
                    affiliation="^{1}所属大学院　^{2}共同研究機関", venue="架空の例・データも架空")


def s_background(n: int, total: int, images: Path) -> str:
    return (dc.header("背景") + dc.column_head(80, 186, "固相反応の特徴")
            + dc.bullet(80, 226, "分子の動きが結晶格子に制限される")
            + dc.bullet(80, 264, "生成物が格子をひずませ、近傍の反応性を変える")
            + dc.bullet(80, 302, "赤外吸収 1705 cm^{-1} の減衰で反応率を追跡する")
            + dc.column_head(660, 186, "本研究の問い", colour=dc.GOLD)
            + dc.bullet(660, 226, "律速段階は何に由来するか", colour=dc.GOLD)
            + dc.callout(80, 360, 1120, 60, ["反応は格子のひずみを介して隣へ伝わる"]) + dc.footer(n, total))


def s_rate(n: int, total: int, images: Path) -> str:
    rows = [[f"{t} K", f"{h:g} min", f"{half_life_min(t):.3g} min"] for t, h in DATA]
    box, _, _ = dp.figure(images / "fig_arrhenius.png", 660, 170, w=540)
    return (dc.header("活性化エネルギー") + dp.table(80, 170, [0, 170, 340], ["温度", "測定", "計算"], rows, width=520, highlight=2)
            + box + dc.text(80, 420, f"Ea = {EA:g} kJ/mol（Arrhenius 式）", bold=True, fill=dc.NAVY)
            + dc.text(80, 640, "測定条件: 窒素気流下・昇温なし（架空）", size=13, fill=dc.GREY, fine=True) + dc.footer(n, total))


def s_video(n: int, total: int, images: Path) -> str:
    return (dc.header("加熱中の観察") + dp.frame(80, 170, 480, 270)
            + dc.bullet(600, 206, "スライドを開くと自動で再生・ループする")
            + dc.bullet(600, 244, "枠は SVG、動画は videos.json が置く") + dc.footer(n, total))


def s_summary(n: int, total: int, images: Path) -> str:
    return (dc.header("まとめ") + dp.badge(96, 196, "1") + dc.text(126, 203, "固相反応の半減期を 3 温度で決定した")
            + dp.badge(96, 248, "2") + dc.text(126, 255, f"活性化エネルギーは {EA:g} kJ/mol")
            + dc.callout(80, 310, 1120, 96, ["近傍の反応率への依存を測定する"], title="今後の課題", edge=dc.GREEN)
            + dc.footer(n, total))


PAGES = [("01_cover", s_cover), ("02_background", s_background), ("03_rate", s_rate), ("04_video", s_video),
         ("05_summary", s_summary)]
NOTES = {"02_background": "固相では分子の動きが制限される点から話し始める。"}


def write_video(images: Path) -> bool:
    """見本の動画を ffmpeg で作る。ffmpeg が無ければ動画なしで進める。"""
    if shutil.which("ffmpeg") is None:
        return False
    import prepare_video as pv

    raw = images / "raw.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=d=2:s=480x270:r=15", "-c:v", "libx264",
                    str(raw)], check=True)
    pv.prepare(raw, images / "clip.mp4", poster=images / "clip.png")
    raw.unlink()
    return True


def main(project: Path) -> None:
    """デッキのフォルダへ SVG・図・ノートを書く。"""
    images, out, notes = project / "images", project / "svg_output", project / "notes"
    for folder in (images, out, notes):
        folder.mkdir(parents=True, exist_ok=True)
    fig_arrhenius(images / "fig_arrhenius.png")
    for k, (name, page) in enumerate(PAGES, start=1):
        (out / f"{name}.svg").write_text(dc.svg(page(k, len(PAGES), images)), encoding="utf-8")
    for name, body in NOTES.items():
        (notes / f"{name}.md").write_text(body, encoding="utf-8")
    if write_video(images):
        spec = [{"slide": "04_video", "mp4": "clip.mp4", "poster": "clip.png", "x": 81, "y": 171, "w": 478, "h": 268}]
        (project / "videos.json").write_text(json.dumps(spec), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
