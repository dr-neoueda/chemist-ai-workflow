#!/usr/bin/env python3
"""手で直された pptx を壊さずに足す・差し替えるための道具（caw-slides）。

手で直された配布版は生成器から作り直せない（作り直すと直しが消える）。生成器で作った 1 枚を写す・画像を差し替える・
ノートを書き換える、を配布版の上で直接行う。Python から import して使う。

- copy_slide: 1 枚を別の pptx の末尾へ写す。図形は XML をそのまま写し、画像は中身を相手の pptx に入れ直して参照を付け替える。
  画像以外の関係（ハイパーリンク・動画・グラフなど）を持つ枚は写さない（参照が壊れるので ValueError）。図形の id は振り直す。
- replace_picture: 位置と大きさ（EMU）が一致する画像 1 つの中身だけを差し替える（位置・大きさ・名前・アニメーションはそのまま）。
- replace_slide: 手の入っていない 1 枚を、生成器の新しい版で同じ位置ごと入れ替える。
- copy_shapes・move_shapes: 手の入った枚に部品（表など）だけを足す・場所を空けるために図形をずらす。
- set_notes・prepend_notes_line: ノートの文を置き換える・先頭に足す。
"""
from __future__ import annotations

import copy
import io

from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

R_ATTRS = (qn("r:embed"), qn("r:id"), qn("r:link"), qn("r:pict"))
P14_SLD_ID = "{http://schemas.microsoft.com/office/powerpoint/2010/main}sldId"   # 節（sections）の中の枚
GEOMETRY_TOLERANCE_EMU = 9525           # 1 px


def _relationship_refs(el) -> list[tuple[object, str]]:
    return [(node, attr) for node in el.iter() for attr in R_ATTRS if node.get(attr) is not None]


def _shape_elements(slide) -> list:
    tree = slide.shapes._spTree
    return [c for c in tree if c.tag not in (qn("p:nvGrpSpPr"), qn("p:grpSpPr"))]


def _next_id(slide) -> int:
    ids = [int(n.get("id")) for n in slide.shapes._spTree.iter(qn("p:cNvPr"))]
    return max(ids, default=1) + 1


def copy_slide(src_slide, dst_prs, layout=None):
    """``src_slide`` を ``dst_prs`` の末尾へ写して、新しい枚を返す。``layout`` が無ければ相手の最後の枚の配置を使う。"""
    bg = src_slide._element.cSld.find(qn("p:bg"))
    elements = _shape_elements(src_slide)
    _check_relationships(elements if bg is None else [bg, *elements])
    layout = layout or dst_prs.slides[-1].slide_layout
    new = dst_prs.slides.add_slide(layout)
    for ph in list(new.placeholders):
        ph._element.getparent().remove(ph._element)
    if bg is not None:
        dup = copy.deepcopy(bg)
        _rebind_images(dup, src_slide, new)
        new._element.cSld.insert(0, dup)
    _append_copies(elements, src_slide, new)
    return new


def _check_relationships(elements: list) -> None:
    for el in elements:
        for node, attr in _relationship_refs(el):
            if not (node.tag == qn("a:blip") and attr == qn("r:embed")):
                raise ValueError(f"画像以外の関係（{attr}）を持つ図形は写せない: {el.tag}")


def _rebind_images(el, src_slide, dst_slide) -> None:
    """``el`` の画像の中身を ``dst_slide`` に入れ直し、参照を付け替える。"""
    for blip in el.iter(qn("a:blip")):
        if blip.get(qn("r:embed")) is None:
            continue
        blob = src_slide.part.related_part(blip.get(qn("r:embed"))).blob
        _, rid = dst_slide.part.get_or_add_image_part(io.BytesIO(blob))
        blip.set(qn("r:embed"), rid)


def _remap_connections(el, new_ids: dict[str, str]) -> None:
    """結線の相手を振り直した id へ付け替える。相手が写らなかった端は結線を外す（別の図形へつながらないように）。"""
    for tag in ("a:stCxn", "a:endCxn"):
        for cxn in list(el.iter(qn(tag))):
            target = new_ids.get(cxn.get("id"))
            if target is None:
                cxn.getparent().remove(cxn)
            else:
                cxn.set("id", target)


def _append_copies(elements: list, src_slide, dst_slide) -> int:
    """図形の XML を写して ``dst_slide`` の最前面に足す（画像は中身を入れ直し、id は振り直す）。足した数を返す。"""
    next_id = _next_id(dst_slide)
    copies = [copy.deepcopy(el) for el in elements]
    new_ids: dict[str, str] = {}
    for dup in copies:
        _rebind_images(dup, src_slide, dst_slide)
        for c in dup.iter(qn("p:cNvPr")):
            new_ids[c.get("id")] = str(next_id)
            c.set("id", str(next_id))
            next_id += 1
    for dup in copies:
        _remap_connections(dup, new_ids)
        dst_slide.shapes._spTree.append(dup)
    return len(elements)


