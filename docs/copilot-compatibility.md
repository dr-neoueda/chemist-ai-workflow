# caw × Microsoft / GitHub Copilot 互換性アセスメント

調査日: 2026-06-04 / 対象: Chemist's AI Workflow (caw) を Microsoft の Copilot 系で使えるか

## 結論（要約）

**できる。ただし「Copilot」を製品で分けること。** caw が動くのは **GitHub Copilot CLI**
（および VS Code Agent Mode）であり、Microsoft 365 Copilot / Copilot Studio / 消費者 Copilot
は対象外。GitHub Copilot CLI は caw が依存するプリミティブ（AGENTS.md/CLAUDE.md 読込・Skills=
SKILL.md・custom agents・hooks・MCP・plugin+marketplace 配布）を **同型・一部同名**でそろえており、
移植コストは Codex CLI 版からの差分が小さい。

## 製品の見分け（ここで答えが正反対）

| 製品 | caw との相性 | 理由 |
|---|---|---|
| **GitHub Copilot CLI**（`github/copilot-cli`） | ◎ ほぼドロップイン | ターミナル native エージェント。Claude Code / Codex CLI と同じ土俵 |
| **GitHub Copilot（VS Code Agent Mode）** | ◎ | 同じカスタマイズ基盤（CLI と共通の skills/agents/hooks/MCP） |
| Microsoft 365 Copilot / Copilot Studio | △ 別物 | Office 生産性向け。declarative agent（マニフェスト型）、Graph 接地。研究のファイル運用に不向き。2025-12 に MCP 対応 |
| 消費者 Copilot（copilot.microsoft.com / Windows） | ✕ | チャットのみ。Web ティア相当の最小 |

注: GitHub Copilot と Microsoft 365 Copilot はライセンスも別。caw 対応 Copilot は **すべて GitHub Copilot**。

## caw の柱 → GitHub Copilot CLI 対応（驚くほど一致）

| caw の柱 | Claude Code | GitHub Copilot CLI |
|---|---|---|
| 部署の指示ファイル | `CLAUDE.md` | `AGENTS.md`（primary）/ `CLAUDE.md` / `GEMINI.md` を読込。`$HOME/.copilot/copilot-instructions.md` も |
| Skills | `skills/<name>/SKILL.md` | `skills/<name>/SKILL.md`（frontmatter 付き・同形式） |
| Sub-agents | sub-agents | custom agents（`agents/<name>.agent.md`）+ `/fleet` 並列 |
| Hooks | SessionStart/Stop/PreToolUse 等 | **同名ライフサイクル**: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, SubagentStart, SubagentStop, Stop |
| MCP | MCP | MCP（`.mcp.json`、標準 `mcpServers` 形式） |
| 配布 | `.claude-plugin/marketplace.json` + plugin | `.github/plugin/marketplace.json`（`.claude-plugin/` も代替可）+ `plugin.json` |

特筆: **hooks のイベント名が Claude Code と完全一致**、**plugin/marketplace 配布モデルも同型**、
**SKILL.md がそのまま使える**。caw は既に `codex-plugin/` で AGENTS.md をターゲットにしているため、
その AGENTS.md を Copilot CLI がそのまま拾う。

## 移植コストの honest assessment

**ほぼそのまま動く**
- `.company/<部署>/` の AGENTS.md / CLAUDE.md（Copilot は両方読む）
- skills/<name>/SKILL.md（同形式）
- MCP 設定（Notion・Drive、`.mcp.json`）
- hooks（イベント名一致でシェルスクリプト流用可能）

**翻訳が要る**
- `plugin.json` スキーマ（Claude の `.claude-plugin/plugin.json` とフィールドが異なる。Copilot は
  root `plugin.json` + `skills`/`agents`/`hooks`/`mcpServers` ポインタ）
- `marketplace.json` スキーマ（`owner`/`metadata{description,version}`/`plugins[].source`）
- MCP 登録コマンド（`claude mcp add` → `.mcp.json` JSON 形式）
- 別ランタイムでの動作テスト

**対象外（明記すべき）**
- Microsoft 365 Copilot / Copilot Studio（declarative agent、Office 接地）
- 消費者 Copilot（チャットのみ）

## 維持コストのトレードオフ

現状 `plugin/`（Claude）+ `codex-plugin/`（Codex）の 2 系統を `scripts/check-consistency.sh` で
監視している。Copilot を足すと **3 系統目のミラー**になり、版 bump・整合チェック・個人化リーク
スキャンの対象が増える。「対応の幅」と「保守負荷」のトレードオフは正直に認識すること。

## PoC の現状（本リポジトリ）

- `copilot-plugin/`: `plugin.json` + 2 スキル（`caw` / `caw-setup`、`caw` は references 同梱）
- `.github/plugin/marketplace.json`: Copilot マーケットプレイス定義（`source: ./copilot-plugin`）
- 版: copilot-plugin 1.0.0（新トラック）。plugin 1.5.2 / codex 1.4.2 は無変更
- 既知の簡略化: 部署テンプレ見出しの `CLAUDE.md` 表記は据え置き（Copilot は両読みで機能的に問題なし）

## 次の一手（フルポート時）

1. 残りスキル（caw-slides / caw-paper / caw-input / caw-playbook / caw-doctor）を Copilot 形式に
2. `hooks.json`（SessionStart コンテキスト注入・Stop レビュー）を同名イベントで移植
3. `.mcp.json` サンプル同梱
4. `check-consistency.sh` に copilot-plugin の mirror/leak チェックを追加
5. 実機（`copilot` CLI）でオンボーディング → scaffold の動作確認

## 出典

- GitHub Copilot CLI — https://github.com/github/copilot-cli / https://docs.github.com/copilot/concepts/agents/about-copilot-cli
- カスタム命令（AGENTS.md/CLAUDE.md/GEMINI.md）— https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
- coding agent の AGENTS.md 対応 — https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/
- プラグイン作成 — https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating
- プラグインマーケットプレイス — https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace
- Agent hooks（lifecycle events）— https://code.visualstudio.com/docs/agent-customization/hooks / https://docs.github.com/en/copilot/reference/hooks-reference
- custom agents（.agent.md）— https://code.visualstudio.com/docs/agent-customization/custom-agents
- prompt files — https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files
- M365 Copilot declarative agents + MCP — https://devblogs.microsoft.com/microsoft365dev/build-declarative-agents-for-microsoft-365-copilot-with-mcp/
- GitHub vs Microsoft Copilot の違い — https://www.techtarget.com/searchenterprisedesktop/tip/Comparing-Copilot-for-Microsoft-365-vs-GitHub-Copilot
