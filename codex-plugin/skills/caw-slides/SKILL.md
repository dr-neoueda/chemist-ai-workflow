---
name: caw-slides
description: >
  研究発表用 PowerPoint スライドを SVG-first で生成する。手描き SVG（1280×720）を
  native DrawingML pptx に変換し、図形・表・native chart が PowerPoint で直接編集できる。
  学会発表・論文紹介（journal club）・研究室報告会・講義の 4 用途に対応。デザインは
  PPT Master default 準拠（和文 MS Gothic / 英数 Arial）。フォント/重なりゲートで
  authoring ミス（豆腐・はみ出し・重なり）を機械的に潰す。各 CLI で自己完結（外部委譲なし）。
  スライド・パワポ・pptx・発表資料・学会発表・論文紹介・journal club・報告会・講義で発火。
---

# caw-slides — 研究発表スライド生成（SVG-first）

## いつ使うか

- 「スライド作って」「パワポ作って」「発表資料お願い」「学会発表用に」「ポスター」
- 「この論文を紹介するスライドにして」「journal club」「報告会の資料」「講義スライド」

`office/presentation/`（プレゼン部）が無ければ `caw` でスキャフォールドを促す。**就活トラック**では「これは研究向けのスキルです」と伝える。

## 設計思想（重要）

**手描き SVG → native pptx**。python-pptx でレイアウトを組むのではなく、**SVG を正として描き**、同梱の変換器（`vendor/svg_to_pptx`、native DrawingML 出力）で pptx 化する。だから図形・表・チャートが PowerPoint で**直接編集できる**（ラスタ画像でない）。

- **デザインは `references/design-system.md` に従う**（PPT Master default 準拠・日本語ローカライズ）。**発火時に必ず design-system.md を読む**。
- **各 CLI で自己完結**：Claude Code / Codex CLI / Gemini CLI いずれも、その CLI 自身が SVG を描き・変換し・検証する。**別 CLI への委譲はしない**（追加プラグイン不要）。
- **ゲートで機械的に検証**：authoring ミス（和文の豆腐・はみ出し・重なり）は目視前にスクリプトで潰す。
- **出力は pptx のみ**（§出力規約）。

`${SKILL}` = このスキルの install 位置（各 CLI のプラグイン配下の `skills/caw-slides/`）。以下のコマンドの `${SKILL}` を実パスに置換して実行する。

## はじめてモードを尊重する

`office/CLAUDE.md`（Codex/Copilot は `AGENTS.md`、Gemini は `GEMINI.md`）冒頭に `> 運用モード: はじめて` があれば、`caw` skill の「はじめてモードの挙動」を全応答に適用する。

## ワークフロー（Step A–H）

### Step A: 用途と素材を確定
| 項目 | 内容 |
|---|---|
| 用途 | 論文紹介 / 学会発表 / 報告会 / 講義 |
| 元データ | 論文紹介＝`work/papers/`（`caw-register` 登録の md ＋原論文 PDF）／ 学会・報告会＝`work/manuscripts/`・`work/profile/key-findings.md`・`work/analyses/`／ 講義＝指定教材 |
| 言語・場面・制約 | 日本語/英語、枚数目安（下表）、必須で入れる図 |

### Step B: SVG を描く（`design-system.md` どおり）
- 1 スライド = 1 つの `.svg`（`01_cover.svg`, `02_...` と連番）。`viewBox="0 0 1280 720"`。作業場所は `work/presentations/slides/_src/<deck>/`（配布先でなく作業層）。
- **§0 図表優先・1 スライド 1 メッセージ**。タイトルは主張形。家具（accent bar＋kicker＋navy タイトル＋divider、footer）は design-system.md §2 の座標に従う。
- **論文図の切り抜き**（論文紹介）：まずページを見て座標を当て、region で高解像度切り抜き：
  ```bash
  python3 ${SKILL}/scripts/crop_paper_figures.py page   <pdf> <page_no> /tmp/pg.png --dpi 150
  python3 ${SKILL}/scripts/crop_paper_figures.py region <pdf> <page_no> <x0> <y0> <x1> <y1> <out.png> --dpi 300
  ```
  切り抜き図は SVG に **data-URI で埋め込む**（`<image href="data:image/png;base64,...">`）。source caption（誌名・Fig 番号）を必ず添える。
- **自作の図表・チャート・スキームは native SVG shape** で描く（`<rect>`/`<line>`/`<path>`/`<text>`）→ 変換後も編集可能。棒グラフ＝rect、フロー＝rect＋marker 矢印、表＝rect（navy ヘッダ）＋text＋divider line。
- **数式（LaTeX）**：`scripts/render_latex.py` で**透過 PNG にレンダ**して SVG に data-URI で埋め込む（図の切り抜きと同じ流儀。数式はラスタ埋込になる）。既定は **matplotlib mathtext のオフライン**（ネット不要・第三者送信なし・速度論/熱力学/量子化学の数式を広くカバー）。`\ce{}`（mhchem）等フル LaTeX が要る式のみ `--online`（codecogs へ・要ネット）:
  ```bash
  python3 ${SKILL}/scripts/render_latex.py "k = A e^{-E_a/RT}" <out.png> --dpi 300 --color "#16283D"
  python3 ${SKILL}/scripts/render_latex.py "\ce{2H2 + O2 -> 2H2O}" <out.png> --online   # フル LaTeX
  ```

