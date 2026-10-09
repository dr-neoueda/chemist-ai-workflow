# caw — GitHub Copilot CLI 版

Chemist's AI Workflow (caw) の **GitHub Copilot CLI** 向け配布。
Codex CLI 版（`../codex-plugin/`）・Claude Code 版（`../plugin/`）と**同じ 15 スキル**を、
GitHub Copilot CLI のプラグイン形式で提供する。

> **企業向けトラック。** 化学メーカーの研究部門など、GitHub Copilot が全社導入されている
> 組織での導入伴走を想定している。2026-08-21 に 2 スキルの PoC から **15 スキルへフルポート**した。

## なぜ Copilot で動くのか

GitHub Copilot CLI は、caw が依存するプリミティブを同型でサポートする：

| caw の柱 | Claude Code | GitHub Copilot CLI |
|---|---|---|
| 部署の指示ファイル | `CLAUDE.md` | `AGENTS.md`（primary）/ `CLAUDE.md` を両方ネイティブ読込 |
| Skills | `skills/<name>/SKILL.md` | `skills/<name>/SKILL.md`（同形式・frontmatter 付き） |
| Sub-agents | sub-agents | custom agents（`agents/<name>.agent.md`）+ `/fleet` |
| Hooks | SessionStart/Stop/PreToolUse… | 同名ライフサイクル（SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, SubagentStart, SubagentStop, Stop） |
| MCP | MCP | MCP（`.mcp.json`、標準 `mcpServers` 形式） |
| 配布 | `.claude-plugin/marketplace.json` + plugin | `.github/plugin/marketplace.json` + `plugin.json` |

詳細な互換性分析と出典は [`../docs/copilot-compatibility.md`](../docs/copilot-compatibility.md)。

## 対応する Copilot（重要）

- ✅ **GitHub Copilot CLI**（`copilot`、ターミナル native エージェント）
- ✅ GitHub Copilot（VS Code Agent Mode、同じカスタマイズ基盤）
- ✕ Microsoft 365 Copilot / Copilot Studio（declarative agent・別パラダイム、研究のファイル運用には不向き）
- ✕ 消費者 Copilot（copilot.microsoft.com / Windows、チャットのみ）

## インストール（リポジトリ公開・marketplace 設定後）

```bash
# 1. マーケットプレイスを登録（.github/plugin/marketplace.json を読む）
copilot plugin marketplace add dr-neoueda/chemist-ai-workflow

# 2. caw プラグインをインストール
copilot plugin install caw
```

> **前提**：事前に **git** と **Node.js（LTS）** が必要です（`copilot plugin marketplace add` は配布元 GitHub を clone するため git が要ります）。

その後、プロジェクトのディレクトリで `copilot` を起動し、「caw」または
「化学プロジェクトの環境を作って」と話しかけるとオンボーディングが始まる。

## 同梱スキル（15）

### 研究トラック（12）

| スキル | 役割 |
|---|---|
| `caw` | オンボーディング → 部署 `office/` 一括 scaffold → 運営モード。scaffold 用テンプレ（`references/`）同梱 |
| `caw-research` | 論文検索（arXiv / Crossref / Semantic Scholar / OpenAlex / PubMed）→ クリック可能な HTML リスト |
| `caw-register` | 入手済み PDF → 書誌付き要約 md → ナレッジベース + クラウドストレージへ登録 |
| `caw-write` | 登録済み文献を引用源に、論文・申請書・学会要旨を本人の文体で執筆 |
| `caw-input` | 7 ソフト（Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO / ChimeraX）の入力雛形 |
| `caw-playbook` | 計算 log の解析 → Lessons Learned 起案 → Playbook 追記 |
| `caw-analyze` | 手法非依存の解析コンパニオン |
| `caw-slides` | SVG-first で編集可能な pptx を生成（native 変換器同梱） |
| `caw-setup` | 前提ツールの検出と、**1 つずつ理由を説明しながら**の導入 |
| `caw-doctor` | `office/` 構造の健全性チェックと修復提示 |
| `caw-intake` | 統合 `inbox/` の自動仕分け |
| `caw-report` | 開発者向けの匿名動作レポート |

### 就活トラック（3）

`caw-es` / `caw-interview` / `caw-events`
（オンボーディングで「就活」トラックを選んだときだけ使う。企業導入では通常使わない）

**未収載**: `hooks.json`（ライフサイクル hooks）。Copilot CLI は hooks に対応しているが未移植。

## 実装メモ・既知の制約

- 部署テンプレ `skills/caw/references/chemistry-departments.md` の見出しは `AGENTS.md` に統一済み
  （Copilot は `AGENTS.md`/`CLAUDE.md` を両方読むが、primary の `AGENTS.md` で揃えた）。
- MCP 設定は Claude 形式コマンド例を残しつつ、Copilot 用 `.mcp.json`（標準 `mcpServers` 形式）を併記
  （`skills/caw/references/mcp-setup-templates.md`）。
- **13 スキルは Codex 版と byte 一致**で維持している（`scripts/check-consistency.sh` が
  ディレクトリ単位で強制。ドリフトすると CI が落ちる）。`caw` と `caw-setup` のみ、
  CLI 名（`copilot` vs `codex`/`claude`）の違いがあるため系統ごとに保守する。
- **hooks は未移植**。Copilot CLI はライフサイクル hooks に対応しているが、
  Claude Code 版の 3 本（SessionStart / PostToolUse / Stop）はまだ移していない。
- **`caw-slides` の Windows 実機確認は未実施。** パイプライン自体は Windows 互換に
  作られている（v1.71.0）が、Copilot CLI 上での動作は未検証。

## ライセンス

MIT。開発: Shinno Ueda (UEC SPRING)。
