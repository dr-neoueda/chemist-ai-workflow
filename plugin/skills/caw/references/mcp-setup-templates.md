# MCP セットアップテンプレート集

`/caw` のオンボーディング Step 3 で、Q3（ナレッジベース）/ Q4（クラウドストレージ）の選択に応じて `office/.mcp-setup.md` を生成するためのテンプレート。

MCP（Model Context Protocol）サーバを設定すると、caw の各部署が Notion / Google Drive / Gmail などの外部サービスに直接アクセスできる。**API key を含むため `office/.mcp-setup.md` は手順書であって認証情報そのものは置かない**。認証情報は環境変数または各 CLI の設定ファイルで管理する。

---

## `office/.mcp-setup.md` のヘッダ（共通）

````markdown
# MCP セットアップ手順

このプロジェクトの caw 部署が使う MCP サーバの設定手順。
オンボーディングで選択したナレッジベース / クラウドストレージに応じて生成。

## 重要な原則

- ❌ API key を **この .mcp-setup.md にもコミット対象ファイルにも直接書かない**
- ✅ API key は環境変数（`~/.zshrc` / `~/.bashrc`）または各 CLI の設定ファイルへ
- ✅ 各 MCP サーバの権限スコープは **最小限**に（read-only で済むものは read-only）
- ✅ `office/.mcp-setup.md` 自体は手順書なので commit して良い（鍵を書かない限り）

## セットアップ状況

- [ ] ナレッジベース MCP
- [ ] クラウドストレージ MCP
- [ ] 動作確認

---
````

以下、Q3 / Q4 の選択に応じて該当セクションを `office/.mcp-setup.md` に追記する。

---

## ナレッジベース MCP（Q3 の回答に応じて）

### Q3 = Notion

````markdown
## Notion MCP

### 1. Integration を作成

1. https://www.notion.so/my-integrations で新しい integration を作成
2. 必要な capability を選択（Read content / Update content / Insert content）
3. Internal Integration Secret（`ntn_...` または `secret_...`）をコピー

### 2. 対象 DB に integration を接続

文献 DB（Paper DB）や ToDo DB のページで「...」→「Connections」→ 作成した integration を追加

### 3. 環境変数を設定

```bash
# ~/.zshrc または ~/.bashrc
export NOTION_API_KEY="ntn_..."   # ← 実際の鍵に置換（このファイルには書かない）
```

### 4. Claude Code に MCP サーバを登録

```bash
claude mcp add notion --env NOTION_API_KEY=$NOTION_API_KEY \
  -- npx -y @notionhq/notion-mcp-server
```

### 5. 動作確認

```
claude
> Notion の Paper DB に登録されている最近 5 件の論文を一覧して
```

### caw との連携

- research 部署が `work/papers/<author-year>.md` を生成 → Notion Paper DB に同期
- 秘書部の TODO ⇄ Notion ToDo DB の双方向同期
- データソース ID は `office/CLAUDE.md` の「オーナープロフィール」付近にメモしておくと再利用しやすい
````

### Q3 = Obsidian

````markdown
## Obsidian MCP

Obsidian はローカルの vault（Markdown ファイル群）。MCP サーバ経由か、Filesystem MCP で直接アクセスする。

### オプション A: obsidian-mcp（コミュニティ実装）

```bash
claude mcp add obsidian -- npx -y obsidian-mcp /path/to/your/vault
```

### オプション B: Filesystem MCP（vault ディレクトリを直接読み書き）

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/your/vault
```

### caw との連携

- research 部署が生成した `work/papers/<author-year>.md` を vault にコピー（frontmatter 付き）
- vault パスは `office/CLAUDE.md` にメモしておく
````

### Q3 = Logseq

````markdown
## Logseq 連携

Logseq は専用 MCP の成熟度が低いため、Filesystem MCP 経由でグラフディレクトリにアクセスする運用を推奨。

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/logseq/graph
```

- research 部署の出力は `pages/` または `journals/` に frontmatter 付き Markdown で保存
````

### Q3 = 使わない / まだ決めていない

````markdown
## ナレッジベース未設定

現状ナレッジベース連携は無効。`work/papers/`（md）・`work/topics/`（HTML）にローカル蓄積される。

後でナレッジベースを決めたら `/caw` で再度この手順を生成できる。
````

---

## クラウドストレージ MCP（Q4 の回答に応じて）

### Q4 = Google Drive

