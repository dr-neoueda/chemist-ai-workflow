# Changelog

本ファイルは [Keep a Changelog](https://keepachangelog.com/) と [Semantic Versioning](https://semver.org/) に準拠。

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