def copy_shapes(src_slide, dst_slide, keep=lambda shape: True) -> int:
    """``src_slide`` の図形のうち ``keep(shape)`` が真のものを、既存の ``dst_slide`` に写す（位置はそのまま）。写した数を返す。

    手の入った枚に、生成器で作った部品（表など）だけを足すとき用。
    """
    elements = [s._element for s in src_slide.shapes if keep(s)]
    _check_relationships(elements)
    return _append_copies(elements, src_slide, dst_slide)


def move_shapes(slide, select, dy_emu: int) -> int:
    """``select(shape)`` が真の図形を縦に ``dy_emu`` ずらす。ずらした数を返す。"""
    hits = [s for s in slide.shapes if select(s)]
    for s in hits:
        s.top = s.top + int(dy_emu)
    return len(hits)


def _retarget_links(prs, old_part, new_part) -> None:
    """他の枚から ``old_part`` へのリンクを ``new_part`` へ付け替える。

    関係は作り直す。python-pptx は関係の行き先をキャッシュするので、行き先だけ書き換えると古い枚を指して保存される。
    """
    for slide in prs.slides:
        part = slide.part
        stale = [rid for rid, rel in part.rels.items() if rel.reltype == RT.SLIDE and rel.target_part is old_part]
        for old_rid in stale:
            new_rid = part.relate_to(new_part, RT.SLIDE)
            for node in slide._element.iter():
                if node.get(qn("r:id")) == old_rid:
                    node.set(qn("r:id"), new_rid)
            part.drop_rel(old_rid)


def _carry_deck_lists(prs, old_id, new_id) -> None:
    """節と目的別スライドショーの中の古い枚を新しい枚へ置き換える。"""
    root = prs.part._element
    for node in root.iter(P14_SLD_ID):
        if node.get("id") == old_id.get("id"):
            node.set("id", new_id.get("id"))
    for node in root.iter(qn("p:sld")):
        if node.get(qn("r:id")) == old_id.rId:
            node.set(qn("r:id"), new_id.rId)


def replace_slide(prs, number: int, src_slide):
    """``number`` 枚目（1 から数える）を ``src_slide`` の写しに入れ替える（末尾に写して位置へ移し、古い枚を外す）。新しい枚を返す。

    手の入っていない枚を生成器の新しい版で丸ごと替えるとき用。手の入った枚には使わない（直しが消える）。
    """
    ids = prs.slides._sldIdLst
    if not 1 <= number <= len(ids):
        raise IndexError(f"{number} 枚目は無い（{len(ids)} 枚）")
    new = copy_slide(src_slide, prs)
    new_id, old_id = ids[-1], ids[number - 1]
    old_part = prs.part.related_part(old_id.rId)
    _carry_deck_lists(prs, old_id, new_id)
    ids.remove(new_id)
    ids.insert(number - 1, new_id)
    prs.part.drop_rel(old_id.rId)
    ids.remove(old_id)
    _retarget_links(prs, old_part, new.part)
    prs.part.rename_slide_parts([s.rId for s in ids])   # python-pptx は最初の一度しか振り直さず、続けると名前が重なる
    return new


def replace_picture(slide, geometry_emu: tuple[int, int, int, int], png: bytes) -> str:
    """位置と大きさ (left, top, width, height) [EMU] が 1 px 以内で一致する画像 1 つの中身を ``png`` にする。名前を返す。"""
    hits = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE
            and all(abs(a - b) <= GEOMETRY_TOLERANCE_EMU for a, b in zip((s.left, s.top, s.width, s.height), geometry_emu))]
    if len(hits) != 1:
        raise LookupError(f"位置と大きさ {geometry_emu} の画像が {len(hits)} 個（1 個のときだけ差し替える）")
    _, rid = slide.part.get_or_add_image_part(io.BytesIO(png))
    hits[0]._element.blipFill.find(qn("a:blip")).set(qn("r:embed"), rid)
    return hits[0].name


def prepend_notes_line(slide, text: str, replace_if: str | None = None) -> None:
    """ノートの先頭に 1 段落 ``text`` を足す（残りの段落と書式はそのまま。足す段落は先頭の段落の書式を写す）。
    先頭の段落が ``replace_if``（正規表現）に合えば、足さずにその段落の文を置き換える（2 回かけても重ならない）。"""
    import re

    tf = slide.notes_slide.notes_text_frame
    first = tf.paragraphs[0]
    if replace_if and re.match(replace_if, first.text.strip()):
        runs = first.runs
        if not runs:
            first.text = text
            return
        runs[0].text = text
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
        return
    p_new = copy.deepcopy(first._p)
    for r in list(p_new.iter(qn("a:r")))[1:]:
        r.getparent().remove(r)
    for br in list(p_new.iter(qn("a:br"))):
        br.getparent().remove(br)
    runs = list(p_new.iter(qn("a:r")))
    if runs:
        runs[0].find(qn("a:t")).text = text
    else:
        r = p_new.makeelement(qn("a:r"), {})
        t = r.makeelement(qn("a:t"), {})
        t.text = text
        r.append(t)
        end = p_new.find(qn("a:endParaRPr"))
        (end.addprevious(r) if end is not None else p_new.append(r))
    first._p.addprevious(p_new)


def set_notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text
