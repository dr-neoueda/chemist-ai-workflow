#!/usr/bin/env python3
"""pptx のグループ（p:grpSp）をすべて解き、中の図形をスライドの直下に出す（raw-slides）。

変換器は SVG の ``<g>`` をグループにして書き出す。グループのままだと PowerPoint で図形を個別に編集しにくいので、
書き出しの最後（fix_ea_font・add_videos の後）にこれをかける。

やること: グループの xfrm（off・ext・chOff・chExt）で子の位置と大きさを親の座標に直し（拡大縮小つき）、子をグループのあった位置
（重なりの順）にそのまま差し込んでグループを消す。入れ子も外側から順にすべて解く。
解かないもの: 回転・反転のあるグループ、xfrm の無い子を持つ拡大縮小つきのグループ、アニメーション（p:timing）が
グループの id を指しているもの（解くとアニメーションが壊れる）。解かなかったものは結果に名前を出す。

実行: ``python ungroup_pptx.py in.pptx [-o out.pptx]``（-o が無ければ上書き）
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

SHAPE_TAGS = {qn("p:sp"), qn("p:pic"), qn("p:cxnSp"), qn("p:graphicFrame"), qn("p:grpSp"), qn("p:contentPart")}


def _xfrm(el):
    """図形の位置と大きさの要素（a:xfrm、表などは p:xfrm）。無ければ None。"""
    if el.tag == qn("p:grpSp"):
        return el.find(qn("p:grpSpPr")).find(qn("a:xfrm"))
    if el.tag == qn("p:graphicFrame"):
        return el.find(qn("p:xfrm"))
    sppr = el.find(qn("p:spPr"))
    return None if sppr is None else sppr.find(qn("a:xfrm"))


def _pair(node, a: str, b: str) -> tuple[int, int]:
    return int(node.get(a)), int(node.get(b))


def _group_id(grp) -> str:
    return grp.find(qn("p:nvGrpSpPr")).find(qn("p:cNvPr")).get("id")


def _flatten_one(grp, animated_ids: set[str]) -> str | None:
    """グループ 1 つを解く。解いたら None、解かなかったら理由。"""
    xfrm = grp.find(qn("p:grpSpPr")).find(qn("a:xfrm"))
    if _group_id(grp) in animated_ids:
        return "アニメーションがグループを指す"
    children = [c for c in grp if c.tag in SHAPE_TAGS]
    if xfrm is not None:
        if int(xfrm.get("rot", "0")) or xfrm.get("flipH") in ("1", "true") or xfrm.get("flipV") in ("1", "true"):
            return "回転・反転のあるグループ"
        ox, oy = _pair(xfrm.find(qn("a:off")), "x", "y")
        ex, ey = _pair(xfrm.find(qn("a:ext")), "cx", "cy")
        cx0, cy0 = _pair(xfrm.find(qn("a:chOff")), "x", "y")
        cex, cey = _pair(xfrm.find(qn("a:chExt")), "cx", "cy")
        sx, sy = (ex / cex if cex else 1.0), (ey / cey if cey else 1.0)
        identity = (ox, oy, sx, sy) == (cx0, cy0, 1.0, 1.0)
        if not identity:
            if any(_xfrm(c) is None for c in children):
                return "位置の無い子を持つ拡大縮小つきのグループ"
            for c in children:
                cx = _xfrm(c)
                off, ext = cx.find(qn("a:off")), cx.find(qn("a:ext"))
                x, y = _pair(off, "x", "y")
                w, h = _pair(ext, "cx", "cy")
                off.set("x", str(round(ox + (x - cx0) * sx)))
                off.set("y", str(round(oy + (y - cy0) * sy)))
                ext.set("cx", str(round(w * sx)))
                ext.set("cy", str(round(h * sy)))
    parent = grp.getparent()
    i = parent.index(grp)
    for k, c in enumerate(children):
        parent.insert(i + k, c)
    parent.remove(grp)
    return None


def ungroup(src: Path, dst: Path) -> dict:
    """``src`` のすべてのスライドのグループを解いて ``dst`` に保存する。

    Returns
    -------
    dict
        groups_removed（解いた数）、skipped（[スライドの番号, グループの id, 理由]）。

    Raises
    ------
    FileNotFoundError
        ``src`` が無い。
    """
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(src)
    prs = Presentation(str(src))
    removed, skipped = 0, []
    for n, slide in enumerate(prs.slides, start=1):
        root = slide._element
        animated = {t.get("spid") for t in root.iter(qn("p:spTgt"))}
        tree = slide.shapes._spTree
        kept: list = []          # 要素そのものを持つ。id() は lxml のプロキシが消えると変わるので比較に使えない
        while True:
            groups = [g for g in tree.iter(qn("p:grpSp")) if not any(g is k for k in kept)]
            if not groups:
                break
            grp = groups[0]
            reason = _flatten_one(grp, animated)
            if reason is None:
                removed += 1
            else:
                kept.append(grp)
                skipped.append([n, _group_id(grp), reason])
    dst = Path(dst)
    tmp = dst.with_name(f".{dst.name}.tmp")   # 手で直した pptx にもかけるので、書き込みに失敗しても元を壊さない
    try:
        prs.save(str(tmp))
        os.replace(tmp, dst)
    finally:
        tmp.unlink(missing_ok=True)
    return {"groups_removed": removed, "skipped": skipped}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("pptx", type=Path)
    p.add_argument("-o", "--out", type=Path, help="書き出し先（無ければ上書き）")
    a = p.parse_args()
    report = ungroup(a.pptx, a.out or a.pptx)
    print(f"グループを解いた数 {report['groups_removed']}、解かなかった {len(report['skipped'])}: {report['skipped']}")


if __name__ == "__main__":
    main()
