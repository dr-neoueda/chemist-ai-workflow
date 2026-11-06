#!/usr/bin/env python3
"""書き出した pptx に動画を埋め込み、スライドを開いたら自動で再生・ループするようにする（caw-slides）。

変換器は動画を扱わないので、SVG には枠と説明だけを描き、ここで ``videos.json`` の位置に置く。

python-pptx は「クリックで再生」のタイミングしか書かないので、スライドの ``p:timing`` を PowerPoint が
「開始: 自動」「停止するまで繰り返す」で保存するときと同じ構造に置き換える。
- 主シーケンスに mediacall（``playFrom(0.0)``）を ``onBegin`` ＋ afterEffect で置く（スライドを開くと再生）
- ``p:video/p:cMediaNode/p:cTn`` に ``repeatCount="indefinite"``（ループ）

``videos.json``（デッキのフォルダ直下。座標はスライド上の px）::

    [{"slide": "04_micro", "mp4": "melt.mp4", "poster": "melt.png", "x": 80, "y": 180, "w": 370, "h": 347}]

``slide`` は SVG の名前（拡張子なし）。``mp4`` と ``poster`` は ``images/`` の中のファイル名。

Usage
-----
    python3 add_videos.py <deck.pptx> <デッキのフォルダ>
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.util import Emu

EMU_PER_PX = 9525                  # 1280 px = 12,192,000 EMU
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

HEAD = ('<p:timing xmlns:p="{p}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        '<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
        '</p:stCondLst><p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>')
CALL = ('<p:par><p:cTn id="{id1}" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="{node}">'
        '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr>'
        '<p:cTn id="{id2}" dur="{dur_ms}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd></p:childTnLst>'
        '</p:cTn></p:par>')
MID = ('</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
       '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
       '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>')
VIDEO = ('<p:video><p:cMediaNode vol="80000"><p:cTn id="{id1}" repeatCount="indefinite" fill="hold" display="0">'
         '<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
         '</p:cMediaNode></p:video>')
TAIL = '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'


@dataclass(frozen=True)
class Video:
    """動画 1 本。座標はスライド上の最終位置 [px]。"""
    slide: str
    mp4: str
    poster: str
    x: float
    y: float
    w: float
    h: float


def timing_xml(items: list[tuple[int, int]]) -> str:
    """スライドを開くと同じ枚の動画をすべて同時に再生し、ループさせる ``p:timing``。

    1 本目は afterEffect、2 本目以降は withEffect（同時に始まる）。``cTn`` の id は通し番号で重複させない。

    Parameters
    ----------
    items : list[tuple[int, int]]
        (図形の id, 長さ [ms]) の列。

    Returns
    -------
    str
        ``p:timing`` の XML。
    """
    out, next_id = [HEAD.format(p=NS["p"])], 5
    for k, (spid, dur) in enumerate(items):
        out.append(CALL.format(id1=next_id, id2=next_id + 1, dur_ms=dur, spid=spid,
                               node="afterEffect" if k == 0 else "withEffect"))
        next_id += 2
    out.append(MID)
    for spid, _ in items:
        out.append(VIDEO.format(id1=next_id, spid=spid))
        next_id += 1
    out.append(TAIL)
    return "".join(out)


def duration_ms(mp4: Path) -> int:
    """動画の長さ [ms] を ffprobe で測る。"""
    if shutil.which("ffprobe") is None:
        raise ValueError("ffprobe が見つからない。動画を貼るには ffmpeg を導入する")
    done = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return round(float(done.stdout) * 1000)
    except ValueError as exc:
        raise ValueError(f"{mp4} の長さが読めない: {done.stderr[-300:]}") from exc


def load_videos(project: Path) -> list[Video]:
    """``videos.json`` を読む。無ければ空。"""
    spec = project / "videos.json"
    if not spec.exists():
        return []
    return [Video(**item) for item in json.loads(spec.read_text(encoding="utf-8"))]


def _add_slide_videos(slide, images: Path, videos: list[Video], name: str) -> None:
    """同じ枚の動画をまとめて置き、1 つの ``p:timing`` で自動再生・ループにする。"""
    if slide.element.xpath(".//a:videoFile"):
        raise ValueError(f"{name}: すでに動画がある（1 回の書き出しに 1 度だけかける）")
    if slide.element.find("p:timing", NS) is not None:
        raise ValueError(f"{name}: 独自のアニメーションがあるので上書きしない")
    items = []
    for video in videos:
        mp4, poster = images / video.mp4, images / video.poster
        movie = slide.shapes.add_movie(str(mp4), Emu(round(video.x * EMU_PER_PX)), Emu(round(video.y * EMU_PER_PX)),
                                       Emu(round(video.w * EMU_PER_PX)), Emu(round(video.h * EMU_PER_PX)),
                                       poster_frame_image=str(poster), mime_type="video/mp4")
        items.append((movie.shape_id, duration_ms(mp4)))
        click_timing = slide.element.find("p:timing", NS)              # python-pptx の「クリックで再生」
        if click_timing is not None:
            slide.element.remove(click_timing)
    slide.element._insert_timing(etree.fromstring(timing_xml(items)))


def add_videos(pptx_path: str | Path, project: str | Path) -> int:
    """``videos.json`` の動画を pptx に貼り、貼った本数を返す。

    Parameters
    ----------
    pptx_path : str | Path
        書き出した pptx。上書きする。
    project : str | Path
        デッキのフォルダ（``svg_output/``・``images/``・``videos.json`` を持つ）。

    Returns
    -------
    int
        貼った本数。``videos.json`` が無ければ 0 で pptx に触らない。

    Raises
    ------
    ValueError
        枚の名前が無い、すでに動画がある、独自のアニメーションがある。
    """
    project = Path(project)
    videos = load_videos(project)
    if not videos:
        return 0
    order = [svg.stem for svg in sorted((project / "svg_output").glob("*.svg"))]
    prs = Presentation(str(pptx_path))
    if len(order) != len(prs.slides):
        raise ValueError(f"SVG {len(order)} 枚に対して pptx は {len(prs.slides)} 枚")
    by_slide: dict[str, list[Video]] = {}
    for video in videos:
        if video.slide not in order:
            raise ValueError(f"videos.json の {video.slide} に当たる SVG が無い")
        by_slide[video.slide] = [*by_slide.get(video.slide, []), video]
    for name, items in by_slide.items():
        _add_slide_videos(prs.slides[order.index(name)], project / "images", items, name)
    prs.save(str(pptx_path))
    return len(videos)


def main(argv: list[str] | None = None) -> int:
    """CLI。"""
    parser = argparse.ArgumentParser(description="pptx に自動再生・ループの動画を貼る")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("project", type=Path)
    args = parser.parse_args(argv)
    try:
        count = add_videos(args.pptx, args.project)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"  動画: {count} 本を貼った")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
