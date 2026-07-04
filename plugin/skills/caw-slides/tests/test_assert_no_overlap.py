"""assert_no_overlap ゲートのテスト（はみ出し・テキスト重なり検出）。"""
import pytest

import assert_no_overlap as ano


def _svg(body: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" '
        f'viewBox="0 0 1280 720">{body}</svg>'
    )


def _check(tmp_path, body):
    p = tmp_path / "case.svg"
    p.write_text(_svg(body), encoding="utf-8")
    return ano.check_svg(str(p))


def test_clean_has_no_violations(tmp_path):
    oob, ov, warns = _check(
        tmp_path,
        '<text x="80" y="120" font-size="28" font-family="Arial">Clean Title</text>'
        '<text x="80" y="300" font-size="20" font-family="Arial">Body within canvas</text>'
        '<text x="1200" y="694" font-size="13" text-anchor="end" font-family="Arial">6 / 6</text>',
    )
    assert not oob and not ov and not warns


def test_overlapping_text_is_error(tmp_path):
    oob, ov, warns = _check(
        tmp_path,
        '<text x="100" y="300" font-size="24" font-family="Arial">OVERLAPPING LABEL AAAAA</text>'
        '<text x="120" y="305" font-size="24" font-family="Arial">OVERLAPPING LABEL BBBBB</text>',
    )
    assert any(sev == "ERROR" for *_, sev in ov)


def test_offcanvas_detected(tmp_path):
    oob, ov, warns = _check(
        tmp_path,
        '<text x="1100" y="300" font-size="40" font-family="Arial">This runs far past the right edge</text>',
    )
    assert oob


def test_no_namespace_overlap_detected(tmp_path):
    """名前空間なしでも重なりを検出（fail-open 回帰）。"""
    oob, ov, warns = _check(
        tmp_path,
        '<text x="100" y="300" font-size="24">NONS OVERLAP AAAAA</text>'
        '<text x="118" y="304" font-size="24">NONS OVERLAP BBBBB</text>',
    )
    assert any(sev == "ERROR" for *_, sev in ov)


def test_style_sized_offcanvas(tmp_path):
    oob, ov, warns = _check(
        tmp_path,
        '<text x="1150" y="300" style="font-size:44px;font-weight:bold">Style-sized runs past right edge</text>',
    )
    assert oob


def test_positional_tspan_above_top_edge(tmp_path):
    oob, ov, warns = _check(
        tmp_path,
        '<text x="80" y="300" font-size="20">Leading line<tspan x="80" y="-40">Above top edge</tspan></text>',
    )
    assert oob


def test_leading_run_offcanvas(tmp_path):
    oob, ov, warns = _check(
        tmp_path,
        '<text x="1150" y="300" font-size="44">Lead run past right edge<tspan x="80" y="500">safe</tspan></text>',
    )
    assert oob


def test_transform_is_collected_as_warning_at_parse_layer(tmp_path):
    """parse 層では transform 付き text を測定せず warnings に集める（偽 bbox を作らない）。"""
    oob, ov, warns = _check(
        tmp_path,
        '<g transform="translate(100,100)"><text x="1260" y="10" font-size="40">only if measured raw</text></g>',
    )
    assert not oob and not ov and warns


def test_check_path_transform_is_hard(tmp_path):
    """check_path では transform 付き text は測定不能 → hard 違反（exit 1・false green を避ける）。"""
    (tmp_path / "xf.svg").write_text(
        _svg('<g transform="translate(100,100)"><text x="10" y="10" font-size="40">rotated label</text></g>'),
        encoding="utf-8",
    )
    assert ano.check_path(str(tmp_path)) == 1


def test_estimate_width_cjk_wider_than_latin():
    w_cjk = ano.estimate_text_width("あいう", 20.0, bold=False, letter_spacing=0.0)
    w_latin = ano.estimate_text_width("abc", 20.0, bold=False, letter_spacing=0.0)
    assert w_cjk > w_latin


def test_check_path_nonzero_on_offcanvas(tmp_path):
    (tmp_path / "off.svg").write_text(
        _svg('<text x="1100" y="300" font-size="40" font-family="Arial">runs far past the right edge</text>'),
        encoding="utf-8",
    )
    assert ano.check_path(str(tmp_path)) == 1


def test_check_path_missing_returns_two(tmp_path):
    assert ano.check_path(str(tmp_path / "nope")) == 2