````markdown
## Google Drive MCP

### 1. Google Cloud プロジェクトと OAuth クライアント

1. https://console.cloud.google.com/ でプロジェクトを作成（既存でも可）
2. 「APIとサービス」→ Google Drive API を有効化
3. OAuth 2.0 クライアント ID を作成（デスクトップアプリ）
4. クライアント JSON をダウンロード → `~/.config/google-drive-creds.json` に保存

### 2. 環境変数を設定

```bash
# ~/.zshrc または ~/.bashrc
export GOOGLE_CREDENTIALS_PATH="$HOME/.config/google-drive-creds.json"
```

### 3. Claude Code に MCP サーバを登録

```bash
claude mcp add google-drive --env GOOGLE_CREDENTIALS_PATH=$GOOGLE_CREDENTIALS_PATH \
  -- npx -y @modelcontextprotocol/server-google-drive
```

初回起動時にブラウザで OAuth 認証フローが走る。

### caw との連携

- research 部署が `work/papers/` の PDF を Drive にアップロード → 共有 URL を md の `pdf_url` に書き戻し
- analysis 部署の大きな結果ファイルを Drive に退避
````

### Q4 = Dropbox

````markdown
## Dropbox 連携

専用 MCP の成熟度が低いため、ローカル同期フォルダ + Filesystem MCP 経由を推奨。

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem "$HOME/Dropbox/research"
```

- Dropbox デスクトップアプリでローカル同期 → caw は普通のローカルファイルとして読み書き
````

### Q4 = OneDrive

````markdown
## OneDrive 連携

Microsoft Graph API 経由か、ローカル同期フォルダ + Filesystem MCP。研究室が M365 契約なら Graph API が機能豊富。

### 簡易: ローカル同期フォルダ

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem "$HOME/OneDrive/research"
```

### 本格: Microsoft Graph API

M365 サブスク + Azure AD アプリ登録が必要。共著者と OneDrive 上で論文を共同編集する場合に有用（writing 部署の Word 派運用と連携）。
````

### Q4 = 使わない / ローカルのみ

````markdown
## クラウドストレージ未設定

現状クラウドストレージ連携は無効。すべてローカルファイルで完結。

後で必要になったら `/caw` で再度この手順を生成できる。
````

---

## 任意追加: Gmail MCP（共著者・指導教員とのやり取り）

オンボーディングでは聞かないが、ユーザーが「メールも連携したい」と言った場合に追記する。

````markdown
## Gmail MCP（任意）

```bash
# Google Cloud で Gmail API を有効化、OAuth クライアントを作成後
claude mcp add gmail --env GOOGLE_CREDENTIALS_PATH=$HOME/.config/gmail-creds.json \
  -- npx -y @modelcontextprotocol/server-gmail
```

### caw との連携

- writing 部署が `office/secretary/notes/<today>-decisions.md` を元に共著者宛ての進捗メール下書きを生成 → Drafts に保存（送信は手動確認）
- ⚠️ 送信権限は付けず、下書き作成権限のみに絞ることを推奨
````

---

## Codex CLI を併用する場合

Codex CLI も同じ MCP サーバを使えるが、設定ファイルは別管理：

- Claude Code: `claude mcp add ...`（`~/.claude.json` 等）
- Codex CLI: `codex mcp add ...` または `~/.codex/config.toml` の `[mcp_servers]` セクション

```toml
# ~/.codex/config.toml
[mcp_servers.notion]
command = "npx"
args = ["-y", "@notionhq/notion-mcp-server"]
env = { NOTION_API_KEY = "${NOTION_API_KEY}" }
```

**環境変数（`NOTION_API_KEY` 等）を `~/.zshrc` に置けば、両 CLI から同じ鍵を参照でき、二重管理を避けられる。**

---

## セットアップテンプレートの運用ルール

- `office/.mcp-setup.md` は **手順書**。実際の API key は絶対に書かない（環境変数経由）
- `office/.mcp-setup.md` は git commit して良い（鍵を書かない限り、チームで手順を共有できる）
- caw は Step 3 で Q3 / Q4 の回答に該当するセクションだけを抜粋して `office/.mcp-setup.md` を生成する
- 「使わない」を選んだ項目も、未設定セクションを入れておく（後から再生成しやすい）
- ユーザーが後でナレッジベース / クラウドストレージを決めた場合、`/caw` で「MCP セットアップを生成して」と言えば再生成できる
