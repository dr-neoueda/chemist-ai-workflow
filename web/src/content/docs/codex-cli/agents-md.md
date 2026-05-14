---
title: AGENTS.md の書き方
description: Codex CLI が読むプロジェクトルールファイル `AGENTS.md` の構造、ルール記述の粒度、Claude Code の `CLAUDE.md` との対応
---

`AGENTS.md` は Codex CLI（および他の AI エージェント）が読む、プロジェクト固有のルール記述ファイルです。Claude Code の `CLAUDE.md` に相当し、エージェント横断で読まれる universal な標準としても採用が広がっています。本ページでは `AGENTS.md` の階層、書き方、化学プロジェクトでの実用例を通します。

## ファイル配置の階層

Codex CLI は以下の順で `AGENTS.md` を探索し、コンテキストに注入します。

```
~/.codex/AGENTS.md                ← グローバル（全プロジェクト）
└─ <project-root>/AGENTS.md       ← プロジェクトルート
    └─ <subdir>/AGENTS.md         ← サブディレクトリ単位の補足
        └─ <deeper>/AGENTS.md     ← さらに下位
```

下位の `AGENTS.md` は上位のルールを **継承 + 上書き** します。研究プロジェクトでは：

- **グローバル**：研究者個人の好み（言語、コーディング規約、思考レベル）
- **プロジェクトルート**：その研究プロジェクト共通のルール（使う計算ソフト、ファイル命名規則）
- **サブディレクトリ**：部署単位 / 計算単位の固有ルール（caw の `.company/<dept>/AGENTS.md` がこの層）

## 最小構成

```markdown
# プロジェクト名

## このプロジェクトについて

何をしているプロジェクトか 1-2 行。

## 重要なルール

- ルール 1
- ルール 2
```

これだけでも Codex は読みます。ただし「具体的に何を期待しているか」が伝わるほうがエージェントの判断が安定します。

## 推奨される構成

化学研究プロジェクト向けの `AGENTS.md` テンプレート：

```markdown
# <プロジェクト名>

## 概要

- 分野: <有機化学 / 物理化学 / 材料・無機・結晶化学 等>
- 主要活動: <実験 / 計算 / 論文執筆 / 申請書>
- 環境: macOS / Linux / HPC（記述があれば）

## 使用ツール

- 計算: <Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO>
- 解析: Python (NumPy, SciPy, ASE, RDKit, MDAnalysis, pymatgen)
- ナレッジベース: <Notion / Obsidian / Logseq>
- クラウドストレージ: <Google Drive / Dropbox / OneDrive>

## コーディング規約

- Python 3.12+ を使用
- 型ヒント必須
- docstring は NumPy スタイル
- 物理量には単位コメントを必ず付ける（例: `# kJ/mol`, `# Å`, `# fs`, `# K`）
- 計算パラメータはハードコーディング禁止（設定ファイル or 引数）
- 乱数シード固定（再現性確保）

## ファイル命名規則

- シミュレーションスクリプト: `sim_<目的>_<日付>.py`
- Gaussian 入力: `<分子名>_<計算レベル>.gjf`
- 解析スクリプト: `analyze_<対象>.py`
- 図の出力: `fig_<内容>_<日付>.png`
- 実験記録: `exp_<実験名>_<日付>.md`

## エージェントの振る舞い

- 物理量の単位を必ず明示する
- エネルギー単位変換に注意（kcal/mol ↔ kJ/mol ↔ eV ↔ Hartree）
- 計算手法の選択は目的に応じて適切に
- 既存ファイルは上書きせず追記または新規作成

## 関連

