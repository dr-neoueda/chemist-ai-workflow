# ⏸ GitHub Copilot CLI 版は開発を保留中

paused_date: 2026-11-06
paused_at_plugin_version: 1.78.0
paused_at_copilot_version: 1.46.0

> このファイルは `scripts/check-consistency.sh` が読み取る**保留の記録の単一情報源**です。
> このファイルがある間、Codex 版と Copilot 版のミラー検査（2b・2c）は飛ばします。

## なぜ保留にしたか

研究トラックを化学者向けから理工系の研究者全般へ広げ、商品名とコマンド名を変える（`caw` → `raw`）
作業を、**Claude Code 版と Codex 版に絞って先に進める**ため（2026-11-06 の判断）。
Copilot 版まで同時に追従すると、作業量が 1.5 倍になる。

Gemini 版の凍結（`gemini-plugin/FROZEN.md`）とは違い、**やめたのではなく後回し**にしている。

## 保留中の状態

- Copilot 版は v1.78.0 の内容のまま配布される（化学者向けの文言・`caw` のコマンド名・`caw-slides` の lab 同等化まで）
- `copilot-plugin/` と `.github/plugin/marketplace.json` は触らない（版も上げない）
- 個人情報の検査（`check-consistency.sh` の 3）と不可視フォルダの検査（4）は保留中も Copilot 版にかける

## 再開するときの手順

1. Codex 版の 13 スキルを Copilot 版へ写す（以前の全面移植と同じ。`raw-*` の名前で）
2. `raw` と `raw-setup` は Copilot 向けの CLI 名（`copilot`）に直して移す
3. `copilot-plugin/plugin.json` と `.github/plugin/marketplace.json` の版を本体に揃える
4. このファイルを消し、`check-consistency.sh` の 2b・2c が通ることを確かめる
