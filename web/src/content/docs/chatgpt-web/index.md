---
title: "Tier 4: Web 版（最小）"
description: ブラウザのみで完結する圧縮版。CLI を使えない環境向け
---

## なぜ Web 版を残すか

- 大学事務 PC や共用端末など **CLI が使えない環境** で完全に機能停止すると教材として弱い
- ChatGPT Plus / Claude Pro / Gemini Advanced のサブスク勢にとっての導線
- AI 部署メソッドを「Custom Instructions」「Projects」機能に圧縮した最小版を提示

## 章立て（執筆中）

1. ChatGPT Custom Instructions に圧縮する（複数 AI 部署 → 単一プロンプト）
2. Claude Projects への落とし込み
3. Gemini の Gem 機能との対応
4. ファイル管理は**お使いのクラウドストレージ + ナレッジベース**で代替（Google Drive / Dropbox + Notion / Obsidian など）
5. CLI 版へのアップグレードパス

## 制約と限界

- **Hooks / Sub-agents / MCP は使えない**
- **長文の文脈保持に弱い**（Custom Instructions の文字数制限）
- **品質ゲートの自動化が手動運用になる**

→ あくまでエントリー & 緊急時用。長期運用なら CLI 版を推奨。

## ステータス

**Phase 2（2026-06）執筆予定**。
