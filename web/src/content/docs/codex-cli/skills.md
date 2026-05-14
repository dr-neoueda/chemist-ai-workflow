---
title: Skills
description: Codex CLI の Skills 仕様、`SKILL.md` フォーマット、プラグイン経由配布、caw を実例として
---

Skills は Codex CLI の機能拡張の主軸。プロンプト的なワークフロー指示を分離・再利用可能なモジュールに切り出して、エージェントが必要に応じて自動発火させる仕組みです。本ページでは Skills の構造、書き方、配布までを caw を例に通します。

## Skills の場所と発火

Codex CLI が読む Skills の探索順：

```
~/.codex/skills/                              ← ユーザーレベル
└── .system/                                  ← Codex 同梱のシステムスキル
    ├── skill-creator/SKILL.md
    ├── plugin-creator/SKILL.md
    └── ...

~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/skills/
└── <skill-name>/SKILL.md                     ← プラグイン経由でインストールしたスキル
```

スキルは **自然言語マッチで自動発火** します。ユーザーが「caw を起動」「化学プロジェクトの環境を作って」のように述べると、Codex が登録済みスキルの `description` と照合して該当スキルをロード。

スラッシュ起動（`/caw` 等）は **不要**（むしろ無効、Codex では `/` は明示的コマンド専用）。詳細は [Commands](/codex-cli/commands/) を参照。

## `SKILL.md` の最小フォーマット

```markdown
---
name: my-skill
description: 何をするスキルか、いつ発火すべきかを具体的に書く（description マッチに使われる）
---

# My Skill

## いつ使うか

- ユーザーが「○○」と言ったとき
- ○○の作業が必要なとき

## ワークフロー

1. Step 1: ...
2. Step 2: ...
3. Step 3: ...

## 注意事項

- 既存ファイルは上書きしない
- ...
```

**重要**：`description` フィールドは発火判定の最重要要素。「何をするか」だけでなく「いつ発火すべきか」を具体的に書く。

## caw を実例として

caw プラグイン（`codex-plugin/skills/caw/SKILL.md`）の構造を見てみます。

### Frontmatter

```yaml
---
name: caw
description: >
  化学研究プロジェクトのための AI 部署システム。
  `/caw` で起動し、秘書部から開始。
  研究分野・使う計算ソフト・ナレッジベース等をヒアリングして、
  化学者向けにカスタマイズされた部署 AGENTS.md と Playbook を一括スキャフォールドする。
---
```

ポイント：
- **`name`** はスキルの ID。`caw` のように短く一意な名前
- **`description`** は発火判定に使われる。複数行可、`>` で folded scalar
- description には「caw」「化学研究」「部署」「ヒアリング」「スキャフォールド」など複数のキーワードを含めて、自然言語マッチの hit 率を上げる

### ワークフロー本体

`SKILL.md` の本文はステップバイステップの手順。Codex がスキル発火時にこれを system prompt として読み込み、指示通りに動きます。

caw の場合：
1. **検出**：カレントディレクトリの `.company/` 有無を判定
2. **オンボーディング**：`AskUserQuestion` で研究プロファイル 4 問 + 部署選択
3. **スキャフォールド**：`.company/` 部署 + 作業ディレクトリ + Playbook を一括生成
4. **運営モード**：2 回目以降は秘書を窓口に部署振り分け

