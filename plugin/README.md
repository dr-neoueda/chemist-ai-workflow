# caw — Chemist's AI Workflow Plugin

化学研究プロジェクトのための AI 部署システムを 1 コマンドで構築する Claude Code プラグイン。秘書部から開始し、必要な部署を必要なときに増やす。計算ソフトの Playbook と作業ディレクトリも対話的に整備。

## インストール

```bash
claude
> /plugin marketplace add dr-neoueda/chemist-ai-workflow
> /plugin install caw
```

`/plugin list` で `caw` が `enabled` 表示されれば導入完了。

## 動作環境

対応 OS は **macOS** と **Windows** の 2 つ（同列にサポート）。

| OS | コア（Skills のワークフロー） | Hooks |
|---|---|---|
| macOS | ✅ | ✅ |
| Windows | ✅ | ✅（Git Bash または WSL2 を併用。`hooks.json` が `bash` を呼ぶため） |

- **コア（オンボーディング・部署スキャフォールド・5 Skills）** は OS 非依存。SKILL.md は markdown のワークフロー指示で、Claude Code / Codex CLI のファイルツールがパスをクロスプラットフォーム処理する
- **Hooks**（SessionStart / PostToolUse / Stop）は bash スクリプト。macOS はそのまま、Windows は Git Bash または WSL2 で動作する
- hook スクリプトは POSIX 準拠で記述（`stat -f` などの BSD 専用構文、`date -j` などの macOS 専用構文は使わない）。Windows の Git Bash / WSL2 でも macOS の環境でも動作する
- `office/` は**可視フォルダ**（先頭ドットなし）で macOS Finder / Windows Explorer のどちらでも見える。「運営情報専用エリア」で成果物とは分ける。**caw は不可視の先頭ドット始まりフォルダをユーザーのプロジェクトに作らない（絶対）**
- 必要な外部ツールと OS 別のインストール手順は LP の「必要なツールとインストール」を参照

## クイックスタート

```bash
cd ~/your-research-project
claude
> /caw
```

`office/` が存在しない場合、オンボーディングウィザードが起動：

1. **研究プロファイル**（4 問）：研究分野、計算ソフト、ナレッジベース、クラウドストレージ
2. **部署選択**：立ち上げる部署を 7 つから複数選択（秘書部は常設）

選択内容に応じて、`office/` 部署と作業ディレクトリ（`gaussian/`、`papers/` 等）が一括生成される。2 回目以降の `/caw` は運営モードで起動し、秘書を窓口にした対話型の研究支援に入る。

## 生成される構造の例

研究分野：物理化学、計算ソフト：ORCA + LAMMPS、KB：Obsidian、ストレージ：Google Drive、部署：秘書 + research + computation を選択した場合：

```
your-research-project/
├── office/
│   ├── CLAUDE.md
│   ├── secretary/{CLAUDE.md, inbox/, todos/, notes/}
│   ├── research/{CLAUDE.md, papers/, topics/}
│   └── computation/
│       ├── CLAUDE.md
│       ├── jobs/
│       ├── parameters/
│       └── playbooks/{orca.md, lammps.md}
├── orca/README.md          ← 入出力ファイル置き場
├── lammps/README.md
└── papers/README.md        ← PDF ステージング
```

## 含まれる内容（v1.5.2）

### Skills

- **`/caw`**：オンボーディング（Quick / Standard / Advanced の 3 段階）→ 自動スキャフォールド → 運営モードの一連
- **`/caw-paper`**：論文検索（arXiv / Crossref / Semantic Scholar / OpenAlex / PubMed）+ 入手済み PDF のメタデータ抽出 → ナレッジベース（Notion / Obsidian 他）+ クラウドストレージ（Google Drive 他）への自動登録
- **`/caw-input`**：6 ソフト（Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO）の入力ファイル雛形生成、Playbook デフォルト起点 + ジョブ記録自動生成
- **`/caw-playbook`**：計算 log の自動解析 → Lessons Learned エントリ起案 → Playbook 末尾追記、memory feedback 昇格判定。`_past-data/` に置いた過去データの一括取り込み（その人向けに Playbook を初期最適化）にも対応
- **`/caw-doctor`**：`office/` 構造の健全性チェック（部署 CLAUDE.md の存在、旧構造の検出、Playbook 更新滞り等）と修復コマンド提示
- **`/caw-setup`**：caw を十分に使うための外部ツール（Python・poppler・python-pptx 等）の不足を検出し、計画提示 → 一度の承認 → 順番にインストール（macOS / Windows、冪等）。CLI/Node 自体の導入は `setup/caw-setup.sh`・`setup/caw-setup.ps1` を案内
- **`/caw-slides`**：研究発表用 PowerPoint スライドを生成（学会発表 / 論文紹介 / 報告会 / 講義の 4 用途バリアント）。`pptx_helpers.py`（1000+ 行のヘルパ）+ スタイルガイド（16:9・フォント階層・図表優先・shape 重なり禁止の品質ゲート）同梱。出力は `presentations/slides/`

