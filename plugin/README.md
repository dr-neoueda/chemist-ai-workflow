# caw — Chemist's AI Workflow Plugin

化学研究プロジェクトのための AI 部署システムを 1 コマンドで構築する Claude Code プラグイン。秘書部から開始し、必要な部署を必要なときに増やす。計算ソフトの Playbook と作業ディレクトリも対話的に整備。

## インストール

```bash
claude
> /plugin marketplace add dr-neoueda/chemist-ai-workflow
> /plugin install caw
```

`/plugin list` で `caw` が `enabled` 表示されれば導入完了。

## クイックスタート

```bash
cd ~/your-research-project
claude
> /caw
```

`.company/` が存在しない場合、オンボーディングウィザードが起動：

1. **研究プロファイル**（4 問）：研究分野、計算ソフト、ナレッジベース、クラウドストレージ
2. **部署選択**：立ち上げる部署を 7 つから複数選択（秘書部は常設）

選択内容に応じて、`.company/` 部署と作業ディレクトリ（`gaussian/`、`papers/` 等）が一括生成される。2 回目以降の `/caw` は運営モードで起動し、秘書を窓口にした対話型の研究支援に入る。

## 生成される構造の例

研究分野：物理化学、計算ソフト：ORCA + LAMMPS、KB：Obsidian、ストレージ：Google Drive、部署：秘書 + research + computation を選択した場合：

```
your-research-project/
├── .company/
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

## 含まれる内容

- **`/caw` スキル**：オンボーディング → 自動スキャフォールド → 運営モードの一連
- **8 部署 CLAUDE.md テンプレート**：secretary / research / engineering / computation / analysis / writing / review / presentation
- **Playbook 雛形**：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用
- **作業ディレクトリ自動生成**：選択した計算ソフトと部署に応じて配置

## 運営モードでできること

| 入力例 | 動作 |
|---|---|
| 「今日の TODO を整理して」 | `secretary/todos/YYYY-MM-DD.md` を表示・編集 |
| 「ORCA で benzene の構造最適化の雛形を作って」 | `orca/<system>_<purpose>_<YYYYMMDD>/` を作成し `.inp` 雛形 + `.company/computation/jobs/` にジョブ記録 |
| 「読んだ論文を登録して」 | PDF → `.company/research/papers/<author-year>.md` に書誌情報付き md を生成 |
| 「ここまでの会話で決めたことを記録して」 | `secretary/notes/YYYY-MM-DD-decisions.md` に追記 |

## プラグイン構造

```
plugin/
├── .claude-plugin/plugin.json
├── README.md
└── skills/caw/
    ├── SKILL.md
    └── references/
        ├── claude-md-template.md
        ├── chemistry-departments.md
        └── playbook-starters.md
```

## ライセンス

MIT License. 詳細は repo 直下の [LICENSE](../LICENSE) を参照。

## 関連リンク

- 配布元 LP: [Chemist's AI Workflow](https://github.com/dr-neoueda/chemist-ai-workflow)
- 開発元: 電気通信大学 SPRING（戦略的研究人材育成事業）

## 貢献

Issue / Pull Request 歓迎。開発時のローカルテスト手順は [TESTING.md](./TESTING.md) を参照。