詳細は [GitHub の caw SKILL.md](https://github.com/dr-neoueda/chemist-ai-workflow/blob/main/codex-plugin/skills/caw/SKILL.md) を参照。

## References — 補助ファイル

スキルが大きくなる場合、テンプレートやデータを `references/` サブディレクトリに切り出します。

```
skills/caw/
├── SKILL.md                                  ← メインのワークフロー指示
└── references/
    ├── agents-md-template.md                 ← ルート AGENTS.md 生成テンプレ
    ├── chemistry-departments.md              ← 8 部署 AGENTS.md テンプレ集
    └── playbook-starters.md                  ← 計算ソフト Playbook 雛形（6 種類）
```

`SKILL.md` 本文から `references/<file>` を Read tool で必要時にロードする指示を書きます。これで `SKILL.md` 本体は薄く保てる。

## 自作スキルを作る

### 最小手順

```bash
mkdir -p ~/.codex/skills/my-skill
cat > ~/.codex/skills/my-skill/SKILL.md <<'EOF'
---
name: my-skill
description: <発火タイミングを具体的に>
---

# My Skill

## ワークフロー

1. ...
EOF
```

これで Codex を起動すると、自動的にスキルとして認識されます。

### `plugin-creator` スキルを使う

Codex 同梱の `plugin-creator` スキルがスキャフォールドを自動化します：

```
codex
> plugin-creator で新しいスキル作って
```

または：

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/create_basic_plugin.py my-plugin
```

これでプラグイン構造（`.codex-plugin/plugin.json` + `skills/my-plugin/SKILL.md`）が一括生成されます。

## プラグイン経由での配布

複数のスキルや references をまとめて配布する場合、プラグインとしてマーケットプレイス公開します。

### 必要なファイル

```
my-plugin/
├── .codex-plugin/plugin.json                 ← プラグインマニフェスト
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── references/
```

### marketplace.json

リポジトリルートに：

```json
{
  "name": "my-marketplace",
  "interface": { "displayName": "My Marketplace" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": { "source": "local", "path": "./my-plugin" },
      "policy": { "installation": "AVAILABLE", "authentication": "NONE" },
      "category": "Research"
    }
  ]
}
```

このファイルは `<repo-root>/.agents/plugins/marketplace.json` に配置。

### ユーザー側の導入

```bash
codex plugin marketplace add <github-user>/<repo>
codex plugin install <plugin-name>
```

caw を実例にすると：

```bash
codex plugin marketplace add dr-neoueda/chemist-ai-workflow
codex plugin install caw
```

## スキル設計のベストプラクティス

### 単一責任の原則

1 スキル = 1 目的に絞る。caw が肥大化したので Phase 3 で `caw-paper`、`caw-input`、`caw-playbook` に分割した、というように。

### Description は具体的に

❌ 悪い例：
```yaml
description: 論文を扱うスキル
```

✅ 良い例：
```yaml
description: >
  関心テーマの論文を arXiv / Crossref / Semantic Scholar / OpenAlex で検索し、
  入手済み PDF からメタデータを抽出してナレッジベース（Notion / Obsidian / Logseq）と
  クラウドストレージ（Google Drive 等）に自動登録。要約・タグ付け・引用整理まで一貫運用。
```

description が長すぎると context window を圧迫しますが、短すぎると発火条件があいまいになります。**100-300 字を目安**に、複数の発火キーワードを自然に織り込む。

### 既存ファイルへの破壊的変更を避ける

ワークフロー内で必ず：

```markdown
## 重要な注意事項

- 既存ファイルは絶対に上書きしない（同名 md があれば skip）
- 同日のファイルは追記、新規作成しない
```

を明示。スキルは複数回発火する可能性があるため、idempotent な動作が重要。

### Codex vs Claude Code でのスキル設計の違い

| 観点 | Codex 流 | Claude Code 流 |
|---|---|---|
| 発火方法 | 自然言語マッチ（description 主導） | スラッシュ + 自然言語の両方 |
| description の役割 | 最重要（発火判定の核） | 補助的（slash で明示できる） |
| ユーザーが覚えるもの | やりたいこと（目的） | スキル名（手段） |

Codex 向けにスキルを書く場合、description を richer に。

## 既存スキルの確認

ユーザーレベル + プラグイン経由のスキル一覧：

```bash
ls ~/.codex/skills/
ls ~/.codex/plugins/cache/*/*/*/skills/
```

または `codex plugin list` でプラグイン経由の一覧を確認。

## 次のステップ

- [Commands](/codex-cli/commands/) — スキルとは異なるスラッシュコマンドの作り方
- [`AGENTS.md` の書き方](/codex-cli/agents-md/) — スキルに切り出さない、プロジェクト全体ルール
- [配布プラグイン（caw）](/plugin/) — caw のスキル設計を実例として
