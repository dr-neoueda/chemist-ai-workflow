# caw — Chemist's AI Workflow Plugin (Codex CLI 版)

化学研究プロジェクトのための AI 部署システムを 1 コマンドで構築する Codex CLI プラグイン。秘書部から開始し、必要な部署を必要なときに増やす。計算ソフトの Playbook と作業ディレクトリも対話的に整備。

Claude Code 版（`../plugin/`）と内容は基本同一。`.company/<dept>/CLAUDE.md` の代わりに `.company/<dept>/AGENTS.md` を生成する点のみ異なる。

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

`.company/` が存在しない場合、対話的オンボーディングが起動：

1. **研究プロファイル**（4 問）：研究分野、計算ソフト、ナレッジベース、クラウドストレージ
2. **部署選択**：立ち上げる部署を 7 つから複数選択（秘書部は常設）

選択内容に応じて、`.company/` 部署（AGENTS.md 構成）と作業ディレクトリ（`gaussian/`、`papers/` 等）が一括生成される。

## 生成される構造の例

研究分野：物理化学、計算ソフト：ORCA + LAMMPS、KB：Obsidian、ストレージ：Google Drive、部署：秘書 + research + computation を選択した場合：

```
your-research-project/
├── .company/
│   ├── AGENTS.md
│   ├── secretary/{AGENTS.md, inbox/, todos/, notes/}
│   ├── research/{AGENTS.md, papers/, topics/}
│   └── computation/
│       ├── AGENTS.md
│       ├── jobs/
│       ├── parameters/
│       └── playbooks/{orca.md, lammps.md}
├── orca/README.md          ← 入出力ファイル置き場
├── lammps/README.md
└── papers/README.md        ← PDF ステージング
```

## 含まれる内容

- **`caw` スキル**：オンボーディング → 自動スキャフォールド → 運営モードの一連（起動は `caw` と入力、または自然言語で指示）
- **8 部署 AGENTS.md テンプレート**：secretary / research / engineering / computation / analysis / writing / review / presentation
- **Playbook 雛形**：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用
- **作業ディレクトリ自動生成**：選択した計算ソフトと部署に応じて配置

## Claude Code 版との関係

| 観点 | Claude Code 版 (`plugin/`) | Codex 版 (`codex-plugin/`) |
|---|---|---|
| プラグインマニフェスト | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` |
| マーケットプレイス manifest | `<repo>/.claude-plugin/marketplace.json` | `<repo>/.agents/plugins/marketplace.json` |
| 生成される指示ファイル | `<dept>/CLAUDE.md` | `<dept>/AGENTS.md` |
| インストール | `/plugin install caw@chemist-ai-workflow` | `codex plugin install caw` |
| スキル本体（プロンプト指示） | 同一 | 同一 |
| Playbook 雛形 | 同一 | 同一 |

両プラグインは同じリポジトリ（`dr-neoueda/chemist-ai-workflow`）から並列配信。研究室で Claude Code 派と Codex CLI 派が混在しても、同じ `.company/` メソッドを共有できる。

## ライセンス

MIT License. 詳細は repo 直下の [LICENSE](../LICENSE) を参照。

## 関連リンク

- 配布元 LP: [Chemist's AI Workflow](https://github.com/dr-neoueda/chemist-ai-workflow)
- Claude Code 版: [`../plugin/`](../plugin/)
- 開発元: 電気通信大学 SPRING（戦略的研究人材育成事業）
