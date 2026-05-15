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

# caw-slides — 研究発表スライド生成 Skill（Codex 版）

## いつ使うか

ユーザーが以下のような発言をしたら発火:

- 「スライド作って」「パワポ作って」「発表資料お願い」
- 「学会発表用に」「○月○日の発表で」「ポスター」
- 「この論文を紹介するスライドにして」「journal club」
- 「報告会の資料」「今週の進捗まとめて」
- 「○○の講義スライド」「チュートリアル資料」

Codex CLI ではスラッシュ起動不要。自然言語マッチで発火する。

## ワークフロー（Codex 直接生成）

Codex は自分で構成・L1 メッセージ・視覚デザインを決定し、生成スクリプトと .pptx を作る。Claude Code 版と異なり、**委譲なし・直接実行**。

### Step 1: 要件確認

ユーザーの指示から以下を確認:

- **元データ**: パス or 本文（例: `experiments/<...>/REPRODUCTION.md`）
- **発表場面**: 研究室報告会 / 国内学会 / 国際学会 / 研究紹介 / 修論 / 論文紹介 / 講義
- **言語**: 日本語 / 英語
- **制約**: 枚数指定、必須図など（あれば）

ユーザーが構成や枚数を指定していなければ、スタイルガイドの場面別目安に従い Codex が自ら決める。

### Step 2: スタイルガイド読込 + 計画メモ

1. `references/style-guide.md`（同梱）を読み、適用すべきルールを把握
2. プロジェクトに `<project_root>/.company/presentation/AGENTS.md` があればそれも読む（プロジェクト固有のオーバライド）
3. `.company/presentation/notes/<YYYY-MM-DD>-plan.md` を作成し、以下を書き残してから実装に入る:
   - スライド数（場面別目安: 報告会 6-15 / 国内学会 20-50 / 国際学会 20-25 / 修論 25-35 / 論文紹介 6-12 / 講義 15-30）
   - 各スライドのタイトル
   - 各スライドの L1 メッセージ（1 スライド 1 個、具体的な主張）
   - 視覚要素の方針（テーブル / chart / フロー図 / 原図切り抜き）

### Step 3: テンプレ + ヘルパをユーザーの scripts/ にコピー

```bash
# Codex CLI install location は ~/.codex/plugins/cache/*/skills/caw-slides/
CAW_SLIDES_DIR=$(find ~/.codex/plugins/cache -type d -name "caw-slides" | head -1)

cp "${CAW_SLIDES_DIR}/references/pptx_helpers.py" .company/presentation/scripts/

USE_CASE=conference   # conference / journal_club / lab_report / lecture
TODAY=$(date +%Y%m%d)
cp "${CAW_SLIDES_DIR}/templates/generate_${USE_CASE}.py" \
   ".company/presentation/scripts/generate_<purpose>_${TODAY}.py"
```

**`.company/presentation/` が未存在**なら、先に `caw` Skill でスキャフォールド。

### Step 4: 実装（テンプレ編集）

コピーした `generate_<purpose>_<YYYYMMDD>.py` を編集:

1. `<...>` プレースホルダをユーザー要件の実値で置換
2. 元データから抽出した数値・図を反映
3. スライドビルダーを必要数だけ追加（Step 2 計画通り）
4. **各スライドビルダー末尾で `assert_no_overlap(rects)` を必ず呼ぶ**
5. L1 強調は 1 スライド 1 個（`add_key_message_band` を 1 回だけ）
6. グラフは **native chart のみ**（`add_bar_chart` / `add_scatter_line_chart`）
7. フロー図は **native shape + arrow のみ**（`add_flow_box` + `add_flow_arrow`）

### Step 5: 生成 + 検証

```bash
python .company/presentation/scripts/generate_<purpose>_<YYYYMMDD>.py
```

`assert_no_overlap` が `ValueError` で停止したら、座標を調整して再実行。

検証:

