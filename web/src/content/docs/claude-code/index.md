---
title: "Tier 1: Claude Code（premium）"
description: Skills / Hooks / Sub-agents / MCP を活用した、本書の主軸となる実装
---

## なぜ Claude Code を主軸に置くか

- **Skills**：プロジェクト固有のメソッドをバージョン管理可能な単位で運用できる
- **Hooks**：SessionStart / PostToolUse / Stop などのライフサイクルに介入できる
- **Sub-agents**：特化エージェント（reviewer / planner / TDD など）に分業させられる
- **MCP（Model Context Protocol）**：各種ナレッジベース・クラウドストレージ・GitHub・Playwright などに直接接続。Notion・Google Drive は Anthropic 公式 MCP、Obsidian / Logseq などファイルベースのツールは Filesystem MCP 経由で連携（[対応ツール一覧](/tools/)）
- 著者が日常運用している環境であり、本書で最も検証が深い実装

## このセクションの構成

環境構築から応用まで、9 つのページに分けて整理します。

### 基礎

- [環境構築](/claude-code/setup/) — インストール、認証、初期確認、化学者向け推奨設定
- [設定の階層と基礎](/claude-code/basics/) — `~/.claude/` と `.claude/`、CLAUDE.md、settings.json

### コア機能

- [Skills](/claude-code/skills/) — プロジェクト固有のメソッドをバージョン管理可能な単位にする
- [Hooks](/claude-code/hooks/) — SessionStart / PreToolUse / PostToolUse / Stop で自動化
- [Sub-agents](/claude-code/subagents/) — 特化エージェントの並行実行と役割分担
- [MCP サーバー連携](/claude-code/mcp/) — ナレッジベース・クラウドストレージ・開発ツールへの接続

### 応用

- [.company/ 部署テンプレート](/claude-code/company-template/) — 著者の実働システムを再現可能テンプレート化
- [応用：化学研究での実例](/claude-code/application/) — 文献管理・計算ジョブ・申請書・論文執筆・スライド生成
- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — AI エージェント運用に慣れてからの上級パターン

## 配布物（Phase 2 以降）

- `.company/` テンプレートリポジトリ（git clone で即運用開始）
- Skills 設定サンプル集
- Hooks レシピ
- Sub-agent 定義集
- 各実例の完全スクリプト・テンプレ・運用手順

## ステータス

**Phase 1（2026-05-10）**: 各章のオリエンテーションを公開。**Phase 2（2026-06 開始）**: 実装の詳細・配布リポジトリを順次追加。
