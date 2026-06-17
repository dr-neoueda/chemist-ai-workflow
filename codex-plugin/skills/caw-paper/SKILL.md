---
name: caw-paper
description: >
  関心テーマの論文検索・書誌情報整理、入手済み PDF からのメタデータ抽出と
  ナレッジベース + クラウドストレージへの自動登録、要約・タグ付け・引用整理までを一貫運用するスキル。
---

# caw-paper — 情報の収集と管理

## いつ使うか

- 論文検索・PDF 登録・書誌整理を依頼されたとき
- `work/papers/` に PDF を置いてユーザーが「論文を登録して」「PDF を取り込んで」と言ったとき
- ユーザーが「○○ について論文を 100 件集めて」「関心テーマの論文を検索して」と言ったとき
- 既存の `work/papers/` に書誌情報を追加したいとき

`office/research/` が存在しない場合、ユーザーに caw で research 部署を追加することを促す。

---

## はじめてモードを尊重する

このスキルを実行する前に `office/AGENTS.md`（Claude Code では `CLAUDE.md`）を読み、冒頭に `> 運用モード: はじめて` があれば、`caw` skill の「はじめてモードの挙動」を全応答に適用する：**平易な日本語**で話し、専門用語（化学・計算手法・書誌の用語）は初出で 1 行説明を添え、各ステップの最後に**「次はこれをしましょう」を 1 つ**だけ提示する。元に戻せない操作（削除・上書き・外部登録・送信）は必ず事前確認する。

## モード A: 論文検索（書誌情報を一括収集）

### 入力

- 検索テーマ（例: "MOF-based luminescence", "mechanochromism in single crystals"）
- 件数指定（デフォルト 50 件、最大 100 件程度）
- 期間 / ジャーナル絞り込み（任意）

### 検索ソース

利用可能な API・MCP サーバを優先順位で組み合わせる：

1. **arXiv API**（preprint、識別子: arXiv ID）
2. **Crossref API**（DOI lookup、書誌情報の最終確認に有用）
3. **Semantic Scholar API**（引用ネットワーク、分野横断）
4. **OpenAlex API**（大規模文献データベース、無料）
5. **PubMed API**（生命科学・医薬分野）
6. **WebFetch / Exa**（上記で拾えない場合の web 検索フォールバック）

### 出力先

`work/topics/<topic-slug>.md` を生成。フォーマット：

```markdown
---
topic: <topic name>
created: YYYY-MM-DD
sources: [arxiv, crossref, semantic-scholar, ...]
count: <件数>
---

# <Topic Name>

## 検索条件

- キーワード: ...
- 期間: ...
- ジャーナル絞り込み: ...

## 論文リスト

| # | Title | Authors | Year | Journal | ID | 要約（1-2 文） |
|---|---|---|---|---|---|---|
| 1 | ... | ... | 2024 | J. Am. Chem. Soc. | DOI: 10.1021/... | ... |
| 2 | ... | ... | 2023 | arXiv | arXiv:2304.12345 | ... |
| 3 | ... | ... | 2022 | Nature Comm. | DOI: 10.1038/... | ... |
```

ユーザーが PDF を取得したい論文を選定 → モード B（登録）へ進む。

---

## モード B: PDF 登録（入手済み PDF → ナレッジベース）

### 前提

- `work/papers/` ディレクトリに対象 PDF が配置されている（caw scaffold で自動生成済）
- `office/AGENTS.md` の「オーナープロフィール」で **ナレッジベース** と **クラウドストレージ** が指定されている

### Step 1: PDF の検出

```bash
ls work/papers/*.pdf
```

新規追加された PDF を検出（既に `work/papers/` に登録済の md と照合してスキップ）。

### Step 2: メタデータ抽出

各 PDF について：

1. **`pdftotext` でテキスト変換**：`pdftotext "work/papers/<file>.pdf" /tmp/<file>.txt`
2. **頭 2 ページから抽出**：
   - title
   - authors（全員）
   - year
   - journal / volume / pages
   - doi
3. **要約セクション + 結論セクションを LLM で読み取り**：3-5 行の要約を生成
4. **タグ付け**：研究分野、手法、対象系（化合物・現象）から 5-10 個

### Step 3: ナレッジベース用 md 生成

