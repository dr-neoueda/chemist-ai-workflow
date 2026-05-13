---
title: Sub-agents
description: 特化エージェントの並行実行と役割分担
---

Sub-agent はメインの Claude セッションから独立した子エージェントを起動する仕組みです。並行実行・役割分担に使います。

## 主な使い道

1. **並行レビュー**: Claude python-reviewer と Codex review を同時起動 → 構文 / 物理意味論を別々の観点でチェック
2. **重い調査の隔離**: コードベース全体の検索を子エージェントに任せて、メインの context を汚さない
3. **役割固定**: planner / TDD / build-error-resolver など、用途別に専用エージェント

## Agent 定義

`~/.claude/agents/python-reviewer.md`：

```md
---
name: python-reviewer
description: PEP 8 / 型ヒント / pythonic / セキュリティをチェック
tools: Read, Grep, Glob, Bash
---

# Python Reviewer

以下を厳格にチェック：
- PEP 8 準拠
- 型ヒント有無
- セキュリティ脆弱性
- DRY 違反
- ...
```

メインセッションから `Task(subagent_type="python-reviewer", prompt="...")` で発火。

## 化学プロジェクトでの活用例

| シーン | 使い方 |
|---|---|
| 文献紹介スライド作成 | スライド生成 agent と論文要約 agent を並行 |
| 計算ジョブ管理 | 入力生成 agent と log 解析 agent を別ターミナルで同時実行 |
| Codex 委譲（プレゼン） | Claude が source 設計、Codex が実装、それぞれ独立セッション |
| ペーパーレビュー | python-reviewer + codex review を 2 並列で意見を集約 |

## ベストプラクティス

- **並行に走らせるなら独立した task** にする（依存関係があるなら sequential）
- メイン context が膨らみすぎる前に search を委譲する
- Agent ごとに明確な「役割」を frontmatter に書く
- 結果は記録ファイル（`code-reviews/`, `analysis/results/` など）に集約してメインに渡す

## Sub-agent vs Skill vs Hook

3 つの仕組みは似ているが目的が違う：

| 仕組み | 目的 |
|---|---|
| **Skill** | 再利用可能な手順をスラッシュコマンド化（手動 / 自動発火） |
| **Hook** | ライフサイクル介入（決定的・shell ベース） |
| **Sub-agent** | 並行 / 独立した推論を別 context で実行 |

## 次のステップ

- [MCP サーバー連携](/claude-code/mcp/)
- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — AI エージェント運用に慣れてからの上級パターン