- 部署システム: `.company/`（caw プラグインで scaffold 済）
- 計算 Playbook: `.company/computation/playbooks/<tool>.md`
- 文献 DB: `<KB の場所>`
```

## ルール記述の粒度

「ルールを書く」と言っても、書きすぎ・書かなさすぎの両極端があります。

### 書かないほうがよいもの

- **当然のこと**：「コードは正しく動くべき」など。エージェントの前提
- **頻繁に変わる詳細**：「現在のジョブ ID」「今日の TODO」など。`AGENTS.md` ではなく `secretary/notes/` 等の動的データへ
- **巨大なリスト**：参照が必要なら別ファイル（`references/`）に切り出して `AGENTS.md` から link
- **エージェントが文脈から推論できるもの**：プロジェクト構造を見れば明らかな情報

### 書くべきもの

- **過去の失敗からの教訓**：「Gaussian の opt=(ts,...) と stable=opt は同一ジョブ禁止」
- **暗黙の規約**：「LaTeX 原稿は `manuscripts/_style/` のスタイルファイルを参照」
- **ドメイン固有の用語と表記**：「汎関数名は B3LYP、定数を含む基底は def2-SVP のように正確に」
- **エージェント間の役割分担**：「コード review は Python reviewer → Codex review の二段」
- **失敗パターンへの対応**：「Bash の non-zero exit が出たら最大 2 回まで仮説修正、それ以上は rescue agent」

## サブディレクトリでの上書き

caw プラグインが生成する構造の場合：

```
my-research-project/
├── AGENTS.md                            ← プロジェクト全体ルール（任意）
└── .company/
    ├── AGENTS.md                        ← .company/ 運営ルール（caw 生成）
    ├── secretary/AGENTS.md              ← 秘書部 ロール
    ├── research/AGENTS.md               ← 文献部 ロール
    ├── computation/AGENTS.md            ← 計算管理部 ロール
    └── writing/AGENTS.md                ← 論文執筆部 ロール
```

各部署の `AGENTS.md` は、Codex が該当ディレクトリ配下で作業する時にコンテキストに読み込まれます。「秘書部で TODO を扱う時の口調」「計算管理部で playbook を必ず最初に読む」など、部署固有のルールはここに集約。

## Claude Code の `CLAUDE.md` との関係

| 観点 | Codex CLI (`AGENTS.md`) | Claude Code (`CLAUDE.md`) |
|---|---|---|
| ファイル名 | `AGENTS.md` | `CLAUDE.md`（および `AGENTS.md` も読む） |
| 階層的読み込み | グローバル → プロジェクト → サブディレクトリ | 同左 |
| 内容の構造 | 自由形式 | 自由形式 |
| エージェント横断性 | 高（universal 標準） | 中（Codex も読むが Claude 寄り） |

**両方使う場合の推奨**：プロジェクトルートに `AGENTS.md` のみ置き、Claude Code 側にも `AGENTS.md` を読ませる。これで二重管理を避けられます。caw プラグイン側は CLI に応じて出し分け（Claude Code 版 → `CLAUDE.md`、Codex 版 → `AGENTS.md`）。

## ECC 連携ルールの記述例

研究室で everything-claude-code（ECC）系のスキルを併用する場合：

```markdown
## エージェントの振る舞い拡張

| ユーザーの発言例 | エージェントの判断 |
|-----------------|-------------------|
| 「〇〇のスクリプト作って」 | `search-first` → `plan` → `tdd` → 完成後 `python-review` + `codex:review` |
| 「このコード見て」 | `code-review` + `codex:review`（必ず併用） |
| 「エラーが出る」 | `build-fix` → 解決しなければ `codex:rescue` |
| 「〇〇について調べて」 | `search-first` スキル |
| 「テスト書いて」 | `tdd` を使用、完成後 `codex:review` でテストの抜けも確認 |
```

このように「ユーザー発言 → エージェントが取るべき行動」のマッピング表を `AGENTS.md` に書くと、対話が安定します。

## 更新運用

`AGENTS.md` は **生きたドキュメント**として運用します：

- 同じ失敗を 2 回繰り返したら、ルールに追加
- ツールやライブラリの変更（バージョンアップ、API 変更）があれば追記
- 不要になったルールは積極的に削除（古い記述は noise になる）

caw プラグインの運用知（学び 3-5 件を毎日 `secretary/notes/<date>-learnings.md` に記録）と連動させると、定期的なルール棚卸しが自然に行えます。

## 次のステップ

- [Skills](/codex-cli/skills/) — `AGENTS.md` ではなく Skills として括り出すべき機能
- [Commands](/codex-cli/commands/) — スラッシュコマンドとの使い分け
- [.company/ 部署テンプレート](/claude-code/company-template/) — 各部署 AGENTS.md の典型構成
