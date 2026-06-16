---
title: "Claude Code"
description: Skills / Hooks / Sub-agents / MCP を活用した、本書の主軸となる実装の片翼（もう片翼は Codex CLI）
---

Anthropic 製のターミナル CLI エージェント。本書では **Codex CLI と並ぶ主軸 CLI** として扱う。著者の日常運用環境であり、検証密度が最も高い。

## Claude Code の特徴

- **Skills**：プロジェクト固有のメソッドをバージョン管理可能な単位で運用できる
- **Hooks**：SessionStart / PostToolUse / Stop などのライフサイクルに介入できる（Codex より hook 種類が豊富）
- **Sub-agents**：特化エージェント（reviewer / planner / TDD など）を並列起動でき、専用 context window で動作
- **MCP（Model Context Protocol）**：各種ナレッジベース・クラウドストレージ・GitHub・Playwright などに直接接続。Notion・Google Drive は Anthropic 公式 MCP、Obsidian / Logseq などファイルベースのツールは Filesystem MCP 経由で連携（[対応ツール一覧](/tools/)）
- **CLAUDE.md** をプロジェクトルールの標準ファイルとする（Codex の `AGENTS.md` に対応）

## caw プラグイン（Claude Code 版）導入

```bash
/plugin marketplace add dr-neoueda/chemist-ai-workflow
/plugin install caw@chemist-ai-workflow
```

`/plugin list` で `caw` が `enabled` 表示されれば導入完了。詳細手順は [環境構築](/claude-code/setup/) を参照。

## クイックスタート

```bash
cd ~/your-research-project
claude
> /caw
```

`office/` が存在しない場合、対話的オンボーディング（研究プロファイル 4 問 + 部署選択）が起動し、化学者向けにカスタマイズされた部署と作業ディレクトリが一括生成される。

## Codex CLI との関係 — 使い分けの目安

caw プラグインは Claude Code 版と Codex CLI 版の **両方** で並列配信されており、研究室で混在運用が可能。両者は機能パリティを保っていますが、運用上の使い分けの目安は以下のとおりです。

| 場面 | 推奨 CLI | 理由 |
|---|---|---|
| Hooks による自動化を組み込みたい（保存時の auto-format、Stop hook での品質ゲート等） | **Claude Code** | Hook 種類が豊富（SessionStart / PreToolUse / PostToolUse / Stop / PreCompact 等） |
| Sub-agent エコシステムを活用したい（言語別 reviewer / build-resolver / planner 等） | **Claude Code** | `everything-claude-code` 等のサードパーティ sub-agent 群が成熟 |
| OpenAI 系モデル（GPT-5 系）を使いたい / 機関契約が OpenAI 側 | **Codex CLI** | モデル選択肢が異なる |
| 物理意味論視点の二段レビューが欲しい（単位・式の整合性） | **Claude + Codex 併用** | 異なる observation を出すという実例あり ([二段レビュー](/claude-code/two-stage-review/)) |
| スラッシュと自然言語マッチを明確に分けたい | **Codex CLI** | Skills（自然言語マッチ）と Commands（`/`）が別名前空間 |

詳細比較は [Codex CLI 概要](/codex-cli/) の「Claude Code との機能比較」表を参照。

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

- [office/ 部署テンプレート](/claude-code/company-template/) — 著者の実働システムを再現可能テンプレート化
- [応用：化学研究での実例](/claude-code/application/) — 文献管理・計算ジョブ・申請書・論文執筆・スライド生成
- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — AI エージェント運用に慣れてからの上級パターン

## 配布物（Phase 2 以降）

- `office/` テンプレートリポジトリ（git clone で即運用開始）
- Skills 設定サンプル集
- Hooks レシピ
- Sub-agent 定義集
- 各実例の完全スクリプト・テンプレ・運用手順

## ステータス

**Phase 1（2026-05-10）**: 各章のオリエンテーションを公開。**Phase 2（2026-06 開始）**: 実装の詳細・配布リポジトリを順次追加。
