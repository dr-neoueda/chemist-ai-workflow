"""assert_font_rule ゲートのテスト（和文=日本語フォント / 英数=Arial）。"""
import pytest

import assert_font_rule as afr

JP = "'MS Gothic','Hiragino Kaku Gothic ProN',Arial"


def _svg(body: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" '
        f'viewBox="0 0 1280 720">{body}</svg>'
    )


CASES = {
    # 和文が日本語フォント・英数が Arial → 違反なし
    "clean": (
        f'<text x="80" y="120" font-family="{JP}">和文はゴシック</text>'
        f'<text x="80" y="160" font-family="Arial">ASCII only 123</text>'
        f'<text x="80" y="200" font-family="{JP}"><tspan font-family="{JP}">背景</tspan> · BG</text>',
        0,
    ),
    # 漢字を Arial run に（→ 中国語フォント化/豆腐の典型ミス）
    "arial_kanji": ('<text x="80" y="120" font-family="Arial">a 軸</text>', 1),
    # 入れ子 tspan で Arial にカナ
    "nested_arial": (
        f'<text x="80" y="120" font-family="{JP}">速度 <tspan font-family="Arial">~10% / 6 日</tspan> 終</text>',
        1,
    ),
    # style 属性で Arial に全角記号
    "style_arial": ('<text x="80" y="120" style="font-family:Arial">項目・値</text>', 1),
    # font-family 未指定で CJK
    "nofont": ('<text x="80" y="120">無指定の漢字</text>', 1),
    # 祖先 <g> からの継承（違反ではない）
    "ancestor_jp": (f'<g font-family="{JP}"><text x="80" y="120">継承した和文</text></g>', 0),
    # inline style が属性より優先（属性 JP でも style Arial なら違反）
    "style_override": (
        f'<text x="80" y="120" font-family="{JP}" style="font-family:Arial">日本語</text>',
        1,
    ),
    # inherit キーワードは親を継承（違反ではない）
    "inherit_keyword": (
        f'<text x="80" y="120" font-family="{JP}"><tspan font-family="inherit">日本語</tspan></text>',
        0,
    ),
    # CJK 拡張 B の漢字を Arial に（範囲拡張の回帰）
    "ext_b": ('<text x="80" y="120" font-family="Arial">\U00020bb7</text>', 1),
    # CSS プロパティ名は大小無視（Font-Family:Arial + 漢字 → 違反）
    "style_case": ('<text x="80" y="120" style="Font-Family:Arial">大小無視の漢字</text>', 1),
    # 丸数字 ①②③（U+2460+）を Arial に → 豆腐。囲み CJK 範囲で検出できること
    "circled_number_arial": ('<text x="80" y="120" font-family="Arial">① 広帯域</text>', 1),
    # "Century Gothic" はラテン専用（"gothic" を含むが日本語不可）→ 漢字は違反
    "century_gothic_kanji": ('<text x="80" y="120" font-family="Century Gothic">漢字</text>', 1),
    # MS Gothic は日本語フォント → 違反でない（家系名の正当一致）
    "ms_gothic_ok": ('<text x="80" y="120" font-family="MS Gothic">和文</text>', 0),
}


@pytest.mark.parametrize("body,expect", list(CASES.values()), ids=list(CASES.keys()))
def test_check_svg_cases(tmp_path, body, expect):
    p = tmp_path / "case.svg"
    p.write_text(_svg(body), encoding="utf-8")
    assert len(afr.check_svg(str(p))) == expect


def test_no_ns_jp_font_is_clean(tmp_path):
    """名前空間なし + 日本語フォント名（游ゴシック）は違反でない。"""
    p = tmp_path / "nons.svg"
    p.write_text(
        '<svg width="1280" height="720"><text x="80" y="120" font-family="游ゴシック">名前空間なし</text></svg>',
        encoding="utf-8",
    )
    assert afr.check_svg(str(p)) == []


def test_resolve_svgs_single_file(tmp_path):
    p = tmp_path / "a.svg"
    p.write_text(_svg('<text x="1" y="1">x</text>'), encoding="utf-8")
    assert afr.resolve_svgs(str(p)) == [str(p)]


def test_resolve_svgs_non_svg_file(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("not svg", encoding="utf-8")
    assert afr.resolve_svgs(str(p)) == []


def test_resolve_svgs_directory_sorted(tmp_path):
    for name in ("02.svg", "01.svg", "note.txt"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    got = afr.resolve_svgs(str(tmp_path))
    assert [p.rsplit("/", 1)[-1] for p in got] == ["01.svg", "02.svg"]


def test_resolve_svgs_subdir_fallback(tmp_path):
    sub = tmp_path / "svg_output"
    sub.mkdir()
    (sub / "a.svg").write_text("x", encoding="utf-8")
    assert afr.resolve_svgs(str(tmp_path)) == [str(sub / "a.svg")]


def test_check_path_returns_nonzero_on_violation(tmp_path):
    (tmp_path / "bad.svg").write_text(
        _svg('<text x="80" y="120" font-family="Arial">漢字</text>'), encoding="utf-8"
    )
    assert afr.check_path(str(tmp_path)) == 1


def test_check_path_returns_zero_on_clean(tmp_path):
    (tmp_path / "ok.svg").write_text(
        _svg(f'<text x="80" y="120" font-family="{JP}">和文</text>'), encoding="utf-8"
    )
    assert afr.check_path(str(tmp_path)) == 0


def test_check_path_missing_returns_two(tmp_path):
    assert afr.check_path(str(tmp_path / "nope")) == 2
