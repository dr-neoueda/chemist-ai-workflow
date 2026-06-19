# caw — Chemist's AI Workflow Plugin (Codex CLI 版)

化学研究プロジェクトのための AI 部署システムを 1 コマンドで構築する Codex CLI プラグイン。秘書部から開始し、必要な部署を必要なときに増やす。計算ソフトの Playbook と作業ディレクトリも対話的に整備。

Claude Code 版（`../plugin/`）と内容は基本同一。`office/<dept>/CLAUDE.md` の代わりに `office/<dept>/AGENTS.md` を生成する点のみ異なる。

## インストール

```bash
codex plugin marketplace add dr-neoueda/chemist-ai-workflow
codex plugin install caw
```

`codex plugin list` で `caw` が `enabled` 表示されれば導入完了。

## クイックスタート

```bash
cd ~/your-research-project
codex
> caw
```

`office/` が存在しない場合、対話的オンボーディングが起動：

1. **研究プロファイル**（4 問）：研究分野、計算ソフト、ナレッジベース、クラウドストレージ
2. **部署選択**：立ち上げる部署を 7 つから複数選択（秘書部は常設）

選択内容に応じて、`office/` 部署（AGENTS.md 構成）と作業ディレクトリ（`work/gaussian/`、`work/papers/` 等）が一括生成される。

## 生成される構造の例

研究分野：物理化学、計算ソフト：ORCA + GROMACS、KB：Obsidian、ストレージ：Google Drive の場合（全 8 部署を作成。下記は抜粋）：

```
your-research-project/
├── office/                       ← 運営側（全 8 部署。各 AGENTS.md＋運営情報のみ）
│   ├── AGENTS.md
│   ├── secretary/{AGENTS.md, inbox/, todos/, notes/}
│   └── computation/{AGENTS.md, jobs/, parameters/, playbooks/{orca.md, gromacs.md}}
├── inbox/                        ← 統合 inbox（何でも入れて「処理して」）
└── work/                         ← 成果物・作業ファイルはすべてこの中
    ├── orca/    {README.md, inbox/, _past-data/}   ← 入出力ファイル置き場
    ├── gromacs/ {README.md, inbox/, _past-data/}
    ├── papers/  {README.md, inbox/}                ← 文献要約 + PDF ステージング
    └── analyses/ figures/ manuscripts/ presentations/slides/ …
```

## 含まれる内容

- **`caw` スキル**：オンボーディング → 自動スキャフォールド → 運営モードの一連（起動は `caw` と入力、または自然言語で指示）
- **8 部署 AGENTS.md テンプレート**：secretary / research / engineering / computation / analysis / writing / review / presentation
- **Playbook 雛形**：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用
- **作業ディレクトリ自動生成**：選択した計算ソフトと部署に応じて配置。初心者向けに投入用 `inbox/` と過去データ用 `_past-data/` も生成
- **`caw-setup` スキル**：外部ツール（Python・poppler・python-pptx 等）の不足を検出し、計画提示 → 一度の承認 → 順番にインストール（macOS / Windows）。CLI/Node 自体は `setup/caw-setup.sh`・`setup/caw-setup.ps1` を案内
- **`caw-playbook` の過去データ取り込み**：`_past-data/` の過去入出力を解析し、その人の傾向を Playbook に初期 seed

## Claude Code 版との関係

| 観点 | Claude Code 版 (`plugin/`) | Codex 版 (`codex-plugin/`) |
|---|---|---|
| プラグインマニフェスト | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` |
| マーケットプレイス manifest | `<repo>/.claude-plugin/marketplace.json` | `<repo>/.agents/plugins/marketplace.json` |
| 生成される指示ファイル | `<dept>/CLAUDE.md` | `<dept>/AGENTS.md` |
| インストール | `/plugin install caw@chemist-ai-workflow` | `codex plugin install caw` |
| スキル本体（プロンプト指示） | 同一 | 同一 |
| Playbook 雛形 | 同一 | 同一 |

両プラグインは同じリポジトリ（`dr-neoueda/chemist-ai-workflow`）から並列配信。研究室で Claude Code 派と Codex CLI 派が混在しても、同じ `office/` メソッドを共有できる。

## ライセンス

MIT License. 詳細は repo 直下の [LICENSE](../LICENSE) を参照。

## 関連リンク

- 配布元 LP: [Chemist's AI Workflow](https://github.com/dr-neoueda/chemist-ai-workflow)
- Claude Code 版: [`../plugin/`](../plugin/)
- 開発元: 電気通信大学 SPRING（戦略的研究人材育成事業）
