---
title: アンインストールと環境リセット
description: Codex CLI から raw プラグインを完全に除去する手順、最新版への更新、office/ 部署システムのリセット方法
---

raw を「一度も入れたことがない状態」に戻したり、`office/` 部署システムを作り直したりする手順をまとめます。**初期化できることは、テスト・トラブル対応・人に配布する前の動作確認で非常に重要**です。テストユーザーの環境を想定して初期構築を試したいときにも使います。

## 3 種類の「リセット」

raw 周りで「消す・戻す」と言っても、対象が 3 つあります。混同しないよう切り分けます。

| やりたいこと | 対象 | 使う手順 |
|---|---|---|
| raw プラグイン自体を完全に消す | `~/.codex/` 配下のプラグイン実体・設定 | ① raw プラグインのアンインストール |
| 新しいバージョンを試したいだけ | marketplace の再取得 | ② 最新版への更新 |
| プロジェクトの `office/` を作り直す | プロジェクト内の `office/` ディレクトリ | ③ `office/` 環境のリセット |

---

## ① raw プラグインのアンインストール

Codex CLI は **プラグイン単位**と **marketplace 単位**の 2 レベルで管理します。目的に応じて使い分けます。

- `codex plugin remove raw@researcher-ai-workflow` … **raw プラグイン本体だけ**を削除（marketplace 登録は残る）
- `codex plugin marketplace remove researcher-ai-workflow` … **marketplace 登録ごと**削除（配布元の登録を消す）

「raw を一度も入れたことがない状態」に戻すには、両方を実行したうえで残骸を手動削除します。

### Step 1: raw プラグイン本体を削除

```bash
codex plugin remove raw@researcher-ai-workflow
```

raw プラグインがアンインストールされます。**marketplace 登録（researcher-ai-workflow）は残る**ので、`codex plugin add raw@researcher-ai-workflow` だけで入れ直せます。プラグインだけ消したいならここで完了です。

### Step 2: marketplace 登録も削除（完全除去する場合）

```bash
codex plugin marketplace remove researcher-ai-workflow
```

成功すると `Removed marketplace researcher-ai-workflow.` と表示され、`~/.codex/config.toml` から marketplace 設定が消えます。

> marketplace 名が分からない場合は `cat ~/.codex/config.toml` で確認してください（Codex CLI には marketplace 一覧コマンドが無いため、config 直読みが確実）。

### Step 3: 残骸の手動削除

`remove` 後も以下が残ることがあるので、完全除去なら手動で削除します。

**3-1. config.toml の有効化設定**

`~/.codex/config.toml` に以下のブロックが残っていたら、この 2 行を削除してください。

```toml
[plugins."raw@researcher-ai-workflow"]
enabled = true
```

**3-2. キャッシュ・clone 実体**

```bash
rm -rf ~/.codex/plugins/cache/researcher-ai-workflow
rm -rf ~/.codex/marketplaces/researcher-ai-workflow
rm -rf ~/.codex/.tmp/marketplaces/.staging/marketplace-add-*
```

- `plugins/cache/` — インストール済みプラグインのキャッシュ実体
- `marketplaces/` — clone した marketplace リポジトリ
- `.tmp/marketplaces/.staging/` — `add` 操作時の中断 staging 残骸（temp）

### Step 4: 完全除去の確認

```bash
find ~/.codex -iname '*researcher-ai-workflow*' -o -iname '*chemist-ai-workflow*'
grep -rnE "researcher-ai-workflow|chemist-ai-workflow" ~/.codex/config.toml
```

どちらも何も出なければ「raw（旧名 caw を含む）を一度も入れたことがない環境」と同じ状態です。新旧どちらのマーケットプレイス名も探します。

> `config.toml` に `[projects."/Users/.../raw-test/..."]` のような行がヒットすることがありますが、これは **パス名に "raw" を含むプロジェクトの trust 設定**であって raw プラグインの足跡ではありません。無害なので放置で構いません（消したい場合は該当ブロックを削除）。

---

## ② 最新版への更新（アンインストール不要）

新しいバージョンを試すだけなら、削除せず `upgrade` で済みます。

```bash
codex plugin marketplace upgrade researcher-ai-workflow
```

GitHub から再取得して最新版に更新されます。**アンインストール → 再インストールよりこちらが手早い**です。クリーンに入れ直したい場合のみ ① の手順を使います。

再インストールは ① で完全除去したあと、改めて 2 ステップで：

```bash
codex plugin marketplace add dr-neoueda/researcher-ai-workflow
codex plugin add raw@researcher-ai-workflow
```

---

## ③ `office/` 環境のリセット

プラグインは残したまま、特定プロジェクトの `office/` 部署システムだけを作り直したい場合の手順です。

### 事前確認（任意）

削除前に `raw-doctor` で構造を点検しておくと、何が入っているか把握できます。

```bash
cd ~/your-research-project
codex
> raw-doctor
```

### リセット

```bash
# office/ を削除
rm -rf office/

# 再スキャフォールド（オンボーディングが再度走る）
codex
> raw
```

### ⚠️ 注意

- `office/` には **TODO・意思決定ログ・学び・Playbook** など蓄積した運営情報が入っています。削除すると失われます。残したい場合は事前にバックアップ（`cp -r office office.bak` など）を取ってください
- **成果物**（`work/papers/` `slides/` `work/manuscripts/` など project root 直下のディレクトリ）は `office/` の外にあるため、`rm -rf office/` では削除されません。これは [成果物配置の二層原則](/plugin/) による設計です
- バックアップを取らずに作り直すのは、テスト用の使い捨てプロジェクトなど「中身が消えてよい」場合に限ってください

---

## テストユーザー環境の再現フロー

「raw を初めて入れる人」の体験を確認したいときの典型的な流れ：

```bash
# 1. 完全除去（① の Step 1〜4）
codex plugin remove raw@researcher-ai-workflow
codex plugin marketplace remove researcher-ai-workflow
# config.toml の [plugins."raw@..."] ブロックが残っていれば削除
rm -rf ~/.codex/plugins/cache/researcher-ai-workflow \
       ~/.codex/marketplaces/researcher-ai-workflow \
       ~/.codex/.tmp/marketplaces/.staging/marketplace-add-*

# 2. まっさらな状態から導入（2 ステップ）
codex plugin marketplace add dr-neoueda/researcher-ai-workflow
codex plugin add raw@researcher-ai-workflow

# 3. 新規プロジェクトで初期構築を試す
cd ~/path/to/fresh-test-project
codex
> raw
```

オンボーディング（研究プロファイルの全 8 問ヒアリング）から `office/` 生成までを、配布先のユーザーと同じ条件で確認できます。

## 次のステップ

- [環境構築](/codex-cli/setup/) — インストールと `office/` の初期構築
- [Skills](/codex-cli/skills/) — `raw-doctor` を含む各 Skill の仕様
- [配布プラグイン（raw）](/plugin/) — raw の構成と成果物配置の二層原則
