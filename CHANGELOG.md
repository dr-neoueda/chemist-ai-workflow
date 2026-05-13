# Changelog

本ファイルは [Keep a Changelog](https://keepachangelog.com/) と [Semantic Versioning](https://semver.org/) に準拠。

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
