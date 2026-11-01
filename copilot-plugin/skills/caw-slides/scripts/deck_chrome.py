"""スライド SVG の共通部品（caw-slides）。見出し・フッター・本文・強調帯を 1 か所に固定する。

ゲートが拾わない規約をここで機械的に守る。和文は親の ``<text>`` に和文フォントを持たせ、ASCII だけを Arial の
``tspan`` に包む。この形は左揃えでのみ安全で、中央・右揃えの文字に ``tspan`` があると変換器が幅を誤測する。
だから本モジュールの関数は ``text-anchor="start"`` だけを出す（中央揃えは ``deck_parts.centred``）。

既定の見た目は「定型の生成物に見える構造物」を置かないように決めてある。
縦のアクセント線・二言語キッカー・タイトル下のリード文・全ページの注記・固定幅の枠は使わない。
減らすのは構造物であって色ではない（青・金・赤・緑は意味の色として使い続ける）。
"""
from __future__ import annotations

import re
from xml.sax.saxutils import escape

JP = "'MS Gothic','Hiragino Kaku Gothic ProN',Arial"
ASCII_FONT = "Arial"

NAVY = "#16283D"
BLUE = "#1F6FEB"    # 中立
GOLD = "#B9791F"    # 注意
RED = "#D6455D"     # 警告
GREEN = "#2E9E6B"   # 良好
BODY = "#47535F"
DARKBODY = "#334452"
GREY = "#8894A2"
DIVIDER = "#D8E0E8"
HAIRLINE = "#EDF1F5"
FRAME = "#E3E9F0"

CALLOUT_PAD = 28      # 強調帯の左右の内余白 [px]
ASCII_ADV, CJK_ADV = 0.56, 1.0   # 文字送りの推定（check_margins.py と同じ値）
BOLD_ADV = 1.06       # 太字の膨らみ
FIT_SAFETY = 1.04     # 推定が細めに出たときに文字がはみ出さないための余裕
WASH = 0.96           # 強調帯の地を白へ寄せる割合。0.97 以上はほぼ白で地の意味が消える

# 四角マーカーの一辺 [px]。見出しと行頭は別の意味なので必ず差を付ける（片方だけ変えると見分けが付かなくなる）
MARK_COLUMN = 9       # 列見出し・小見出しの前に置く印
MARK_BULLET = 5       # 箇条書きの行頭に置く印

# 文字の見かけの中心が基線から何 em 上にあるか。MS Gothic も Arial の大文字もおよそ 0.36 em
VISUAL_CENTRE_EM = 0.36

# pptx は 1280 px = 13.333 in なので 1 px = 0.75 pt。本文は 14 pt（56/3 px）を下限にする。
# 文献・細かい条件・ページ番号は fine=True で下限をかけない
PT_PER_PX = 0.75
BODY_MIN_PX = 56 / 3

SCRIPT_SCALE = 0.68   # 上付き・下付きの大きさ（行の文字に対する比）

# 見出しの区切り線はタイトル（28 px、基線 y=118）の直下。本文の頭は線 + 16〜40 px に置く
DIVIDER_Y = 140

# Arial が描けない文字（または別の字形になる文字）。漢字でなくても和文の run に残す。
# 丸数字は Arial に入ると豆腐になる
_JP_EXTRA = set("①②③④⑤⑥⑦⑧⑨⑩⚠★●▶→←↑↓⇒〜・「」『』（）、。％±×÷≦≧≠∼—―")

# ASCII 外でも Arial が描ける記号。「ΔΔE‡」を 2 つのフォントに分けると字間が開く
_ARIAL_EXTRA = set("Δ‡≈¹")

_SCRIPT = re.compile(r"(\^\{[^}]*\}|_\{[^}]*\})")


def _is_ascii_run(ch: str) -> bool:
    return (ch.isascii() and ch != "\n" and ch not in _JP_EXTRA) or ch in _ARIAL_EXTRA


def _mix_plain(text_: str) -> str:
    """上付き・下付きを含まない文字列を、和文と ASCII の run に分ける。"""
    out, buf, in_ascii = [], [], False
    for ch in text_:
        ascii_run = _is_ascii_run(ch)
        if buf and ascii_run != in_ascii:
            out.append((in_ascii, "".join(buf)))
            buf = []
        in_ascii = ascii_run
        buf.append(ch)
    if buf:
        out.append((in_ascii, "".join(buf)))
    parts = []
    for is_ascii, chunk in out:
        escaped = escape(chunk)
        parts.append(f'<tspan font-family="{ASCII_FONT}">{escaped}</tspan>' if is_ascii and chunk.strip() else escaped)
    return "".join(parts)