```python
from pptx import Presentation
p = Presentation("presentations/slides/<purpose>_<YYYYMMDD>.pptx")
print(f"slide count: {len(p.slides)}")
print(f"aspect: {p.slide_width}x{p.slide_height}")  # 16:9 確認
```

`soffice` があれば PNG レンダで目視:

```bash
soffice --headless --convert-to png --outdir figures/_preview presentations/slides/<...>.pptx
```

### Step 6: 完了報告

`.company/secretary/notes/<YYYY-MM-DD>-decisions.md` に記録:

- 出力 .pptx パス
- 採用した枚数 + 根拠
- 各スライドのタイトル + L1 メッセージ一覧
- 使ったテンプレート種別

## 4 用途バリアント

| 用途 | テンプレ | 想定枚数 | 特徴 |
|------|--------|---------|------|
| 学会発表（口頭・ポスター） | `generate_conference.py` | 20-25 / 20-50 | 専門家向け、結果プロット主体、L1 一行で主張明確 |
| 論文紹介（journal club） | `generate_journal_club.py` | 6-12 | 原論文・SI 図主体、pdftoppm + crop 抽出、source line 必須 |
| 研究室報告会・進捗共有 | `generate_lab_report.py` | 6-15 | 自前データ主体、native chart + table、今後の予定 |
| 講義・チュートリアル | `generate_lecture.py` | 15-30 | 平易語、概念フロー図、目標 + 前提 + サマリ |

## スタイルガイドの絶対ルール

`references/style-guide.md` に体系化されている。**抜粋**:

- スライドサイズは **常に 16:9（13.33" × 7.5"）**
- 和文 = **MS Gothic**、英数字 = **Arial**（`mixed_runs` で自動切替）
- フォントサイズ: タイトル 28pt / 本文 20pt / 強調 24pt / 補足 12pt
- **1 スライド 1 メッセージ**（L1 強調は 1 スライド 1 個）
- 白背景、アニメーションなし、グリッド整列
- **`assert_no_overlap` を全スライドビルダー末尾で必ず呼ぶ**
- グラフは **Excel-editable native chart のみ**（PNG 禁止）
- フロー図は **native shape + arrow のみ**

## 同梱資産

| ファイル | 役割 |
|---------|------|
| `references/pptx_helpers.py` | 共通ヘルパ（1000+ 行） |
| `references/style-guide.md` | スタイルガイド本体 |
| `references/codex-exec-templates.md` | プロンプトテンプレ集（他 CLI 連携用） |
| `templates/generate_conference.py` | 学会発表 variant |
| `templates/generate_journal_club.py` | 論文紹介 variant |
| `templates/generate_lab_report.py` | 報告会 variant |
| `templates/generate_lecture.py` | 講義 variant |

## 重要な注意事項

- 既存スライドの修正は **PowerPoint 上の手修正ではなくスクリプトを正とする**
- スタイルガイド本体（`references/style-guide.md`）はプラグイン更新で上書きされる。プロジェクト固有ルールは `.company/presentation/AGENTS.md` に追加
- Python 依存:

```bash
pip install python-pptx matplotlib Pillow
```

- MS Gothic が標準パスにない場合: `export CAW_SLIDES_MSGOTHIC=/path/to/msgothic.ttc`

## トラブルシュート

| 症状 | 対処 |
|------|------|
| `ValueError: Layout overlap: ...` | shape 矩形が重なっている。`assert_no_overlap` のメッセージで重なった shape ペアを特定し座標調整 |
| 日本語が豆腐（縦長 □）に | `pptx_helpers.configure_matplotlib_japanese()` を呼んでいるか確認 |
| L1 強調が複数スライドに | スタイルガイド §14-2 違反。各スライドで `add_key_message_band` を 1 回だけ呼ぶ |

## 関連 Skill

- `caw` — `.company/` 部署スキャフォールド（presentation 部含む）
- `caw-paper` — 論文 PDF を `papers/` に登録
- `caw-playbook` — 計算ソフト Playbook 蓄積
