#!/usr/bin/env python3
"""デッキのフォルダから配布用の pptx を 1 コマンドで作る（raw-slides）。

手順は「検定 → 変換 → 後処理 → 出力検定 → 配布先へコピー」。どこかで落ちたら止まり、配布先には何も出さない。
手順を 1 か所に固定するのは、どの CLI で作っても同じ結果にするため（後処理の抜けはゲートでは気づけない）。

1. 検定: svg_quality_checker / assert_no_overlap / assert_font_rule / check_margins
2. 変換: SVG → native pptx（切り替え効果なし）。``notes/<SVG の名前>.md`` は各枚のノートに入る
3. 後処理: fix_ea_font → fix_scripts → add_videos（``videos.json`` があれば）→ ungroup_pptx
4. 出力検定: 切り替え効果 0・和文の run が MS Gothic・グループ 0（解けなかったものは報告）

手で直した pptx は作り直すと直しが消える。前回の書き出しと中身が違う出力は ``--force`` なしでは上書きしない。

デッキのフォルダ::

    work/presentations/slides/_src/<deck>/
        svg_output/*.svg     スライド（名前順が並び）
        images/              図。SVG からは ../images/<名前> で参照する
        notes/<SVG の名前>.md  発表原稿（任意）
        videos.json          動画の置き場所（任意）

Usage
-----
    python3 build_deck.py work/presentations/slides/_src/<deck> [-o out.pptx] [--force]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

import add_videos as videos_step
import fix_ea_font as ea_step
import fix_scripts as scripts_step
import ungroup_pptx as ungroup_step
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"
VENDOR = SKILL / "vendor"
STATE_FILE = ".last_build.json"
WORK_NAME = ".build.pptx"
JA_FONT = "MS Gothic"
BODY_MIN_SZ = 1400          # 本文の下限 14 pt（pptx の sz は 1/100 pt）
REQUIRED_MODULES = {"PIL": "Pillow", "lxml": "lxml"}   # Pillow が無いと画像の検定が黙って飛ぶ
CONVERT = ("import sys; sys.path.insert(0, sys.argv.pop(1)); "
           "from svg_to_pptx import main; raise SystemExit(main())")


class BuildError(Exception):
    """どこかの段で止まった。メッセージに直し方を書く。"""


def default_output(project: Path) -> Path:
    """``_src/<deck>`` の 2 つ上（配布先）に ``<deck>.pptx`` を置く。それ以外の場所は配布先が決まらないので止める。"""
    project = Path(project).resolve()
    if project.parent.name != "_src":
        raise BuildError(f"{project} は _src/<deck> の形でないので配布先が決まらない。-o で指定する")
    return project.parent.parent / f"{project.name}.pptx"


def sha256(path: Path) -> str:
    """ファイルの sha256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _child_env() -> dict[str, str]:
    """子プロセスの入出力を UTF-8 にする。Windows の既定（cp932）だと日本語や ≈ の出力で落ちる。"""
    return {**os.environ, "PYTHONUTF8": "1"}


def _read_state(project: Path) -> dict[str, str]:
    """出力先ごとの、前回の書き出しの sha256。"""
    state = project / STATE_FILE
    try:
        return json.loads(state.read_text(encoding="utf-8")) if state.exists() else {}
    except ValueError:      # 壊れた記録は「記録なし」として扱う（出力は手編集の可能性ありとして守られる）
        return {}


def _check_inputs(project: Path) -> Path:
    """デッキのフォルダと依存を確かめ、``svg_output`` を返す。"""
    svg_dir = project / "svg_output"
    if not any(svg_dir.glob("*.svg")):
        raise BuildError(f"{svg_dir} に SVG が無い。スライドは <deck>/svg_output/*.svg に置く")
    for module, package in REQUIRED_MODULES.items():
        if importlib.util.find_spec(module) is None:
            raise BuildError(f"{package} が無い。pip install {package}")
    return svg_dir


def _check_not_hand_edited(project: Path, output: Path) -> None:
    """前回の書き出しと違う出力を上書きしない。"""
    if not output.exists() or _read_state(project).get(str(output)) == sha256(output):
        return
    raise BuildError(f"{output} は前回の書き出しと中身が違う（手で直した可能性がある）。作り直すと直しが消える。"
                     "1 枚だけ替えるなら copy_slide_pptx を使う。捨ててよいなら --force")


def run_gates(project: Path, svg_dir: Path) -> None:
    """4 つの検定を流し、落ちたら名前と出力を添えて止める。"""
    gates = (
        ("svg_quality_checker", [VENDOR / "svg_quality_checker.py", project]),
        ("assert_no_overlap", [SCRIPTS / "assert_no_overlap.py", svg_dir]),
        ("assert_font_rule", [SCRIPTS / "assert_font_rule.py", svg_dir]),
        ("check_margins", [SCRIPTS / "check_margins.py", svg_dir]),
    )
    for name, args in gates:
        done = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=_child_env())
        if done.returncode != 0:
            raise BuildError(f"{name} に通らない:\n{done.stdout[-2000:]}{done.stderr[-1000:]}")