def _script(token: str, size: float) -> str:
    """``^{..}`` / ``_{..}`` を ``baseline-shift`` の tspan にする（Unicode の上付き数字は使わない）。"""
    shift = "super" if token[0] == "^" else "sub"
    inner = token[2:-1]
    if not inner or "{" in inner:
        raise ValueError(f"上付き・下付きの書き方が正しくない: {token!r}")
    font = ASCII_FONT if all(_is_ascii_run(ch) for ch in inner) else JP
    return (f'<tspan font-family="{font}" baseline-shift="{shift}" '
            f'font-size="{round(size * SCRIPT_SCALE)}">{escape(inner)}</tspan>')


def mix(text_: str, size: float = 16) -> str:
    """和文と ASCII が混ざった文字列を run に分け、ASCII を Arial に包む。

    親の ``<text>`` が和文フォントを持っている前提で、左揃えの文字にだけ使う。
    ``^{-1}`` / ``_{2}`` は上付き・下付きの tspan になる。

    Parameters
    ----------
    text_ : str
        文字列。
    size : float
        行の文字の大きさ [px]。上付き・下付きの大きさを決める。

    Returns
    -------
    str
        ``<text>`` の中身。
    """
    parts = []
    for tok in _SCRIPT.split(text_):
        if _SCRIPT.fullmatch(tok):
            parts.append(_script(tok, size))
        elif "^{" in tok or "_{" in tok:
            raise ValueError(f"上付き・下付きの閉じ括弧が無い: {text_!r}")
        elif tok:
            parts.append(_mix_plain(tok))
    return "".join(parts)


def advance(body: str, size: float, *, bold: bool = False) -> float:
    """文字列の描画幅の推定 [px]。``check_margins.py`` と同じ字送りを使う。"""
    plain = _SCRIPT.sub(lambda m: m.group(0)[2:-1], body)
    raw = sum(size * (ASCII_ADV if ch.isascii() else CJK_ADV) for ch in plain)
    return raw * (BOLD_ADV if bold else 1.0)


def wash(colour: str, t: float = WASH) -> str:
    """``colour`` を白に ``t`` だけ寄せた色。枠線と同じ色から作るので 4 色の薄さがそろう。"""
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * t) for c in (r, g, b))


def body_size(size: float, *, fine: bool = False) -> float:
    """本文の文字の大きさ [px]。``fine`` でなければ 14 pt 未満を 14 pt に上げる。"""
    return size if fine else max(size, BODY_MIN_PX)


def fmt_size(size: float) -> str:
    """SVG の font-size の文字列（18.666… は 18.67。pptx では 14.0 pt になる）。"""
    return f"{round(size, 2):g}"


def text(x: float, y: float, body: str, *, size: float = 16, fill: str = BODY, bold: bool = False, font: str = JP,
         raw: bool = False, fine: bool = False) -> str:
    """左揃えの 1 行。``raw`` なら run に分けない。``fine`` なら 14 pt の下限をかけない（文献・条件の注）。"""
    size = body_size(size, fine=fine)
    weight = ' font-weight="bold"' if bold else ""
    content = escape(body) if raw else mix(body, size)
    return (f'<text x="{x}" y="{y}" font-size="{fmt_size(size)}" fill="{fill}"{weight} '
            f'font-family="{font}">{content}</text>')


# 1 行の中で色・太さを変える区間: (文字, 色, 太字)
Run = tuple[str, str, bool]


def rich(x: float, y: float, runs: tuple[Run, ...], *, size: float = 16) -> str:
    """区間ごとに色・太さを変えた左揃えの 1 行。"""
    size = body_size(size)
    if not runs:
        raise ValueError(f"rich at y={y}: 区間が 1 つも無い")
    spans = []
    for body, fill, bold in runs:
        weight = ' font-weight="bold"' if bold else ""
        spans.append(f'<tspan fill="{fill}"{weight}>{mix(body, size)}</tspan>')
    return (f'<text x="{x}" y="{y}" font-size="{fmt_size(size)}" fill="{runs[0][1]}" '
            f'font-family="{JP}">{"".join(spans)}</text>')


