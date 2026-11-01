"""check_margins のテスト: 右余白 1200 を越える文字を拾い、右寄せのページ番号は誤検出しない。"""
import check_margins as cm


def _write(tmp_path, body):
    (tmp_path / "01.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>', encoding="utf-8")
    return tmp_path


def test_right_anchored_footer_at_the_margin_passes(tmp_path):
    root = _write(tmp_path, '<text x="1200" y="694" font-size="13" text-anchor="end">3 / 12</text>')
    assert cm.check(root) == []


def test_fractional_font_size_is_read(tmp_path):
    root = _write(tmp_path, '<text x="1100" y="300" font-size="18.67">長い本文がここで右の余白を越える</text>')
    assert len(cm.check(root)) == 1


def test_missing_directory_is_an_error_not_zero_findings(tmp_path):
    assert cm.main([str(tmp_path / "nope")]) == 2
