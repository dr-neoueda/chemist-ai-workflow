# caw — GitHub Copilot CLI 版（PoC）

Chemist's AI Workflow (caw) の **GitHub Copilot CLI** 向け配布（Proof of Concept）。
Claude Code 版（`../plugin/`）・Codex CLI 版（`../codex-plugin/`）と同じメソッドを、
GitHub Copilot CLI のプラグイン形式で提供する。

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

その後、プロジェクトのディレクトリで `copilot` を起動し、「caw」または
「化学プロジェクトの環境を作って」と話しかけるとオンボーディングが始まる。

## PoC の範囲

本 PoC では **2 スキル**を Copilot 形式に翻訳して同梱する：

- **`caw`** — オンボーディング（経験レベル判定 → 研究プロファイル）→ 部署 `office/` 一括 scaffold → 運営モード。scaffold 用テンプレ（`references/`）同梱
- **`caw-setup`** — 前提ツール（Python・poppler・python-pptx 等）の検出と順次インストール

未収載（フルポート時に追加予定）: `caw-slides` / `caw-paper` / `caw-input` / `caw-playbook` / `caw-doctor`、`hooks.json`、`.mcp.json`。

## 既知の PoC 簡略化

- 部署テンプレ `skills/caw/references/chemistry-departments.md` の見出しは `AGENTS.md` に統一済み
  （Copilot は `AGENTS.md`/`CLAUDE.md` を両方読むが、primary の `AGENTS.md` で揃えた）。
- MCP 設定は Claude 形式コマンド例を残しつつ、Copilot 用 `.mcp.json`（標準 `mcpServers` 形式）を併記
  （`skills/caw/references/mcp-setup-templates.md`）。
- 同梱スキルは `caw` / `caw-setup` の 2 つ（PoC）。残りの 5 スキル（caw-doctor / caw-input / caw-paper /
  caw-playbook / caw-slides）と hooks のフルポートは Phase 2 検討。

## ライセンス

MIT。開発: Shinno Ueda (UEC SPRING)。
