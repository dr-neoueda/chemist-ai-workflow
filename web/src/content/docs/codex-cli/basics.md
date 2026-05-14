---
title: 設定の階層と基礎
description: Codex CLI の `~/.codex/` 構造、`config.toml` の書き方、プロジェクト信頼レベル、モデルと思考レベルの選択
---

Codex CLI を効率的に使うには、設定がどこに保存され、どう優先されるかを理解しておく必要があります。本ページでは `~/.codex/` ディレクトリの構造、`config.toml` の書き方、プロジェクト単位の信頼管理、モデル切替までを通します。

## `~/.codex/` の構造

Codex CLI はユーザーホームの `~/.codex/` 配下に状態を保持します。

```
~/.codex/
├── config.toml         ← グローバル設定（モデル / プロジェクト信頼 / sandbox）
├── auth.json           ← OpenAI 認証情報
├── memories/           ← 永続メモリ
├── sessions/           ← セッション履歴（`codex resume` で参照）
├── shell_snapshots/    ← shell 環境スナップショット
├── rules/              ← ユーザーレベルのルール（プロジェクト横断）
├── skills/             ← ユーザーレベルのスキル
│   └── .system/        ← Codex 同梱のシステムスキル
├── plugins/
│   ├── cache/          ← インストール済みプラグインのキャッシュ
│   └── marketplaces/   ← マーケットプレイス登録
├── log/                ← セッションログ
└── cache/              ← 一時キャッシュ
```

プロジェクト固有のルールは `~/.codex/` ではなく、各プロジェクトの `AGENTS.md` に書きます。詳細は [`AGENTS.md` の書き方](/codex-cli/agents-md/)。

## `config.toml` — グローバル設定

`~/.codex/config.toml` がメインの設定ファイル。TOML 形式で記述します。

### 最小例

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"
```

### よく使うキー

| キー | 値の例 | 説明 |
|---|---|---|
| `model` | `"gpt-5.5"` / `"gpt-5"` / `"o3"` | デフォルトモデル |
| `model_reasoning_effort` | `"low"` / `"medium"` / `"high"` | 思考レベル（タスクに応じて切替推奨） |
| `sandbox_permissions` | `["disk-full-read-access"]` | sandbox 実行時の許可設定 |
| `[features]` | サブテーブル | 機能フラグの有効化 / 無効化 |

### プロジェクト信頼レベル

`[projects."<absolute-path>"]` セクションでプロジェクトごとの信頼レベルを設定できます。

```toml
[projects."/Users/neoueda/lab"]
trust_level = "trusted"

[projects."/Users/neoueda/Desktop/PythonPractice"]
trust_level = "trusted"
```

- `trusted` — sandbox なしで自由に実行可能
- 未設定 — sandbox 内で実行、危険操作はプロンプト

研究プロジェクトの作業ディレクトリは `trusted` にしておくと、ジョブスクリプト実行や大量の I/O がスムーズです。

## モデルと思考レベルの切替

Codex CLI は **モデル**と**思考レベル**の 2 軸で挙動を調整できます。

### モデル選択（`model` キー）

| モデル | 用途 |
|---|---|
| **GPT-5.5** | 日常のコーディング・執筆（バランス型、デフォルト推奨） |
| **GPT-5** | 大規模リファクタや research、よりクリエイティブな出力 |
| **o3 系** | 複雑な論理推論・数式・アルゴリズム設計 |

セッション中の切替は `-c model="gpt-5"` のように config override で可能。

```bash
codex -c model="gpt-5" -c model_reasoning_effort="high"
```

### 思考レベル（`model_reasoning_effort` キー）

| レベル | 性質 | 化学プロジェクトでの使い分け例 |
|---|---|---|
| **low** | 速く軽く | バッチ処理・繰り返しタスク・テンプレ生成 |
| **medium** | バランス（デフォルト） | 計算入力ファイル生成・log 解析・通常の対話 |
| **high** | 深く考える | 複雑な実験設計の議論・難しいデバッグ・申請書の論理構成 |

タスクの複雑さに応じて使い分けることでコストと品質のバランスが取れます。

## 認証と再認証

```bash
codex login    # ブラウザで OpenAI アカウントにログイン
codex logout   # 認証情報を破棄
```

`auth.json` に保存される認証情報は機密。Git で誤って commit しないよう、`.gitignore` に `.codex/auth.json` を追加することを推奨。

## 機能フラグ

新機能のオプトインは `[features]` で行います。

```toml
[features]
foo = true
bar = false
```

セッション単位で切替したい場合は CLI フラグ：

```bash
codex --enable foo --disable bar
```

利用可能なフラグは `codex features` で確認できます（実験的機能を含む）。

## サンドボックス（`codex sandbox`）

sandbox サブコマンドで隔離環境内のコマンド実行が可能。

```bash
codex sandbox -- some-command
```

化学計算系では、HPC ジョブスクリプトのドライランや、信頼性の低い外部スクリプトの試験実行に使えます。

## セッション管理

| コマンド | 用途 |
|---|---|
| `codex resume` | 過去セッションを picker で選んで再開 |
| `codex resume --last` | 直近セッションを継続 |
| `codex fork` | 過去セッションを分岐して新規再開 |
| `codex sessions` | セッション一覧 |

長い研究 thread を翌日に持ち越す際、`codex resume` で文脈ごと復帰できます。

## 設定の優先順位

設定は以下の優先順位で解決されます（上位が下位を上書き）：

1. **CLI フラグ**（`-c model="..."` 等）
2. **環境変数**（特定のキーのみ）
3. **`~/.codex/config.toml`** グローバル設定
4. **デフォルト値**

セッションごとに微調整したい設定は CLI フラグで、恒久的な設定は `config.toml` に書きます。

## 推奨初期設定（化学研究者向け）

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"

[projects."/Users/<USER>/lab"]
trust_level = "trusted"
```

`high` 思考レベルを既定にしておくと、計算手法の議論や log 解析で深く考えてもらえます。コスト最適化したい場合は medium に下げ、軽作業ではセッション内で `low` に切替。

## 次のステップ

- [`AGENTS.md` の書き方](/codex-cli/agents-md/) — プロジェクト単位のルール記述
- [Skills](/codex-cli/skills/) — 機能拡張の主軸
- [Commands](/codex-cli/commands/) — スラッシュコマンドの作り方
