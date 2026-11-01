#!/usr/bin/env python3
"""動画をスライド用に変換し、再生前に表示する 1 コマ目を書き出す（caw-slides）。

H.264・yuv420p・音声なし・BT.709 で変換してタグ 4 つを付ける。無指定だと BT.601 で変換され、PowerPoint が HD を
BT.709 で描くので色がずれる（鋭敏色板のマゼンタのような彩度の高い色で目立つ）。

Usage
-----
    python3 prepare_video.py in.mp4 images/melt.mp4 --poster images/melt.png --start 12 --duration 40 --speed 4
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

CRF = 20          # 画質（小さいほど高画質）。10 秒ほどのループなら数 MB に収まる


def video_filter(*, speed: float | None, crop: str | None, width: int | None) -> str:
    """ffmpeg の ``-vf`` の文字列を組み立てる。

    Parameters
    ----------
    speed : float | None
        再生速度の倍率。
    crop : str | None
        切り抜き ``w:h:x:y`` [px]。
    width : int | None
        出力の幅 [px]。高さは縦横比を保つ。

    Returns
    -------
    str
        フィルタの文字列。色の変換は必ず最後に置く。

    Raises
    ------
    ValueError
        ``speed`` が正でない。
    """
    if speed is not None and speed <= 0:
        raise ValueError(f"speed は正の数: {speed}")
    steps = []
    if crop:
        steps.append(f"crop={crop}")
    if speed and speed != 1:
        steps.append(f"setpts=PTS/{speed:g}")
    if width:
        steps.append(f"scale={width}:-2")
    steps.append("scale=out_color_matrix=bt709:out_range=tv,format=yuv420p")
    return ",".join(steps)


def ffmpeg_command(src: str | Path, out: str | Path, *, start: float | None = None, duration: float | None = None,
                   speed: float | None = None, crop: str | None = None, width: int | None = None) -> list[str]:
    """変換の ffmpeg コマンドを返す。``start`` / ``duration`` は元の動画の秒。"""
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if start is not None:
        cmd += ["-ss", f"{start:g}"]
    if duration is not None:
        cmd += ["-t", f"{duration:g}"]
    cmd += ["-i", str(src), "-vf", video_filter(speed=speed, crop=crop, width=width),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
            "-c:v", "libx264", "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709",
            "-crf", str(CRF), "-preset", "slow", "-movflags", "+faststart", "-an", str(out)]
    return cmd


def prepare(src: str | Path, out: str | Path, *, poster: str | Path | None = None, **options: object) -> None:
    """動画を変換し、``poster`` があれば 1 コマ目を画像にする。"""
    if shutil.which("ffmpeg") is None:
        raise ValueError("ffmpeg が見つからない。動画を扱うには ffmpeg を導入する")
    subprocess.run(ffmpeg_command(src, out, **options), check=True)
    if poster is not None:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-frames:v", "1", str(poster)], check=True)


def main(argv: list[str] | None = None) -> int:
    """CLI。"""
    parser = argparse.ArgumentParser(description="動画をスライド用に変換する")
    parser.add_argument("src", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--poster", type=Path, help="1 コマ目の画像の書き出し先")
    parser.add_argument("--start", type=float, help="元の動画の開始 [s]")
    parser.add_argument("--duration", type=float, help="元の動画から使う長さ [s]")
    parser.add_argument("--speed", type=float, help="再生速度の倍率")
    parser.add_argument("--crop", help="切り抜き w:h:x:y [px]")
    parser.add_argument("--width", type=int, help="出力の幅 [px]")
    args = parser.parse_args(argv)
    if not args.src.exists():
        print(f"[ERROR] {args.src} が無い", file=sys.stderr)
        return 1
    try:
        prepare(args.src, args.out, poster=args.poster, start=args.start, duration=args.duration, speed=args.speed,
                crop=args.crop, width=args.width)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"  {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