`work/papers/<author-year-keyword>.md` に書誌情報付き md を生成。命名規則：
- `<first-author-lastname>-<year>-<keyword>.md`
- 例: `tanaka-2024-mof-luminescence.md`

フォーマット：

```markdown
---
title: "..."
authors:
  - "First Author"
  - "Second Author"
year: 2024
journal: "..."
volume: ...
pages: "..."
doi: "10.1021/..."
url: "https://doi.org/..."
pdf_local: "work/papers/<file>.pdf"
pdf_url: "TBD"
tags:
  - tag1
  - tag2
added: YYYY-MM-DD
status: "to-read"
---

# <Title>

## 書誌情報

- 著者: ...
- 掲載: ...
- DOI: ...

## 要旨

（3-5 行で要約）

## 主要数式・物性値

（あれば）

## 結論（暫定）

（読了後に追記）

## ネクストアクション

- [ ] 読了
- [ ] 関連論文との比較
- [ ] 引用候補としてマーク

## 関連メモ

（壁打ちの結果や追加調査メモ）

## 関連部署

- 文献部: `../`
- ナレッジベース: <ナレッジベース名>
- クラウドストレージ: <クラウドストレージ名>
```

### Step 4: ナレッジベースへの登録（オプション）

ユーザープロファイルの「ナレッジベース」設定に応じて：

#### Notion の場合

- MCP `notion-create-pages` を使用（権限がある場合）
- データソース ID をユーザーから取得（`office/AGENTS.md` に保存されていれば使用、無ければ問い合わせ）
- frontmatter のフィールドを Notion プロパティにマッピング

#### Obsidian の場合

- MCP `obsidian-append-content` を使用、または vault パスをユーザーから取得して直接書き込み
- frontmatter をそのまま保持（Obsidian は YAML frontmatter ネイティブ対応）

#### Logseq / 他

- frontmatter 付き md ファイルをユーザー指定の vault ディレクトリにコピー

#### 「使わない / 未定」の場合

- `work/papers/` 配下のローカル md のみで完結
- 将来的な KB 連携のため frontmatter は維持

### Step 5: クラウドストレージへのアップロード（オプション）

「クラウドストレージ」設定に応じて：

#### Google Drive

- MCP `google-drive-create-file` を使用
- アップロード後の URL を取得し、登録済 md の `pdf_url` を実 URL に更新

#### Dropbox / OneDrive

- 現状は手動アップロードを促す（自動化は将来対応）

#### 「使わない / ローカルのみ」

- スキップ

### Step 6: 登録レポート

完了後、以下をユーザーに報告：

```
登録完了：

| ファイル | 登録先 md | KB 登録 | クラウドアップロード |
|---|---|---|---|
| paper1.pdf | tanaka-2024-mof.md | ✅ Notion | ✅ Drive |
| paper2.pdf | yamada-2023-xrd.md | ✅ Notion | ⏳ 手動アップロード待ち |

スキップ件数: 2 件（既登録）
失敗件数: 0 件
```

---

## モード C: バッチ処理（複数 PDF 一括）

バッチ処理（複数 PDF 一括登録）を依頼された場合：

- `work/papers/` 配下の全 PDF を対象に Step 1〜6 を順次実行
- 1 ファイルあたり 30-60 秒程度を想定（PDF サイズによる）
- 進捗を逐次表示（"3/10 件処理中..."）
- 失敗ファイルはスキップして続行、最後にまとめて報告

---

## 重要な注意事項

- **既存ファイルは絶対に上書きしない**。同名 md があれば skip して報告
- **PDF 自動ダウンロード機能は未対応**（モード A の検索結果から、ユーザーが手動で PDF を取得する前提）
- **メタデータ抽出の精度**：pdftotext で読めない PDF（画像 PDF・OCR 未処理）は、ファイル名から推定 + ユーザーに確認を求める
- **化学物質名・反応名の正確性**：自動タグ付けは初期案として提示、ユーザーに確認・修正の機会を与える
- **大容量 PDF（>100 MB）**：pdftotext で頭 10 ページのみ抽出、フォールバック処理
- **DOI 重複チェック**：同じ DOI の論文を 2 回登録しないよう、frontmatter の `doi` フィールドで照合
