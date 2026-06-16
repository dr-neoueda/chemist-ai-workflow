---
title: MCP サーバー連携
description: ナレッジベース、クラウドストレージ、開発ツールに直接接続
---

MCP（Model Context Protocol）は、Claude Code から外部ツールを呼び出すためのオープンプロトコルです。これを通じて Notion / Google Drive / GitHub / Playwright などにシームレスに接続できます。

## 公式 MCP サーバー（Anthropic 提供）

| サーバー | 用途 |
|---|---|
| **Notion** | ページ作成・更新、DB クエリ、コメント |
| **Google Drive** | ファイル一覧、内容取得、メタデータ |
| **GitHub** | Issue / PR / Discussion 操作、コード検索 |
| **Playwright** | ブラウザ自動操作（Web QA / E2E） |
| **Memory** | 永続化メモリ（オプション） |
| **Filesystem** | 任意ディレクトリの read/write |

## コミュニティ MCP サーバー

| 用途 | 例 |
|---|---|
| クラウドストレージ | Dropbox MCP, OneDrive MCP |
| データベース | PostgreSQL MCP, SQLite MCP |
| API | OpenAI MCP, Slack MCP, Linear MCP, Jira MCP |
| 化学（カスタム） | NMR ピーク自動アサイン、PXRD reduce など自前構築 |

## セットアップ例（Notion）

`settings.json` または `~/.claude.json`：

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-notion"],
      "env": { "NOTION_TOKEN": "..." }
    }
  }
}
```

セットアップ後、Claude Code セッション内で MCP ツールがそのまま使える状態になります（`mcp__notion__notion-create-pages` など）。

## 化学プロジェクトでの活用例

1. **論文 DB 自動更新**: Notion MCP で paper-register skill が PDF メタデータを直接登録（[応用例](/claude-code/application/)で詳述）
2. **PXRD データ解析**: Filesystem MCP で計算結果ディレクトリを読み込み、Python で解析
3. **HPC ジョブ監視**: SSH 経由（カスタム MCP）で `qstat` の結果を Claude が直接読む
4. **ブラウザ自動化**: Playwright MCP で論文 DB（PubChem / CCDC など）から構造データを自動取得
5. **Web 動作確認**: 本サイトのような Astro Starlight ドキュメントを Playwright MCP で自動 QA

## カスタム MCP サーバー

自前のデータソースを Claude から使えるようにしたい場合、TypeScript / Python で MCP サーバーを実装可能です。例えば：

- ラボ内 NMR データベース
- 計算ジョブの SQL 履歴 DB
- 結晶構造ローカルアーカイブ

## 対応マトリクス

各ツールの API / MCP 成熟度（特にナレッジベースとクラウドストレージ）は [対応ツール一覧](/tools/) を参照。

## 次のステップ

- [office/ 部署テンプレート](/claude-code/company-template/)
- [応用：化学研究での実例](/claude-code/application/)
