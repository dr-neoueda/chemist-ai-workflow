---
name: caw-slides
description: >
  化学研究発表用 PowerPoint スライドを python-pptx ベースで生成する。
  学会発表（口頭・ポスター）、論文紹介（journal club）、研究室報告会・進捗共有、
  講義・チュートリアル資料の 4 用途に対応した汎用テンプレートを内蔵。
  16:9 / 和文 MS Gothic + 英数字 Arial / L1 強調 1 個ルール /
  assert_no_overlap 自動検証 / Excel-editable native chart を強制する
  スタイルガイドを同梱。スライド作成・パワポ・pptx・発表資料・学会発表・
  論文紹介・journal club・報告会・講義の依頼で発火。
---

# caw-slides — 研究発表スライド生成 Skill

## いつ使うか

ユーザーが以下のような発言をしたら発火:

- 「スライド作って」「パワポ作って」「発表資料お願い」
- 「学会発表用に」「○月○日の発表で」「ポスター」
- 「この論文を紹介するスライドにして」「journal club」
- 「報告会の資料」「今週の進捗まとめて」
- 「○○の講義スライド」「チュートリアル資料」

## ワークフロー（Step A-E）

このスキルは **Codex 委譲 v2: 完全お任せ** 方式を採用している。構成・L1 メッセージ・視覚デザインの判断は Codex に渡し、Claude は要件転送と検証に専念する。

### Step A: 要件転送（最低限の情報を抽出）

ユーザーの指示から以下を抽出する。構成や枚数は **Claude が決めない**:

| 必須項目 | 例 |
|---------|---|
| 元データのパス（または貼り付け本文） | `work/experiments/cp2k/foo/REPRODUCTION.md` |
| 発表場面 | 研究室報告会 / 国内学会 / 国際学会 / 研究紹介 / 修論 / 論文紹介 / 講義 |
| 言語 | 日本語 / 英語 |
| 制約（あれば） | 「枚数最大 20」「特定の図を必ず含める」など |

ユーザーが枚数・構成を指定していなければ Codex の裁量に任せる。

### Step B: テンプレ + helper をユーザーのプロジェクトにコピー

caw-slides Skill の `references/` と `templates/` から、ユーザーの `office/presentation/scripts/` に必要ファイルをコピー:

```bash
# pptx_helpers.py（ヘルパライブラリ）と research_icons.py（概念イラスト）をコピー
cp "${CAW_SLIDES_DIR}/references/pptx_helpers.py" office/presentation/scripts/
cp "${CAW_SLIDES_DIR}/references/research_icons.py" office/presentation/scripts/

# 用途別テンプレートをコピーして日付付き名前に変える
USE_CASE=conference   # or journal_club / lab_report / lecture
TODAY=$(date +%Y%m%d)
cp "${CAW_SLIDES_DIR}/templates/generate_${USE_CASE}.py" \
   "office/presentation/scripts/generate_<purpose>_${TODAY}.py"
```

`${CAW_SLIDES_DIR}` は Skill の install location（Claude Code: `~/.claude/plugins/marketplaces/*/skills/caw-slides/`）。

**`office/presentation/` が未存在**なら、先に `caw` Skill でスキャフォールドを促す。

### Step C: Codex に生成委譲（Codex CLI 利用時）/ または Claude 直接生成

#### Codex 委譲（推奨、`codex` コマンド利用可の場合）

`references/codex-exec-templates.md` の汎用版テンプレートを使う。`codex exec` 呼び出しは **必ず `</dev/null` で stdin を閉じる**（hang 事故防止）:

```bash
cat > /tmp/codex_prompt.txt <<'EOF'
<project_root>/office/presentation/AGENTS.md と、caw-slides の
references/style-guide.md のスタイルガイドに厳密に従って、研究発表用
PowerPoint スライドを生成してください。

## 元データ
<元データのパスまたは貼り付け本文>

## 発表場面・要件
- 場面: <報告会 / 国内学会 / 国際学会 / 研究紹介 / 修論 / 論文紹介 / 講義>
- 発表者: <your_name>
- 言語: <日本語 / 英語>
- 既知の制約: <あれば>

## Codex 自身に委ねる判断
- スライド枚数（スタイルガイド場面別目安）
- 各スライドのタイトル
- 各スライドの L1 メッセージ（1 スライド 1 個）
- 視覚要素の選定（テーブル / チャート / フロー図 / 原図切り抜き）
- 内容の取捨選択・圧縮

## 必須事項
- 着手前に `office/presentation/notes/<YYYY-MM-DD>-plan.md` に計画を書く
- 生成スクリプト: `office/presentation/scripts/generate_<purpose>_<YYYYMMDD>.py`
- .pptx: `work/presentations/slides/<purpose>_<YYYYMMDD>.pptx`
- `pptx_helpers.py` を import して再利用
- 各スライドビルダー末尾で `assert_no_overlap(rects)` を呼ぶ
- L1 強調は 1 スライド 1 個ルール厳守
EOF

codex exec --full-auto --skip-git-repo-check -C <project_root> \
  "$(cat /tmp/codex_prompt.txt)" </dev/null
```

#### Claude 直接生成（Codex 不可 or 軽微差分修正のとき）

Step B でコピーしたテンプレを `Read` → `Edit` で `<...>` プレースホルダをユーザー要件で埋める → `Bash` で実行 → 出力 .pptx を `python-pptx` で構造検証。

### Step D: 検証

```python
# python-pptx で構造検証
from pptx import Presentation
p = Presentation("work/presentations/slides/<...>.pptx")
print(f"slide count: {len(p.slides)}")
# 16:9 確認
print(f"aspect: {p.slide_width}x{p.slide_height}")
```

`soffice` があれば PNG レンダで目視も:

```bash
soffice --headless --convert-to png --outdir work/figures/_preview work/presentations/slides/<...>.pptx
```

**検証項目**:
1. スライド数が場面別目安と整合（報告会 6-15 / 国内学会 20-50 / 国際学会 20-25 等）
2. 16:9 アスペクト
3. 文字の枠内収まり、図・ボックスの重なり（**`assert_no_overlap` でスクリプト内検証**）
4. フォント豆腐（MS Gothic 設定）
5. L1 強調が 1 スライド 1 個ルール

問題があれば Step C に戻り Codex に差分修正委譲、または Claude が `Edit` で直接修正。

### Step E: 完了報告

`office/secretary/notes/<YYYY-MM-DD>-decisions.md` に記録:

- 出力 .pptx パス
- 採用した枚数 + 根拠
- 各スライドのタイトル + L1 メッセージ一覧
- 使ったテンプレート種別

## 5 用途バリアント

| 用途 | テンプレ | 想定枚数 | 特徴 |
|------|--------|---------|------|
| 学会発表（口頭・ポスター） | `generate_conference.py` | 20-25 / 20-50 | 専門家向け、結果プロット主体、L1 一行で主張明確 |
| 論文紹介（journal club） | `generate_journal_club.py` | 6-12 | 原論文・SI 図主体、pdftoppm + crop 抽出、source line 必須 |
| 研究室報告会・進捗共有 | `generate_lab_report.py` | 6-15 | 自前データ主体、native chart + table、今後の予定 |
| 講義・チュートリアル | `generate_lecture.py` | 15-30 | 平易語、概念フロー図、目標 + 前提 + サマリ |
| 宣伝・紹介・募集（showcase） | `generate_showcase.py` | 5-8 | 実スクショ主役のコラージュ、プログラム名ヘッダ、キャプション画像上、アプリロゴ。**§0 緩和**（style-guide §15） |

詳細は各テンプレの docstring を参照。showcase variant は研究発表用 4 種と設計思想が異なり、
§0 のテキスト最小ルールを緩和する（密なコラージュ）。詳細は style-guide §15。

## スタイルガイドの絶対ルール

`references/style-guide.md` に体系化されている。**Skill 発火時は必ず style-guide.md の §0 を最初に読むこと。**

### §0（最優先・絶対ルール）

**文字数を極限まで減らし、図表で直感的に伝える。** スライドはテキストを読ませる媒体ではなく、聴衆に瞬時に意味を伝える視覚装置。

- 数値・比較・時系列・プロセス・関係性は **必ず** 図表（chart / table / flow diagram / scheme）で示す
- 1 スライド内のテキストボックスは **3 個まで**（タイトル + 本文 + key-message band）、補足 1 個まで許容
- 本文ブロックは **総 8 行まで**、1 ボックス内 **120 字まで**；超えたらスライド分割 or 内容捨てる
- フォント自動縮小で 16pt 未満に落とすのは禁止
- タイトルは主張形（❌「結果」/ ✅「Form I が 175 分で Form II に転移」）
- このルールはセクション 11 / 12 / 14 のすべてに優先する。判断に迷ったら §0 が勝つ

