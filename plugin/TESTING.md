# caw プラグイン ローカルテスト手順

`~/lab` の環境を汚さずに、`~/caw-test/` 配下の別フォルダで caw プラグインを試すための手順書。

---

## 前提

- 開発中の caw プラグインは `~/lab/spring/chemist-ai-workflow/plugin/` にある
- ローカル marketplace `caw-local` は `~/.claude/plugins/marketplaces/caw-local/` に作成済み
- `~/.claude/plugins/known_marketplaces.json` には `caw-local` 登録済み
- **未完了**: `installed_plugins.json` と `settings.json` への登録（auto モードの自己改変ブロックにより手動対応必須）

---

## Phase 0 — プラグインを Claude Code に有効化する（残作業）

caw プラグインを使えるようにするには、以下のいずれかの方法で「登録 + 有効化」が必要。

### 方法 A（推奨）— `/plugin install` で自動登録

新しい Claude Code セッションを別ターミナル / 別 tmux ウィンドウで開き、以下を実行：

```
/plugin install caw@caw-local
```

これで以下 3 ファイルが自動更新される：
- `~/.claude/plugins/installed_plugins.json` に `caw@caw-local` エントリ追加
- `~/.claude/settings.json` の `enabledPlugins` に `"caw@caw-local": true` 追加
- `~/.claude/settings.json` の `extraKnownMarketplaces` に `caw-local` 追加（既存の場合スキップ）

実行後、`/plugin list` で `caw@caw-local` が表示されれば成功。

### 方法 B — 手動 JSON 編集

エディタで以下を直接編集する（`/plugin install` が使えない、または挙動を完全制御したい場合）。

**1. `~/.claude/plugins/installed_plugins.json`**

既存の JSON に下記エントリを追加：

```json
"caw@caw-local": {
  "marketplace": "caw-local",
  "plugin": "caw",
  "installLocation": "/Users/neoueda/.claude/plugins/cache/caw-local/caw/0.1.0",
  "installedAt": "2026-05-11T00:00:00.000Z",
  "version": "0.1.0"
}
```

**2. `~/.claude/settings.json` の `enabledPlugins` セクション**

```json
"enabledPlugins": {
  ...既存エントリ...,
  "caw@caw-local": true
}
```

**3. `~/.claude/settings.json` の `extraKnownMarketplaces` セクション**

```json
"extraKnownMarketplaces": [
  ...既存エントリ...,
  "caw-local"
]
```

編集後、Claude Code を再起動して `/plugin list` で確認。

### 共通の確認

```bash
ls -la ~/.claude/plugins/cache/caw-local/caw/0.1.0
# → ~/lab/spring/chemist-ai-workflow/plugin/ への symlink になっていること
```

symlink が壊れていたら：

```bash
mkdir -p ~/.claude/plugins/cache/caw-local/caw
ln -sfn ~/lab/spring/chemist-ai-workflow/plugin ~/.claude/plugins/cache/caw-local/caw/0.1.0
```

---

## Phase 1 — テスト用ディレクトリの準備

`~/lab` を汚さないため、ホーム直下に専用ディレクトリを切る。

```bash
mkdir -p ~/caw-test/sample-project-01
cd ~/caw-test/sample-project-01
```

### サンプルプロジェクトの想定

caw の対話的ウィザードを試すために、以下のような架空のプロファイルを用意：

| 項目 | 想定値 |
|---|---|
| 研究分野 | 有機化学・結晶化学（自分の実環境に近い） |
| 計算ソフト | Gaussian + CP2K |
| ナレッジベース | Notion |
| クラウドストレージ | Google Drive |
| 部署構成 | 秘書 + research + computation + writing |

別プロファイルも試したい場合は `sample-project-02`, `sample-project-03` を別途切る。

```bash
mkdir -p ~/caw-test/sample-project-02  # 例: 計算化学者プロファイル（GROMACS + ORCA）
mkdir -p ~/caw-test/sample-project-03  # 例: 文献調査メインプロファイル（Obsidian + Dropbox）
```

各ディレクトリは互いに独立、`/caw` を実行するたびに別の構成が生成される。

---

## Phase 2 — Claude Code セッション起動

このセッション（`~/lab` で動いている方）を**閉じずに**、別ターミナル / 別 tmux ウィンドウで：

```bash
cd ~/caw-test/sample-project-01
claude
```

新セッションで `/plugin list` を実行し、`caw@caw-local` がリストに出ることを確認。

---

## Phase 3 — `/caw` 実行（オンボーディングウィザード）

新セッション内で：

```
/caw
```

期待される挙動：

1. **検出**: `.company/` が無いと判定 → オンボーディングモードへ
2. **AskUserQuestion Call 1（研究プロファイル 4 問）**:
   - 研究分野
   - 主な計算ソフト
   - ナレッジベース
   - クラウドストレージ
3. **AskUserQuestion Call 2（部署選択 2 問）**:
   - 秘書 + 立ち上げる部署（research/engineering/computation/analysis/writing/review/presentation から複数選択）
   - 化学者向け Playbook を入れるかどうか

### 入力例（sample-project-01）

**Call 1**:
- 研究分野: 「有機化学・結晶化学」
- 計算ソフト: 「Gaussian」「CP2K」
- ナレッジベース: 「Notion」
- クラウドストレージ: 「Google Drive」

**Call 2**:
- 部署: 「秘書」「research」「computation」「writing」
- Playbook: 「はい（Gaussian + CP2K のみ）」

回答送信後、scaffold が走る。

---

## Phase 4 — Scaffold 出力の検証

```bash
cd ~/caw-test/sample-project-01
tree .company
```

期待される構造（最低限）：

