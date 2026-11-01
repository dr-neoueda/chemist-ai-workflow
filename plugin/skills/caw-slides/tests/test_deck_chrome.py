"""deck_chrome のテスト: 定型の見た目（AI 作成感）を出さない見出し・強調帯・本文の下限。"""
import xml.etree.ElementTree as ET

import deck_chrome as dc
import pytest

SVG = "{http://www.w3.org/2000/svg}"


def _parse(fragment: str) -> ET.Element:
    return ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{fragment}</svg>')


def test_header_is_short_title_and_divider_only():
    root = _parse(dc.header("押しの向き"))
    texts = list(root.iter(f"{SVG}text"))
    assert len(texts) == 1                                   # キッカーもリード文も無い
    line = next(root.iter(f"{SVG}line"))
    assert line.get("y1") == str(dc.DIVIDER_Y) == "140"


def test_header_rejects_a_lead_sentence():
    with pytest.raises(TypeError):
        dc.header("題", "この枚の主張の 1 文")                # 引数ごと無い


def test_footer_is_page_number_only():
    root = _parse(dc.footer(3, 12))
    texts = list(root.iter(f"{SVG}text"))
    assert [t.text for t in texts] == ["3 / 12"]


def test_mix_wraps_ascii_in_arial_and_keeps_circled_digits_in_jp():
    out = dc.mix("収率 95% ①")
    assert '<tspan font-family="Arial"> 95% </tspan>' in out
    assert "①" in out.split("</tspan>")[-1]                  # 丸数字は Arial に入れない（豆腐）


def test_mix_keeps_delta_and_double_dagger_in_arial():
    assert '<tspan font-family="Arial">ΔΔE‡</tspan>' in dc.mix("ΔΔE‡は")


@pytest.mark.parametrize("token,shift,inner", [("cm^{-1}", "super", "-1"), ("H_{2}O", "sub", "2")])
def test_scripts_become_baseline_shift_tspans(token, shift, inner):
    out = dc.text(80, 200, token)
    node = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{out}</svg>').find(f"{SVG}text")
    scripts = [t for t in node.iter(f"{SVG}tspan") if t.get("baseline-shift")]
    assert [(t.get("baseline-shift"), t.text) for t in scripts] == [(shift, inner)]
    assert float(scripts[0].get("font-size")) < float(node.get("font-size"))


def test_body_text_is_raised_to_14pt_unless_fine():
    assert float(_parse(dc.text(80, 200, "本文", size=16)).find(f"{SVG}text").get("font-size")) == 18.67
    assert float(_parse(dc.text(80, 200, "文献", size=13, fine=True)).find(f"{SVG}text").get("font-size")) == 13


def test_bullet_marker_is_smaller_than_column_head_marker():
    assert dc.MARK_BULLET < dc.MARK_COLUMN
    bullet = next(_parse(dc.bullet(80, 200, "項目")).iter(f"{SVG}rect"))
    head = next(_parse(dc.column_head(80, 200, "見出し")).iter(f"{SVG}rect"))
    assert int(bullet.get("width")) == dc.MARK_BULLET and int(head.get("width")) == dc.MARK_COLUMN


def test_wash_gives_equal_faintness_across_colours():
    distances = []
    for colour in (dc.BLUE, dc.GOLD, dc.RED, dc.GREEN):
        washed = dc.wash(colour)
        channels = [int(washed[i:i + 2], 16) for i in (1, 3, 5)]
        distances.append(255 - min(channels))
    assert max(distances) - min(distances) <= 3 and max(distances) <= 11


def test_callout_has_no_left_bar_and_uses_outline_with_wash():
    frag = dc.callout(80, 500, 1120, 60, ["要点"], edge=dc.GOLD)
    root = _parse(frag)
    assert not list(root.iter(f"{SVG}rect"))                 # 縦棒の rect を描かない
    path = next(root.iter(f"{SVG}path"))
    assert path.get("stroke") == dc.GOLD and path.get("fill") == dc.wash(dc.GOLD)


def test_callout_width_follows_content_not_the_given_width():
    frag = dc.callout(80, 500, 1120, 60, ["短い"])
    d = next(_parse(frag).iter(f"{SVG}path")).get("d")
    right_edge = float(d.split("H")[1].split()[0]) + 10
    assert right_edge < 80 + 400


def test_callout_rejects_too_many_lines_for_the_height():
    with pytest.raises(ValueError, match="height"):
        dc.callout(80, 500, 1120, 40, ["一行目", "二行目", "三行目"])


def test_callout_rejects_a_line_wider_than_its_limit():
    with pytest.raises(ValueError, match="幅"):
        dc.callout(80, 500, 200, 60, ["とても長い一行が枠の上限を越えてしまう場合の文章です"])


def test_svg_wraps_on_the_1280x720_canvas():
    root = ET.fromstring(dc.svg(dc.header("題") + dc.footer(1, 2)))
    assert root.get("viewBox") == "0 0 1280 720"


def test_cover_has_title_rule_and_meta_lines_without_a_side_bar():
    root = _parse(dc.cover(["結晶相反応の", "速度論"], authors="著者", affiliation="所属", venue="学会"))
    sizes = [float(t.get("font-size")) for t in root.iter(f"{SVG}text")]
    assert sizes[0] == sizes[1] == 36 and len(sizes) == 5
    rects = list(root.iter(f"{SVG}rect"))
    assert all(int(r.get("height")) < 720 for r in rects)     # 左端の全高の縦棒を置かない


def test_reserved_characters_are_escaped():
    node = _parse(dc.text(80, 200, "A<B & C>D ^{a&b}")).find(f"{SVG}text")
    assert "".join(node.itertext()) == "A<B & C>D a&b"


@pytest.mark.parametrize("bad", ["x^{}", "x^{1", "x_{2", "x^{a{b}}"])
def test_malformed_script_markup_stops_early(bad):
    with pytest.raises(ValueError, match="上付き"):
        dc.text(80, 200, bad)


def test_callout_rejects_a_line_that_only_fits_without_the_safety_margin():
    line = "あ" * 20                                         # 373 px（14 pt）
    fits_barely = dc.CALLOUT_PAD * 2 + dc.advance(line, dc.BODY_MIN_PX) + 2
    with pytest.raises(ValueError, match="幅"):
        dc.callout(80, 500, fits_barely, 60, [line])


def test_latin1_superscript_digits_stay_in_the_arial_run():
    """¹²³ は Latin-1。和文の run に入ると字面が基線からずれる。"""
    assert 'font-family="Arial">10¹³ m² </tspan>' in dc.mix("10¹³ m² の面")
    assert ">³</tspan>" in dc.mix("の³")