def convert(project: Path, out: Path) -> None:
    """SVG を native pptx に変換する。切り替え効果は明示的に切る（vendor の既定は fade）。"""
    done = subprocess.run([sys.executable, "-c", CONVERT, str(VENDOR), str(project), "--only", "native",
                           "--transition", "none", "-o", str(out), "-q"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", env=_child_env())
    if done.returncode != 0 or not out.exists():
        raise BuildError(f"変換に失敗した:\n{done.stdout[-2000:]}{done.stderr[-2000:]}")


def _runs(shapes):
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _runs(shape.shapes)
        elif shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                yield from para.runs


def verify_output(path: Path) -> list[str]:
    """書き出した pptx の問題の一覧を返す。空なら合格。"""
    problems = []
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        with_transition = [n for n in names if b"<p:transition" in z.read(n)]
    if with_transition:
        problems.append(f"切り替え効果が残っている: {len(with_transition)} 枚")
    prs = Presentation(str(path))
    bad_ea = 0
    for slide in prs.slides:
        for run in _runs(slide.shapes):
            if not ea_step.has_cjk(run.text):
                continue
            rpr = run._r.find(qn("a:rPr"))
            ea = None if rpr is None else rpr.find(qn("a:ea"))
            if ea is None or ea.get("typeface") != JA_FONT:
                bad_ea += 1
    if bad_ea:
        problems.append(f"和文の run が {JA_FONT} でない: {bad_ea} 個")
    return problems


def small_text_count(path: Path) -> dict[int, int]:
    """14 pt 未満の文字の run の数を枚ごとに返す（枚の番号は 1 から）。文献・注以外が混ざっていないかの確認用。"""
    counts: Counter[int] = Counter()
    for number, slide in enumerate(Presentation(str(path)).slides, start=1):
        for run in _runs(slide.shapes):
            size = run.font.size
            if size is not None and size.pt * 100 < BODY_MIN_SZ - 1 and run._r.rPr.get("baseline") is None and run.text.strip():
                counts[number] += 1
    return dict(counts)


def publish(project: Path, work: Path, output: Path) -> None:
    """配布先を一度に置き換え、状態を記録する。置き換えに失敗しても配布先は元のまま。"""
    tmp = output.with_name(output.name + ".tmp")
    state = _read_state(project)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work, tmp)
        os.replace(tmp, output)
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        raise BuildError(f"{output} に書けない。PowerPoint で開いていれば閉じる: {exc}") from exc
    try:
        (project / STATE_FILE).write_text(json.dumps({**state, str(output): sha256(output)}, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    except OSError as exc:  # 配布先は置き換え済みなので失敗にしない
        print(f"  [注意] 書き出しの記録を保存できなかった。次回は --force が要る: {exc}")


def build(project: str | Path, output: str | Path | None = None, *, force: bool = False) -> Path:
    """デッキを作って配布先へ置き、そのパスを返す。

    Parameters
    ----------
    project : str | Path
        デッキのフォルダ。
    output : str | Path | None
        配布先の pptx。省略時は ``default_output``。
    force : bool
        手で直された可能性のある出力も上書きする。

    Returns
    -------
    Path
        配布先の pptx。

    Raises
    ------
    BuildError
        検定・変換・後処理・出力検定のどこかで止まった。このとき配布先は変わらない。
    """
    project = Path(project).resolve()
    svg_dir = _check_inputs(project)
    output = Path(output).resolve() if output else default_output(project)
    if not force:
        _check_not_hand_edited(project, output)
    run_gates(project, svg_dir)
    work = project / WORK_NAME
    work.unlink(missing_ok=True)          # 中断した前回の残骸を後処理に回さない
    try:
        convert(project, work)
        ea_step.fix_ea_font(str(work))
        scripts_step.fix_scripts(work, svg_dir)
        videos_step.add_videos(work, project)
        report = ungroup_step.ungroup(work, work)
        problems = verify_output(work)
        if problems:
            raise BuildError("出力検定に通らない: " + " / ".join(problems))
        publish(project, work, output)
    except BuildError:
        raise
    except Exception as exc:              # 利用者に生のトレースバックを見せず、どこで止まったかを伝える
        raise BuildError(f"後処理で止まった: {type(exc).__name__}: {exc}") from exc
    finally:
        work.unlink(missing_ok=True)
    for number, group_id, reason in report["skipped"]:
        print(f"  [注意] {number} 枚目のグループ {group_id} は解かなかった: {reason}")
    small = small_text_count(output)
    if small:
        pages = ", ".join(f"{n} 枚目 {c} 個" for n, c in sorted(small.items()))
        print(f"  [確認] 14 pt 未満の文字: {pages}（文献・条件の注・ページ番号以外が混ざっていないか見る）")
    return output


def main(argv: list[str] | None = None) -> int:
    """CLI。"""
    parser = argparse.ArgumentParser(description="デッキのフォルダから配布用の pptx を作る")
    parser.add_argument("project", type=Path, help="デッキのフォルダ（svg_output/ を持つ）")
    parser.add_argument("-o", "--output", type=Path, help="配布先の pptx")
    parser.add_argument("--force", action="store_true", help="手で直された可能性のある出力も上書きする")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(errors="replace")
    try:
        out = build(args.project, args.output, force=args.force)
    except BuildError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
