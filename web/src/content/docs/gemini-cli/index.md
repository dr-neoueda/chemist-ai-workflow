---
title: "Tier 3: Gemini CLI（OSS）"
description: OSS / Apache 2.0 のターミナル native エージェント。個人 Google アカウント連携で手厚い無料枠
---

## なぜ Gemini CLI を扱うか

- **OSS（Apache 2.0）**：ソースコードが公開されており、内部挙動を確認できる
- **手厚い無料枠**：個人 Google アカウント連携で Gemini 2.5 Pro クラスを 60 req/min・1000 req/day 程度
- **Claude Code / Codex CLI と同系統**：ターミナル native エージェントの選択肢として並び立つ
- 学生・若手 PI にとって、金銭面でのエントリー障壁が低い選択肢

## 章立て（執筆中）

1. Gemini CLI セットアップ
2. 個人 Google アカウント連携と無料枠の使い切り戦略
3. AGENTS.md 風のルールファイルを Gemini CLI に効かせる
4. Claude Code / Codex CLI との機能比較表
5. 化学計算系の実例（PDF 解析、log ファイル要約）
6. 「無料枠で回せる範囲」の見極め

## 関連 Google プロダクト（参考）

- **Jules**：GitHub 連携の async coding agent。Codex web 相当
- **Gemini Code Assist**：IDE 拡張（VS Code / JetBrains）。Copilot 寄り

→ 本書では **ターミナル native の Gemini CLI** を主に扱う。

## ステータス

**Phase 2（2026-06）執筆予定**。最新仕様は Phase 2 開始時に再 verify する。