### 他のルール（§0 と矛盾しない範囲で適用）

- スライドサイズは **常に 16:9（13.33" × 7.5"）**
- 和文 = **MS Gothic**、英数字 = **Arial**（`mixed_runs` で自動切替）
- フォントサイズ: タイトル 28pt / 本文 20pt / 強調 24pt / 補足 12pt
- **1 スライド 1 メッセージ**（L1 強調は 1 スライド 1 個）
- 白背景、アニメーションなし、グリッド整列
- **`assert_no_overlap` を全スライドビルダー末尾で必ず呼ぶ**
- グラフは **Excel-editable native chart のみ**（PNG 禁止、`add_bar_chart` / `add_scatter_line_chart`）
- フロー図は **native shape + arrow のみ**（`add_flow_box` + `add_flow_arrow`）

## 同梱資産

| ファイル | 役割 |
|---------|------|
| `references/pptx_helpers.py` | 共通ヘルパ（1000+ 行、`add_slide_chrome` / `add_key_message_band` / `mixed_runs` / `assert_no_overlap` / `add_bar_chart` / `add_scatter_line_chart` 等） |
| `references/research_icons.py` | 概念イラスト（線画アイコン 10 種 + `hub_diagram` / `cycle_diagram` / `converging_diagram` 構図ビルダー）。詳細は style-guide §11bis |
| `references/style-guide.md` | スタイルガイド本体（15 セクション + canonical 実装パターン。§15 = showcase レイアウト） |
| `references/codex-exec-templates.md` | Codex 委譲プロンプトテンプレ集 |
| `templates/generate_conference.py` | 学会発表 variant |
| `templates/generate_journal_club.py` | 論文紹介 variant |
| `templates/generate_lab_report.py` | 報告会 variant |
| `templates/generate_lecture.py` | 講義 variant |
| `templates/generate_showcase.py` | 宣伝・紹介・募集 variant（コラージュ型・§15） |

## 重要な注意事項

- 既存スライドの修正は **PowerPoint 上の手修正ではなくスクリプトを正とする** — 生成スクリプトを編集して再生成
- 同名 .pptx を再生成すると上書きされる。バックアップが必要なら日付サフィックスを変える
- スタイルガイド本体（`references/style-guide.md`）はプラグイン更新で上書きされる。プロジェクト固有のルールは `office/presentation/CLAUDE.md` (or AGENTS.md) に追加し、本体は触らない
- python-pptx の依存（`python-pptx`、`matplotlib`、`Pillow`）はユーザーが事前にインストール:

```bash
pip install python-pptx matplotlib Pillow
# 日本語 matplotlib のため MS Gothic も必要（macOS は Microsoft Office に同梱、
# Windows は標準搭載、Linux は手動配置 + CAW_SLIDES_MSGOTHIC 環境変数）
```

## トラブルシュート

| 症状 | 対処 |
|------|------|
| `ValueError: Layout overlap: ...` | スライド内 shape の矩形が重なっている。`assert_no_overlap` のメッセージで重なった shape ペアを特定し、座標を調整。または shape を削減 |
| 日本語が豆腐（縦長 □）になる | `pptx_helpers.configure_matplotlib_japanese()` を呼んでいるか確認。MS Gothic が見つからないなら `export CAW_SLIDES_MSGOTHIC=/path/to/msgothic.ttc` |
| `codex exec` が hang する | `</dev/null` で stdin を閉じていない可能性。`codex-exec-templates.md` の「禁止形」参照 |
| L1 強調が複数スライドに出る | スタイルガイド §14-2 違反。各スライドで `add_key_message_band` を 1 回だけ呼ぶ |
| chart の軸ラベルが英語フォントで崩れる | `_style_chart_common` がフォント自動切替するが、軸タイトルは `mixed_runs` で明示すると確実 |

## 関連 Skill

- `caw` — `office/` 部署スキャフォールド（presentation 部含む）
- `caw-paper` — 論文 PDF を `work/papers/` に登録（journal club 用素材の源泉）
- `caw-playbook` — 計算ソフト Playbook 蓄積（報告会・学会発表の素材）