### Hooks

- **SessionStart**：`office/secretary/notes` の直近 3 件と利用可能 Playbook をコンテキスト自動注入
- **PostToolUse**：成果物が `office/<dept>/` 配下に書き込まれた場合に「成果物配置の二層原則」違反として警告
- **Stop**：今日の活動があるのに `<today>-learnings.md` が無い場合のリマインド

### 部署テンプレート

- 8 部署 CLAUDE.md：secretary / research / engineering / computation / analysis / writing / review / presentation
- 成果物は project root 直下（`papers/` `slides/` 等）、運営情報は `office/<dept>/` という二層構造

### Playbook 雛形

- 計算ソフト：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO / Psi4 / NAMD / LAMMPS / OpenMM + 汎用
- Python ライブラリ：RDKit / ASE / MDAnalysis / pymatgen（API quirks・よくある罠を体系化）

### MCP セットアップ

- オンボーディングのナレッジベース / クラウドストレージ選択に応じて `office/.mcp-setup.md`（Notion / Obsidian / Logseq / Google Drive / Dropbox / OneDrive / Gmail の設定手順）を生成。API key は環境変数管理

### 作業ディレクトリ

- 選択した計算ソフトに応じて `gaussian/` / `orca/` / `cp2k/` / `gromacs/` / `vasp/` / `quantum-espresso/`
- 選択した部署に応じて `papers/` / `topics/` / `manuscripts/` / `presentations/slides/` / `analyses/` / `notebooks/` / `figures/` / `scripts/` / `tools/`

## 運営モードでできること

| 入力例 | 動作 |
|---|---|
| 「今日の TODO を整理して」 | `secretary/todos/YYYY-MM-DD.md` を表示・編集 |
| 「ORCA で benzene の構造最適化の雛形を作って」 | `orca/<system>_<purpose>_<YYYYMMDD>/` を作成し `.inp` 雛形 + `office/computation/jobs/` にジョブ記録 |
| 「読んだ論文を登録して」 | PDF → `papers/<author-year>.md`（top-level、ファイラーで見える）に書誌情報付き md を生成 |
| 「ここまでの会話で決めたことを記録して」 | `secretary/notes/YYYY-MM-DD-decisions.md` に追記 |

## プラグイン構造

```
plugin/
├── .claude-plugin/plugin.json
├── README.md
├── hooks/
│   ├── hooks.json
│   ├── load-playbooks.sh        ← SessionStart
│   ├── output-location-check.sh ← PostToolUse
│   └── learnings-reminder.sh    ← Stop
└── skills/
    ├── caw/
    │   ├── SKILL.md
    │   └── references/
    │       ├── claude-md-template.md
    │       ├── chemistry-departments.md
    │       ├── playbook-starters.md
    │       └── mcp-setup-templates.md
    ├── caw-paper/SKILL.md
    ├── caw-input/SKILL.md
    ├── caw-playbook/SKILL.md
    ├── caw-doctor/SKILL.md
    ├── caw-setup/SKILL.md
    └── caw-slides/
        ├── SKILL.md
        ├── references/   ← style-guide.md, pptx_helpers.py, research_icons.py
        └── templates/    ← generate_*.py（4 用途バリアント）
```

## ライセンス

MIT License. 詳細は repo 直下の [LICENSE](../LICENSE) を参照。

## 関連リンク

- 配布元 LP: [Chemist's AI Workflow](https://github.com/dr-neoueda/chemist-ai-workflow)
- 開発元: 電気通信大学 SPRING（戦略的研究人材育成事業）

## 貢献

Issue / Pull Request 歓迎。開発時のローカルテスト手順は [TESTING.md](./TESTING.md) を参照。