def _line_width(line: str | tuple[Run, ...], size: float, *, bold: bool = False) -> float:
    """``callout`` の 1 行の幅の推定 [px]。区間の列なら区間ごとの太さで足す。"""
    if isinstance(line, str):
        return advance(line, size, bold=bold)
    return sum(advance(body, size, bold=b) for body, _, b in line)


def header(title: str, *, accent: str = BLUE, raise_px: int = 0) -> str:
    """見出し。短い名詞句のタイトルと区切り線だけ。

    リード文の引数は持たない（渡すと TypeError）。その枚の主張は本文・図・強調帯で示す。
    ``raise_px`` は、見出しごと上へ詰めたい枚に使う。
    """
    return ('  <g id="header">\n'
            f'    <rect x="80" y="{72 - raise_px}" width="40" height="6" fill="{accent}"/>\n'
            f'    <text x="80" y="{118 - raise_px}" font-size="28" font-weight="bold" fill="{NAVY}" '
            f'font-family="{JP}">{mix(title, 28)}</text>\n'
            f'    <line x1="80" y1="{DIVIDER_Y - raise_px}" x2="1200" y2="{DIVIDER_Y - raise_px}" '
            f'stroke="{DIVIDER}" stroke-width="1"/>\n'
            '  </g>\n')


def footer(n: int, total: int) -> str:
    """右下のページ番号だけ。全ページに同じ注記を入れない。"""
    return ('  <g id="footer">\n'
            f'    <text x="1200" y="694" font-size="13" fill="{GREY}" font-family="{ASCII_FONT}" '
            f'text-anchor="end">{n} / {total}</text>\n'
            '  </g>\n')


def app_footer(k: int) -> str:
    """補足の枚の番号（右下）。和文を含むので和文フォント 1 本で tspan を使わない（右揃えの幅誤測を避ける）。"""
    return ('  <g id="footer">\n'
            f'    <text x="1200" y="694" font-size="13" fill="{GREY}" font-family="{JP}" '
            f'text-anchor="end">補足 {k}</text>\n'
            '  </g>\n')


def cover(title_lines: list[str], *, authors: str | None = None, affiliation: str | None = None,
          venue: str | None = None) -> str:
    """表紙。アクセントの帯・36 px のタイトル・区切り線・著者などの行。

    Parameters
    ----------
    title_lines : list[str]
        タイトルの各行。
    authors, affiliation, venue : str | None
        著者（22 px）・所属（本文）・会議名や日付（灰色の本文）。``^{1}`` で所属番号を書ける。

    Returns
    -------
    str
        ``<g id="cover">`` の断片。
    """
    if not title_lines:
        raise ValueError("cover: タイトルの行が無い")
    out = ['  <g id="cover">\n', f'    <rect x="80" y="150" width="72" height="8" fill="{BLUE}"/>\n']
    y = 214
    for line in title_lines:
        out.append(f'    {text(80, y, line, size=36, fill=NAVY, bold=True)}\n')
        y += 52
    rule_y = y - 52 + 34
    out.append(f'    <line x1="80" y1="{rule_y}" x2="1200" y2="{rule_y}" stroke="{DIVIDER}" stroke-width="1"/>\n')
    y = rule_y + 44
    if authors:
        out.append(f'    {text(80, y, authors, size=22, fill=NAVY)}\n')
        y += 36
    if affiliation:
        out.append(f'    {text(80, y, affiliation, fill=BODY)}\n')
        y += 42
    if venue:
        out.append(f'    {text(80, y, venue, fill=GREY)}\n')
    out.append('  </g>\n')
    return "".join(out)


def _square_marker(x: float, baseline: float, side: int, colour: str, text_size: float) -> str:
    """四角マーカーを 1 つ描く。縦位置は隣の文字の見かけの中心に合わせる。

    上端を定数で持つと、一辺を変えたときに中心だけがずれる。基線・文字サイズ・一辺から毎回導く。
    """
    top = round(baseline - VISUAL_CENTRE_EM * text_size - side / 2)
    return f'    <rect x="{x}" y="{top}" width="{side}" height="{side}" fill="{colour}"/>\n'


def bullet(x: float, y: float, body: str, *, colour: str = BLUE, size: float = 16, fill: str = BODY,
           bold: bool = False, gap: int = 22) -> str:
    """小さい四角マーカーと 1 行。``y`` は文字の基線、``gap`` はマーカーの左端から文字までの距離 [px]。"""
    size = body_size(size)
    return (_square_marker(x, y, MARK_BULLET, colour, size)
            + f'    {text(x + gap, y, body, size=size, fill=fill, bold=bold)}\n')


