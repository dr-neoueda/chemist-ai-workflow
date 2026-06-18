---
title: "GitHub Copilot CLI（補助・PoC 実証済）"
description: Microsoft 傘下 GitHub のターミナル native エージェント。caw のプリミティブをほぼ同型でサポートし、PoC プラグインを同梱
---

## 「Microsoft の Copilot」はどれを指すか（重要）

「Copilot」は単一製品ではなく、caw との相性が製品ごとに正反対になる。

| 製品 | caw との相性 | 理由 |
|---|---|---|
| **GitHub Copilot CLI** | ◎ ほぼドロップイン | ターミナル native エージェント。Claude Code / Codex CLI と同じ土俵 |
| **GitHub Copilot（VS Code Agent Mode）** | ◎ | 同じカスタマイズ基盤（skills / agents / hooks / MCP） |
| Microsoft 365 Copilot / Copilot Studio | △ 別物 | Office 生産性向け。declarative agent（マニフェスト型）、研究のファイル運用に不向き |
| 消費者 Copilot（Windows / web） | ✕ | チャットのみ。Web 版ティア相当の最小 |

caw が対象とする Copilot は **すべて GitHub Copilot**（Microsoft 傘下）。Microsoft 365 Copilot とはライセンスも別。

## なぜ GitHub Copilot CLI で動くのか

GitHub Copilot CLI は、caw が依存するプリミティブを **同型・一部同名**でそろえている：

| caw の柱 | GitHub Copilot CLI |
|---|---|
| 部署の指示ファイル | `AGENTS.md`（primary）/ `CLAUDE.md` を両方ネイティブ読込 |
| Skills | `skills/<name>/SKILL.md`（frontmatter 付き・同形式） |
| Sub-agents | custom agents（`agents/<name>.agent.md`）+ `/fleet` 並列 |
| Hooks | 同名ライフサイクル（SessionStart / PreToolUse / PostToolUse / Stop 等） |
| MCP | `.mcp.json`（標準 `mcpServers` 形式） |
| 配布 | `.github/plugin/marketplace.json` + `plugin.json` |

caw は Codex CLI 版で既に `AGENTS.md` をターゲットにしているため、その資産を Copilot CLI がそのまま拾う。

## PoC（実証済）

本リポジトリには **GitHub Copilot CLI 版の PoC プラグイン**を同梱している：

- `copilot-plugin/` — `plugin.json` + 2 スキル（`caw` オンボーディング/scaffold、`caw-setup` 環境構築）
- `.github/plugin/marketplace.json` — Copilot マーケットプレイス定義

詳細な互換性分析と出典はリポジトリの `docs/copilot-compatibility.md` を参照。

## インストール（リポジトリ公開・marketplace 設定後）

```bash
copilot plugin marketplace add dr-neoueda/chemist-ai-workflow
copilot plugin install caw
```

## ステータス

**PoC 実証済（2026-06）／フルポートは Phase 2 検討**。残りスキル（caw-slides / caw-register 等）・hooks・
`.mcp.json` の移植と実機動作確認が残課題。最新仕様は実装時に再 verify する。