```
.company/
├── CLAUDE.md                              ← ルート（プレースホルダ置換済み）
├── secretary/
│   ├── CLAUDE.md
│   ├── notes/
│   └── todos/
├── research/
│   ├── CLAUDE.md
│   └── topics/
├── computation/
│   ├── CLAUDE.md
│   ├── jobs/
│   └── playbooks/
│       ├── gaussian.md
│       └── cp2k.md
└── writing/
    ├── CLAUDE.md
    └── drafts/
```

### 検証チェックリスト

| 項目 | 確認方法 |
|---|---|
| ルート `.company/CLAUDE.md` のプレースホルダが全て置換されている | `grep -n '{{' .company/CLAUDE.md` が何も出ない |
| ルート CLAUDE.md に研究分野・計算ソフト・KB・ストレージが反映 | 目視 |
| 選択した部署のみ存在（未選択は無い） | `ls .company/` |
| `computation/playbooks/` に gaussian.md と cp2k.md がある | `ls .company/computation/playbooks/` |
| 選択外の playbook（gromacs.md など）は無い | 同上 |
| 各部署 CLAUDE.md の `## 役割` `## ルール` が空でない | 目視 |
| Playbook の YAML frontmatter `tool:` `last_updated:` が正しい | `head -10 .company/computation/playbooks/gaussian.md` |

---

## Phase 5 — 結果記録

`~/caw-test/results.md` に検証結果をテーブル形式で記録：

```markdown
# caw プラグインテスト結果

## 2026-05-11

### sample-project-01（有機化学 + Gaussian/CP2K + Notion + Drive）

| 検証項目 | 結果 | メモ |
|---|---|---|
| `/caw` 認識 | ✅ / ❌ | |
| オンボーディング Call 1 表示 | ✅ / ❌ | |
| オンボーディング Call 2 表示 | ✅ / ❌ | |
| `.company/CLAUDE.md` 生成 | ✅ / ❌ | プレースホルダ残: あり/なし |
| 選択部署のみ生成 | ✅ / ❌ | |
| Playbook 配置（Gaussian, CP2K） | ✅ / ❌ | |
| 各部署 CLAUDE.md 内容妥当 | ✅ / ❌ | |
| 想定外の挙動 | | （あれば記述） |
```

問題があれば SKILL.md / references を修正 → symlink 経由で即反映 → 再テスト（別 sample-project-NN で）。

---

## Phase 6 — クリーンアップ

テスト終了後：

```bash
rm -rf ~/caw-test
```

これだけで完全に除去できる。`~/lab` には一切影響しない。

プラグイン自体を外したい場合は別途：

```
/plugin uninstall caw@caw-local
```

または手動で `~/.claude/plugins/installed_plugins.json` と `settings.json` から `caw@caw-local` 関連を削除。

---

## トラブルシューティング

### Q1. `/caw` が認識されない

- `/plugin list` で `caw@caw-local` が `enabled` か確認
- `~/.claude/plugins/cache/caw-local/caw/0.1.0/skills/caw/SKILL.md` が存在するか確認
- symlink が切れていれば Phase 0 末尾の `ln -sfn` で再作成
- Claude Code を完全再起動

### Q2. symlink が壊れている

```bash
ls -la ~/.claude/plugins/cache/caw-local/caw/0.1.0
# 「No such file or directory」または点線で表示される場合
mkdir -p ~/.claude/plugins/cache/caw-local/caw
ln -sfn ~/lab/spring/chemist-ai-workflow/plugin ~/.claude/plugins/cache/caw-local/caw/0.1.0
```

### Q3. Scaffold 結果が想定と違う

- `references/chemistry-departments.md` で該当部署のテンプレ内容を確認
- `references/claude-md-template.md` のプレースホルダ仕様を確認
- 修正 → symlink 経由で即反映 → 別 sample-project-NN で再テスト

### Q4. Playbook が配置されない

- `references/playbook-starters.md` に該当ソフトのセクションがあるか確認
- SKILL.md の Step 3 で computation 部署選択時の playbook 配置ロジックを確認

### Q5. Marketplace 信頼確認のダイアログが出る

初回のみ「この marketplace を信頼しますか？」と聞かれる。`y` で承認。

### Q6. プラグインを完全に外したい

```
/plugin uninstall caw@caw-local
```

または手動で：

```bash
# 1. installed_plugins.json から caw@caw-local エントリ削除
# 2. settings.json の enabledPlugins から "caw@caw-local" 削除
# 3. settings.json の extraKnownMarketplaces から "caw-local" 削除（他で使ってなければ）
# 4. キャッシュ削除
rm -rf ~/.claude/plugins/cache/caw-local
# 5. marketplace 削除（不要なら）
rm -rf ~/.claude/plugins/marketplaces/caw-local
# 6. known_marketplaces.json から caw-local エントリ削除
```

---

## イテレーション運用

ローカル symlink 経由で動作させているため、プラグイン本体（`~/lab/spring/chemist-ai-workflow/plugin/`）を編集すると次の `/caw` 実行で即反映される（キャッシュなし）。

推奨ワークフロー：

1. `~/caw-test/sample-project-NN` で `/caw` 実行
2. 想定通りでない箇所を記録
3. このセッション（`~/lab`）で SKILL.md / references を編集
4. 新しい `sample-project-NN+1` を作成して再実行（既存 sample は履歴として残す）
5. 全プロファイルで安定したら Phase 2 → ベータ配布へ

---

## 関連ファイル

- プラグイン本体: `~/lab/spring/chemist-ai-workflow/plugin/`
- ローカル marketplace: `~/.claude/plugins/marketplaces/caw-local/`
- キャッシュ symlink: `~/.claude/plugins/cache/caw-local/caw/0.1.0`
- LP plugin ページ: `~/lab/spring/chemist-ai-workflow/web/src/content/docs/plugin.md`