def column_head(x: float, y: float, body: str, *, colour: str = NAVY, size: float = 20, gap: int = 18) -> str:
    """列見出し。四角マーカーと見出し語で、左に縦棒は置かない。``colour`` がマーカーと文字の両方に効く。"""
    size = body_size(size)
    return (_square_marker(x, y, MARK_COLUMN, colour, size)
            + f'    {text(x + gap, y, body, size=size, fill=colour, bold=True)}\n')


def callout(x: float, y: float, w: float, h: float, lines: list[str | tuple[Run, ...]], *, edge: str = BLUE,
            title: str | tuple[Run, ...] | None = None, size: float = 16, lead: int = 28) -> str:
    """要点ボックス。領域ごとに 1 つ、データが密な枚でも 2 つまで。

    左の縦棒は付けない。1 px の枠線と、枠線の色を白へ寄せたごく薄い地で作る。
    ``edge`` は中立＝青・注意＝金・警告＝赤・良好＝緑。幅は中身に合わせ、``w`` は上限として扱う。

    Parameters
    ----------
    x, y : float
        左上 [px]。
    w : float
        幅の上限 [px]。
    h : float
        高さ [px]。
    lines : list
        本文の各行。文字列、または区間の列（``Run`` のタプル）。
    edge : str
        枠線の色。
    title : str | tuple | None
        題。あれば本文の上に太字で置く。
    size : float
        文字の大きさ [px]。
    lead : int
        行送り [px]。

    Returns
    -------
    str
        ``<path>`` と ``<text>`` の断片。

    Raises
    ------
    ValueError
        行が高さまたは幅に収まらない。ゲートは文字と枠の関係を見ないので、ここで止める。
    """
    size = body_size(size)
    last = 34 + (lead + 6 if title else 0) + lead * (len(lines) - 1) if lines else 34
    needed = last + 0.3 * size + 8
    if needed > h:
        raise ValueError(f"callout at y={y}: {len(lines)} line(s) need height {needed:.0f}, got {h}")
    candidates = [_line_width(line, size) for line in lines]
    if title:
        candidates.append(_line_width(title, size, bold=True))
    widest = max(candidates) if candidates else 0.0
    if CALLOUT_PAD * 2 + widest * FIT_SAFETY > w:
        raise ValueError(f"callout at y={y}: 行の幅 {widest:.0f} px が枠の上限 {w} px − 余白に入らない")
    width = min(w, round(CALLOUT_PAD * 2 + widest * FIT_SAFETY))
    r = 10
    out = [f'    <path fill="{wash(edge)}" stroke="{edge}" stroke-width="1" '
           f'd="M{x + r},{y} H{x + width - r} A{r},{r} 0 0 1 {x + width},{y + r} '
           f'V{y + h - r} A{r},{r} 0 0 1 {x + width - r},{y + h} H{x + r} '
           f'A{r},{r} 0 0 1 {x},{y + h - r} V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z"/>']
    ty = y + 34
    if title:
        out.append(f'    {text(x + CALLOUT_PAD, ty, title, size=size, fill=NAVY, bold=True)}' if isinstance(title, str)
                   else f'    {rich(x + CALLOUT_PAD, ty, title, size=size)}')
        ty += lead + 6
    for line in lines:
        out.append(f'    {text(x + CALLOUT_PAD, ty, line, size=size, fill=DARKBODY)}' if isinstance(line, str)
                   else f'    {rich(x + CALLOUT_PAD, ty, line, size=size)}')
        ty += lead
    return "\n".join(out) + "\n"


def section_head(x: float, y: float, label: str, *, width: float = 690) -> str:
    """細い線つきの小見出し。"""
    return (f'    {text(x, y, label, size=BODY_MIN_PX, fill=NAVY, bold=True)}\n'
            f'    <line x1="{x}" y1="{y + 16}" x2="{x + width}" y2="{y + 16}" stroke="{HAIRLINE}" stroke-width="1"/>\n')


def svg(body: str) -> str:
    """1 枚分の SVG。背景の全面 rect は描かない（スライドマスターの白がそのまま出る）。"""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" '
            'viewBox="0 0 1280 720">\n' + body + '</svg>\n')