### Step C: ゲート（必ず PASS させる）
```bash
python3 ${SKILL}/scripts/assert_font_rule.py  work/presentations/slides/_src/<deck>/   # 和文=日本語フォント
python3 ${SKILL}/scripts/assert_no_overlap.py work/presentations/slides/_src/<deck>/   # 重なり・はみ出し
```
違反が出たら SVG を直して再実行。**両方 PASS するまで次に進まない**（豆腐・重なりはここで潰す）。

### Step D: native pptx に変換（同梱変換器）
```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "${SKILL}/vendor")
from pathlib import Path
from svg_to_pptx import create_pptx_with_native_svg
src = Path("work/presentations/slides/_src/<deck>")
create_pptx_with_native_svg(sorted(src.glob("*.svg")),
    Path("work/presentations/slides/<deck>.pptx"),
    canvas_format="ppt169", use_native_shapes=True, verbose=False)
PY
```

### Step E: 後処理（ea フォント修正）
```bash
python3 ${SKILL}/scripts/fix_ea_font.py work/presentations/slides/<deck>.pptx
```
変換器が CJK run に残す ea≠MS Gothic を強制修正（必ず 1 回）。

### Step F: 目視 QA（プレビューは scratchpad のみ）
- 全ページを目視する。プレビュー PNG は **scratchpad（`/tmp` 配下）でだけ**生成し、配布先には置かない（§出力規約）。cairosvg があれば SVG→PNG（プレビュー時のみ `'MS Gothic'`→`Hiragino` 置換で macOS 描画）。
- design-system.md §8 の 2 罠（中央寄せ×混在フォント×添字／丸数字豆腐）はゲート緑でも残るので必ず目視。

### Step G: 配布（pptx のみ）
- `work/presentations/slides/<deck>.pptx` を **pptx 1 ファイルだけ**残す。**preview PNG・中間 SVG を配布先に置かない**。
- 生成に使った SVG は `_src/<deck>/` に残して再生成可能にする（配布先の直下には出さない）。

### Step H: 残す価値があれば playbook に蒸留
- 繰り返す構成・レシピは `caw-playbook` 方式で `work/presentations/_playbook.md` 等に残す。

## 出力規約（HARD rule）
- **配布先（`work/presentations/slides/`）に置く成果物は `.pptx` のみ。** preview PNG・中間 SVG・ページ画像をコピーしない。
- preview PNG は目視 QA 専用として scratchpad で生成し、QA 後は放置でよい。

## 用途別の目安
| 用途 | 想定枚数 | 特徴 |
|------|---------|------|
| 論文紹介（journal club） | 6–12 | 原論文図（crop）＋自作図表を混在。①表紙 ②背景 ③機構/系 ④自作データ ⑤主要図 ⑥結論＋**自研究への接続**。各図に「図の読み方」支持本文 |
| 学会発表（口頭・ポスター） | 20–25 | 専門家向け、結果プロット主体、L1 一行で主張明確 |
| 研究室報告会・進捗 | 6–15 | 自前データ主体、native chart＋table、今後の予定 |
| 講義・チュートリアル | 15–30 | 平易語、概念フロー図、目標＋前提＋サマリ |

## 同梱資産
| パス | 役割 |
|---|---|
| `references/design-system.md` | デザイン規約（PPT Master default 準拠・日本語ローカライズ・SVG 制約）。**発火時必読** |
| `vendor/svg_to_pptx/` | SVG→native DrawingML 変換器（上流 PPT Master・MIT、`vendor/NOTICE.md` 参照） |
| `scripts/assert_font_rule.py` | 和文フォントゲート（stdlib のみ） |
| `scripts/assert_no_overlap.py` | 重なり/はみ出しゲート（stdlib のみ） |
| `scripts/crop_paper_figures.py` | 論文 PDF 図の高解像度切り抜き（PyMuPDF） |
| `scripts/render_latex.py` | LaTeX 数式を透過 PNG にレンダ（matplotlib オフライン→任意で codecogs） |
| `scripts/fix_ea_font.py` | ビルド後 pptx の ea フォント修正（python-pptx） |
| `tests/` | 上記スクリプトの pytest（挙動仕様） |

## 依存
```bash
pip install python-pptx        # 変換・ea 修正（必須）
pip install Pillow             # ラスタ図の埋め込み時
pip install PyMuPDF            # 論文図の切り抜き時（crop_paper_figures）
pip install matplotlib         # LaTeX 数式のオフラインレンダ時（render_latex）
# 和文は MS Gothic を想定（macOS は Office 同梱／Windows 標準）。プレビューは Hiragino 代替可
# 数式のフル LaTeX（\ce 等）を --online で使う場合はネットワークが要る（codecogs）
```

## トラブルシュート
| 症状 | 対処 |
|------|------|
| `assert_font_rule` FAIL（CJK in non-JP font） | その run の font-family を日本語フォントに。中央寄せラベルは単一 MS Gothic 化、添字は左寄せ＋`baseline-shift` tspan（design-system §5/§8） |
| `assert_no_overlap` FAIL（overlap/off-canvas） | 座標を調整 or 要素削減。transform 付き text は使わず explicit x/y に |
| 日本語が豆腐（□） | 和文が Arial run に入っている（丸数字①・全角記号・⁻¹ も）。日本語フォント run へ。ビルド後は `fix_ea_font` |
| 図が編集できない（画像化） | native shape/text で描いたか確認。ラスタは論文切り抜き図のみ |

## 関連 Skill
- `caw` — presentation 部を含む scaffold
- `caw-register` — 論文 PDF を `work/papers/` に登録（journal club 素材）
- `caw-write` — 自分の論文・要旨（学会/報告会スライドの元データ）
- `caw-playbook` — 構成・レシピの蓄積
