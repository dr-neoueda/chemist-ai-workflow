---
title: Hooks
description: SessionStart / PreToolUse / PostToolUse / Stop で自動化を仕込む
---

Hooks はセッションのライフサイクルに介入する shell コマンド群です。Claude が見えない場所で**決定的に**走るので、品質ゲートや自動化に最適です。

## 4 つの主要 Hook

| Hook | 発火タイミング | 用途 |
|---|---|---|
| **SessionStart** | セッション開始時 | コンテキスト自動注入、過去ノート読み込み |
| **PreToolUse** | ツール実行前 | パラメータ検証、実行可否判定 |
| **PostToolUse** | ツール実行後 | 自動 lint、自動レビュー、ログ記録 |
| **Stop** | セッション終了時 | サマリ保存、未完了 TODO エスカレート |

## SessionStart：自動コンテキスト注入

`settings.json`：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "cat ~/lab/office/secretary/notes/$(date +%F)*.md 2>/dev/null | head -50"
          }
        ]
      }
    ]
  }
}
```

毎セッション開始時に「今日の意思決定ログ」が自動でコンテキストに入ります。著者環境は `claude-mem` 風の自動ノート注入を SessionStart で実装しています。

## PreToolUse：品質ゲート（Fact-Forcing Gate 風）

Claude が安易にファイルを変更する前に「呼び出し元を grep する」「テストを実行する」を強制する hook を仕込めます：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "scripts/fact-check.sh" }
        ]
      }
    ]
  }
}
```

`fact-check.sh` が non-zero exit すれば Edit / Write がブロックされます。Claude にとっては「実行前に事実を提示しないと進めない」というゲートになります。

## PostToolUse：自動レビュー

`.py` Edit / Write 直後に Claude python-reviewer + Codex review の二段ループを自動起動：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "scripts/pr-loop.sh '$file_path'" }
        ]
      }
    ]
  }
}
```

化学プロジェクトでは数値計算スクリプトの品質保証に必須の仕組みです。

## Stop：セッション終了時のサマリ自動保存

```json
{
  "hooks": {
    "Stop": [
      { "type": "command", "command": "scripts/save-session-summary.sh" }
    ]
  }
}
```

未完了 TODO のエスカレート、学びの自動抽出（learn skill 起動）などに使えます。

## 化学プロジェクトでの活用例

- **計算ジョブ submission 前**: 入力ファイルの cell parameter / charge / multiplicity を validate
- **Python Edit 後**: PR ループ（python-review → codex:review）を自動起動
- **Stop**: セッションの学びを `notes/learnings.md` に自動 append

## ベストプラクティス

- Hook は **失敗しても明確なメッセージを返す**（Claude が何故ブロックされたか分かる形に）
- Bash スクリプトは shellcheck で検証
- Hook の実行は決定的に保つ（タイムアウト・stochastic な処理は避ける）
- 過剰な Hook は session 開始を遅くするので、本当に必要なものに絞る

## 次のステップ

- [Sub-agents](/claude-code/subagents/) — Hooks の効果を並行実行で増幅
- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — AI エージェント運用に慣れてきたら、PostToolUse hook と組み合わせる上級パターン
