---
title: MCP サーバー連携
description: Codex CLI の MCP（Model Context Protocol）サーバー連携、Notion / Google Drive / Gmail などへの統合方法
---

MCP（Model Context Protocol）は、AI エージェントが外部サービス（Notion / Google Drive / Gmail / GitHub 等）にアクセスするための標準プロトコル。Codex CLI は MCP サーバーを介してこれらサービスと統合できます。本ページでは MCP の概要、Codex 側の設定、化学研究での活用例を通します。

## MCP とは

MCP は Anthropic が提唱し、現在は OpenAI や他社も採用する **AI エージェント ⇔ 外部ツール** の標準インターフェース。

- **Server**：外部サービス側で動く軽量サーバー（例: Notion MCP サーバーが Notion API をラップ）
- **Client**：エージェント側（Codex CLI / Claude Code）が server を呼び出す
- **プロトコル**：JSON-RPC ベース、stdio または HTTP 経由

化学研究者向けに役立つ MCP サーバーの例：

| サービス | 用途 |
|---|---|
| Notion | 文献 DB、TODO、研究ノート管理 |
| Google Drive | PDF 保管、データ共有 |
| Gmail | 共著者・指導教員とのコミュニケーション |
| GitHub | コード・LP・プラグインの管理 |
| Linear / Jira | プロジェクト管理 |
| Slack | 研究室内コミュニケーション |
| Obsidian | ナレッジベース連携 |
| Context7 | ライブラリドキュメント参照 |

## Codex 側の MCP 管理

```bash
codex mcp --help
```

主要サブコマンド：

| コマンド | 用途 |
|---|---|
| `codex mcp add <server-spec>` | MCP サーバーを登録 |
| `codex mcp list` | 登録済み MCP サーバー一覧 |
| `codex mcp remove <name>` | 登録解除 |

## Notion MCP の例

### 登録

```bash
codex mcp add notion --command "npx -y @notionhq/notion-mcp-server" --env NOTION_API_KEY=secret_...
```

または config.toml の `[mcp.servers]` テーブルに記述：

```toml
[mcp.servers.notion]
command = "npx"
args = ["-y", "@notionhq/notion-mcp-server"]
env = { NOTION_API_KEY = "secret_..." }
```

### 利用

セッション内で：

```
codex
> Notion の Paper DB に登録されている最近 5 件の論文を一覧して
```

Codex は MCP 経由で Notion API を呼び出し、結果を返します。

## Google Drive MCP の例

```toml
[mcp.servers.google-drive]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-google-drive"]
env = { GOOGLE_CREDENTIALS_PATH = "~/.config/google-drive-creds.json" }
```

ユーザー認証は初回起動時にブラウザフローで完了。

## 化学研究での MCP 活用パターン

### パターン 1: 論文 PDF パイプライン

```
papers/<file>.pdf
     ↓ pdftotext + メタデータ抽出
papers/<author-year>.md
     ↓ Notion MCP
Notion Paper DB（タグ・要約・引用 ID 付き）
     ↓ Google Drive MCP
Google Drive にアップロード、URL を Notion ページの pdf_url に書き戻し
```

caw プラグインの `/caw-paper` スキル（Claude Code 版 v1.1.0）がこのパイプラインを実装。Codex 版でも同じワークフローを Skills として書けます。

### パターン 2: TODO の双方向同期

```
office/secretary/todos/<today>.md  ⇄  Notion ToDo DB（Cabinet）
                                     ⇄  Linear / Jira（オプション）
```

毎朝 `/lab-status` のような Command で同期チェック、差分があれば手動 / 自動マージ。

### パターン 3: 計算結果の即時共有

```
HPC で計算完了 → ローカルに log 取得
     ↓ caw-playbook で解析
office/computation/playbooks/<tool>.md に Lessons Learned 追記
     ↓ Slack MCP
研究室の #computation チャンネルに「benzene Opt 完了 / 22 step 収束」と自動 post
```

非同期コミュニケーションを最小コストで実現。

### パターン 4: 共同研究者とのメール下書き

```
office/secretary/notes/<today>-decisions.md（今日の決定事項）
     ↓ AGENTS.md ガイドライン参照
     ↓ Gmail MCP
共著者宛ての進捗メール下書きを生成 → Drafts に保存（送信は手動確認）
```

### パターン 5: ライブラリドキュメント参照

```
RDKit / ASE / MDAnalysis / pymatgen の API 確認
     ↓ Context7 MCP
最新の docs と code 例を fetch
     ↓
正確な引数 / 戻り値を踏まえてコード生成
```

ハルシネーション（存在しない API の呼び出し）を抑制する効果あり。

## セキュリティと信頼

MCP サーバーは **外部サービスへの認証情報を保持**します。注意点：

### Do

- ✅ `~/.codex/config.toml` を `.gitignore` に追加（auth 情報を含む可能性）
- ✅ API key は環境変数経由で渡す（config.toml に直書きしない）
- ✅ 各 MCP サーバーの権限スコープを最小に絞る（read-only で済むものは read-only に）

### Don't

- ❌ MCP サーバーの設定を public repo に commit
- ❌ 信頼できないソース由来の MCP サーバーをインストール
- ❌ 全権限を持つ管理者用 API key を MCP に渡す

## Claude Code との関係

Claude Code も同じ MCP プロトコルをサポートします。同じ MCP サーバー（例: Notion）を Claude Code と Codex CLI の両方で使えますが、認証情報は別管理：

- Claude Code: `~/.claude/mcp-config.json` 等
- Codex CLI: `~/.codex/config.toml` の `[mcp.servers]` セクション

研究室で両方の CLI を使う場合、同じ MCP サーバーの設定をそれぞれ管理する手間が出ます。共通の認証情報を環境変数で渡す運用が現実的です：

```bash
# ~/.zshrc
export NOTION_API_KEY="secret_..."
export GOOGLE_CREDENTIALS_PATH="~/.config/google-drive-creds.json"
```

両 CLI から同じ環境変数を参照すれば、設定の二重管理は最小化できます。

## トラブルシューティング

### MCP サーバーが起動しない

```bash
codex mcp list                 # 登録状態確認
codex mcp logs <name>          # サーバーのログ確認（実装ある場合）
```

`command` のパスが正しいか、依存パッケージ（`npx -y` の場合は npm registry へのアクセス）が利用可能かを確認。

### 認証エラー

API key が古い、権限スコープが足りない等。サービス側の管理画面で再発行 / 権限拡張。

### Tool が見えない

セッション起動後、すぐに使おうとして MCP サーバーの connection 完了前に呼び出してしまうケース。数秒待ってからリトライ。

## 次のステップ

- [Skills](/codex-cli/skills/) — MCP を使う Skills の書き方
- [Commands](/codex-cli/commands/) — MCP 連携を伴う Commands の作り方
- [配布プラグイン（caw）](/plugin/) — caw の `/caw-paper` で実装される MCP 統合パイプライン
