# Changelog

本ファイルは [Keep a Changelog](https://keepachangelog.com/) と [Semantic Versioning](https://semver.org/) に準拠。

## [1.4.0 / Codex 1.3.0] - 2026-05-15

### Added — `caw-slides` Skill（PowerPoint スライド生成）

化学研究発表用 PowerPoint スライドを python-pptx ベースで生成する専用 Skill。実運用された 12 件のスライドから抽出したスタイルガイドを内蔵し、4 用途バリアントで「学会発表 / 論文紹介 / 報告会 / 講義」に対応する。

- **発火**: 自然言語マッチ（「スライド作って」「パワポ」「学会発表」「論文紹介」「報告会」「講義スライド」等）
- **同梱資産**（plugin / codex-plugin 並列配信）:
  - `references/pptx_helpers.py`（1000+ 行）: `add_slide_chrome` / `add_key_message_band` / `mixed_runs` / `assert_no_overlap` / `add_bar_chart` / `add_scatter_line_chart` / `add_flow_box` / `add_data_table` 等のヘルパ。MS Gothic のクロスプラットフォーム探索（macOS / Windows / Linux、`CAW_SLIDES_MSGOTHIC` 環境変数で override 可）
  - `references/style-guide.md`: 14 セクション + canonical 実装パターン（16:9、フォント混在、L1 強調 1 個ルール、3 層 y 座標構造（chrome / 本文 / key-message band）、3 tier 強調 L1/L2/L4（L2 = 影なし・枠線あり・塗りなしの透明箱）、native chart 強制、座標 hygiene、出典は用途別に任意で `add_source_line`）
  - `references/codex-exec-templates.md`: Codex 委譲 v2（完全お任せ）プロンプトテンプレ集
  - `templates/generate_conference.py`: 学会発表 variant（口頭・ポスター、20-50 枚）
  - `templates/generate_journal_club.py`: 論文紹介 variant（6-12 枚、pdftoppm + crop ワークフロー）
  - `templates/generate_lab_report.py`: 研究室報告会 variant（6-15 枚、native chart + table）
  - `templates/generate_lecture.py`: 講義・チュートリアル variant（15-30 枚、概念フロー図）
- **品質ゲート**: `assert_no_overlap` で shape 矩形交差を物理的に禁止（ValueError raise）、L1 1 個ルール、Excel-editable native chart のみ
- **動作確認**: 4 templates 全て smoke test 成功（標準的な 4 枚のデモ .pptx を生成、`assert_no_overlap` pass）

### Changed

- **`plugin/skills/caw/references/chemistry-departments.md`**: presentation 部の説明を caw-slides skill 利用前提に更新。サブディレクトリ列挙に `scripts/`, `notes/`, `references/` を追加、成果物パスを `slides/` → `presentations/slides/` に統一
- **`plugin/skills/caw/references/playbook-starters.md`**: 「計算外ソフトの Playbook」セクションを追加し、caw-slides との関係を明示
- **`web/src/content/docs/claude-code/application.md`**: §5 を caw-slides skill ベースに改稿（4 用途バリアント、共通スタイルガイド、`assert_no_overlap` 保証）
- `plugin/.claude-plugin/plugin.json` version 1.3.1 → 1.4.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.2.1 → 1.3.0
- `.claude-plugin/marketplace.json` plugin 列挙の version 同期

### Notes

- スライド生成システムは元々ユーザーの `.company/presentation/` で実運用されていた成熟資産を caw plugin 化したもの。新規開発ではなく **配信パッケージング**として実装。個人情報（著者名・研究室名・特定研究テーマ・機器型番）はすべて除去済み
- Codex CLI 版（codex-plugin）も同一資産を並列配信。両 CLI で完全機能パリティ
- python-pptx の依存（`python-pptx`、`matplotlib`、`Pillow`）はユーザーが事前にインストール
- スタイルガイド本体（`references/style-guide.md`）はプラグイン更新で上書きされる。プロジェクト固有のオーバーライドは `.company/presentation/CLAUDE.md` (or AGENTS.md) に追加

## [1.3.1 / Codex 1.2.1] - 2026-05-14

### Fixed（B16 — Windows / Linux 対応）

- **`plugin/hooks/load-playbooks.sh`**：mtime 降順ソートを BSD/macOS 専用の `xargs -0 stat -f "%m %N"` から `ls -t`（macOS / Linux / WSL / Git Bash 共通の POSIX）に置換。これまで macOS 以外（Linux 含む）で直近ノートの注入が動いていなかったのを修正
- **`plugin/skills/caw-doctor/SKILL.md` / `codex-plugin/skills/caw-doctor/SKILL.md`**：Playbook の `last_updated` 経過日数計算を BSD/macOS 専用の `date -j -f` から、GNU `date -d` → BSD `date -j` フォールバックの `to_epoch` ヘルパーに置換。macOS 以外でも動作するように

### Changed

- **`.company/` の可視性に関する説明を OS 別に正確化**：「Finder / Explorer から不可視」という macOS/Linux 前提の表現を「macOS Finder / Linux のファイルマネージャでは標準で非表示、Windows Explorer では表示される（いずれの OS でも運営情報専用エリアという位置づけは同じ）」に修正。SKILL.md / claude-md-template / agents-md-template / chemistry-departments / output-location-check.sh / README
- **`plugin/README.md`**：「動作環境」節を追加（OS × コア/Hooks の対応表、Windows は WSL / Git Bash 必須の旨）。v1.1.0 のまま古かった Skills / Hooks / Playbook / プラグイン構造の記述を v1.3.1 の実態に更新
- `plugin/.claude-plugin/plugin.json` version 1.3.0 → 1.3.1
- `codex-plugin/.codex-plugin/plugin.json` version 1.2.0 → 1.2.1
- `.claude-plugin/marketplace.json` version 同期

### Notes

- caw のコア（オンボーディング・部署スキャフォールド・5 Skills のワークフロー）は元々 OS 非依存。今回の修正は **hooks と caw-doctor の bash スニペットに混入していた macOS 専用構文**（`stat -f` / `date -j`）の除去で、これらは Windows のみならず Linux でも壊れていた
- Windows でネイティブに hooks を動かすには WSL または Git Bash が必要（`hooks.json` が `bash` を呼ぶため）。コア機能は Windows ネイティブでも動作

## [1.3.0 / Codex 1.2.0] - 2026-05-14

### Added

- **B1 — Codex 版の Skills 機能パリティ**：`caw-paper` / `caw-input` / `caw-playbook` を `codex-plugin/skills/` に移植。Codex 流に合わせ `trigger:` フィールドを削除し、自然言語マッチで発火。CLAUDE.md → AGENTS.md 表記に変換。これで両プラグインとも 5 Skills（caw / caw-doctor / caw-paper / caw-input / caw-playbook）で揃った
- **B2 — `caw-doctor` Skill 新規追加**（Claude / Codex 両版）：`.company/` 構造の健全性チェック。ルート CLAUDE.md・秘書部・各部署 CLAUDE.md の存在確認、旧構造（成果物が `.company/<dept>/X/` に残存）の検出、Playbook 更新滞り、同日ファイル重複、inbox 孤立ファイルを総点検し、レポート + 修復コマンドを提示
- **B7 — Playbook 雛形を 8 件拡充**（Claude / Codex 両版）：計算ソフト 4 件（Psi4 / NAMD / LAMMPS / OpenMM）+ Python ライブラリ 4 件（RDKit / ASE / MDAnalysis / pymatgen）を `playbook-starters.md` に追加。Python ライブラリ Playbook は API quirks・version 依存挙動・よくある罠を体系化
- **B8 — MCP 自動セットアップ案内**（Claude / Codex 両版）：オンボーディング Step 3-5 で Q3（ナレッジベース）/ Q4（クラウドストレージ）の選択に応じて `.company/.mcp-setup.md` を生成。Notion / Obsidian / Logseq / Google Drive / Dropbox / OneDrive / Gmail の MCP 設定手順 + API key の環境変数管理ガイド。`references/mcp-setup-templates.md` を新規追加。**鍵そのものは書かず手順書のみ**
- **B10 — オンボーディングの 3 段階化**（Claude / Codex 両版）：Step 2 に「セットアップモード」選択（Call 0）を追加。Quick（1 問・秘書のみ即起動）/ Standard（現行 6 問）/ Advanced（10+ 問、HPC・研究体制・申請書予定・論文ステータスまでヒアリング）
- **B11 — PostToolUse hook で二層原則違反を検出**（Claude Code 版のみ）：`plugin/hooks/output-location-check.sh` を追加。Edit/Write/MultiEdit が `.company/<dept>/<旧パス>/` に書き込んだ時に警告 + 修復コマンドを提示（block はしない warn-only）。`hooks.json` に PostToolUse エントリを追加。Codex 版は hook framework が未整備のため未対応

### Changed

- **`plugin/skills/caw/SKILL.md` / `codex-plugin/skills/caw/SKILL.md`**：Step 2 を 3 段階モード化、Step 3 に MCP セットアップ生成（3-5）を追加し完了メッセージを 3-6 にリネーム、「ファイル参照」に `mcp-setup-templates.md` を追加
- **`plugin/skills/caw/SKILL.md` / `codex-plugin/skills/caw/SKILL.md`**：オンボーディング Q2（計算ソフト）の古典 MD 例示に NAMD / OpenMM を追記（B7 と整合）
- `plugin/.claude-plugin/plugin.json` version 1.2.0 → 1.3.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.1.0 → 1.2.0
- `.claude-plugin/marketplace.json` version 同期

### Notes

- Codex 版は hooks 非対応（B11 のみ Claude Code 限定）。それ以外（B1/B2/B7/B8/B10）は両プラグインで機能等価
- caw-doctor は v1.2 の二層原則 migration 状況の点検にも使える（旧構造を検出して移行コマンドを提示）

## [1.2.0 / Codex 1.1.0] - 2026-05-14

### Added

- **成果物配置の二層原則（CRITICAL）**：caw の出力ファイルを `.company/` 配下（運営情報）と project root 直下（成果物）に明確に二層化
  - 第 1 層 `.company/<dept>/` = 運営情報のみ（TODO・意思決定・学び・Playbook・内部レビュー）
  - 第 2 層 project root = 成果物（`papers/`, `topics/`, `manuscripts/`, `slides/`, `analyses/`, `notebooks/`, `figures/`, `scripts/`, `tools/`, `reports/`, `experiments/`, `gaussian/` 等）
  - `.company/` は dotfile で Finder / Explorer から不可視。AI が生成した md / pptx / docx / png / ipynb 等を `.company/<dept>/` に置くと **ユーザーがファイラーで見つけられない** という v1.0 / v1.1 の構造的問題を解消

### Changed

- **`plugin/skills/caw/SKILL.md`**：「成果物配置の二層原則」セクションを追加。Step 3-4 の作業ディレクトリ生成リストを拡張（research → `papers/` + `topics/`、analysis → `analyses/` + `notebooks/` + `figures/`、engineering → `scripts/` + `tools/`、presentation → `slides/`）
- **`plugin/skills/caw/references/chemistry-departments.md`**：research / engineering / analysis / writing / presentation の各 CLAUDE.md テンプレで出力パスを `.company/<dept>/X/` から `{{PROJECT_ROOT}}/X/` に変更
- **`plugin/skills/caw/references/claude-md-template.md`**：ルート CLAUDE.md にも二層原則を明文化
- **`codex-plugin/skills/caw/SKILL.md`**：同上（AGENTS.md 表記）
- **`codex-plugin/skills/caw/references/agents-md-template.md`**：同上
- **`codex-plugin/skills/caw/references/chemistry-departments.md`**：同上
- `plugin/.claude-plugin/plugin.json` version 1.1.0 → 1.2.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.0.0 → 1.1.0
- `marketplace.json` version 同期

### Migration（v1.0 / v1.1 → v1.2 / Codex 1.0 → 1.1）

既存ユーザーが旧構造（`.company/research/papers/`, `.company/writing/manuscripts/`, `.company/analysis/results/`, `.company/presentation/slides/`）に成果物を蓄積している場合、以下を手動で実施：

```bash
# 移動例（既存ファイルがある場合のみ実行）
mv .company/research/papers/* papers/ 2>/dev/null
mv .company/research/topics/* topics/ 2>/dev/null
mv .company/writing/manuscripts/* manuscripts/ 2>/dev/null
mv .company/analysis/results/* analyses/ 2>/dev/null
mv .company/analysis/figures/* figures/ 2>/dev/null
mv .company/analysis/notebooks/* notebooks/ 2>/dev/null
mv .company/presentation/slides/* slides/ 2>/dev/null
```

`.company/<dept>/` 配下に残った空ディレクトリ（`papers/` `manuscripts/` 等）は削除して構わない。残しても害は無い（caw が読みに行かなくなるだけ）。

将来 v1.3 で `caw-migrate` Skill を追加予定（自動移動 + 衝突解決 + dry-run）。

## [Codex 1.0.0] - 2026-05-13

### Added (Codex CLI 版)

- **codex-plugin/**：Codex CLI 用 caw プラグイン（v1.0.0）を新規追加
  - `codex-plugin/.codex-plugin/plugin.json` — Codex 用プラグインマニフェスト
  - `codex-plugin/skills/caw/SKILL.md` — `/caw` スキル本体（CLAUDE.md → AGENTS.md ターゲットに変換）
  - `codex-plugin/skills/caw/references/{agents-md-template, chemistry-departments, playbook-starters}.md`
- **`.agents/plugins/marketplace.json`**：Codex 用マーケットプレイス manifest（同リポジトリから並列配信）
- **LP**：`/codex-cli/` セクションを placeholder から実装に書き換え、`/codex-cli/setup/` 環境構築ページを新規作成
- **plugin.md**：両環境のインストール手順（Claude Code / Codex CLI）を併記

研究室で Claude Code 派と Codex CLI 派が混在しても、同じ caw メソッドで `.company/` を運用できる構成。

## [1.1.0] - 2026-05-13

### Added

- **Hooks**：SessionStart で `.company/secretary/notes` の直近 3 件と利用可能 Playbook をコンテキスト自動注入、Stop で今日の活動があるのに learnings.md が無い場合にリマインド。
- **`/caw-paper` スキル**：論文検索（arXiv / Crossref / Semantic Scholar / OpenAlex / PubMed）と入手済み PDF の自動メタデータ抽出 → ナレッジベース（Notion / Obsidian / Logseq 等）+ クラウドストレージ（Google Drive 他）への登録。バッチ処理対応。
- **`/caw-input` スキル**：6 ソフト（Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO）の入力ファイル雛形生成。Playbook デフォルト推奨値を起点に対話的に系・目的・計算条件を確定、`<tool>/<system>_<purpose>_<YYYYMMDD>/` 配下に配置 + ジョブ記録自動生成。
- **`/caw-playbook` スキル**：計算 log の自動解析（収束 / エラー / 異常パターン）→ Lessons Learned エントリ起案 → Playbook への末尾追記。memory feedback への昇格判定も含む。

### Changed

- `plugin.json` version 1.0.0 → 1.1.0（後方互換のスキル追加）。
- `marketplace.json` version 同期。

## [1.0.0] - 2026-05-13

### Added

- 初回公開。caw プラグイン（Chemist's AI Workflow）。
- `/caw` スキル：オンボーディング → 自動スキャフォールド → 運営モードの一連を実装。
- 化学者向け 8 部署 CLAUDE.md テンプレート（secretary / research / engineering / computation / analysis / writing / review / presentation）。
- 計算ソフト Playbook 雛形：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用。
- 作業ディレクトリの自動生成：選択した計算ソフトに応じて `gaussian/` / `orca/` 等、選択した部署に応じて `papers/` / `manuscripts/` / `slides/`。
- ローカル marketplace 経由の開発・テスト環境。
- 4 つのテストプロファイルでの実機検証完了。

### Documentation

- 配布マーケットプレイスの `.claude-plugin/marketplace.json` を整備。
- MIT ライセンス採用。
- Chemist's AI Workflow LP（Astro Starlight）。
