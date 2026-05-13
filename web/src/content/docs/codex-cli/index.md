---
title: "Tier 2: Codex CLI"
description: OpenAI 製のターミナル CLI エージェント。AGENTS.md ベースで Claude Code 同等のワークフローを再現し、caw プラグインが公式マーケットプレイス経由で導入可能
---

OpenAI 公式のターミナル CLI エージェント。**AGENTS.md** を標準としてプロジェクトルールを記述する。Claude Code 派と Codex CLI 派が混在する研究室でも、同じ caw メソッドを共有できる。

## caw プラグイン（Codex 版）導入

```bash
codex plugin marketplace add dr-neoueda/chemist-ai-workflow
codex plugin install caw
```

`codex plugin list` で `caw` が `enabled` 表示されれば導入完了。

## クイックスタート

```bash
cd ~/your-research-project
codex
> /caw
```

`.company/` が存在しない場合、対話的オンボーディング（研究プロファイル 4 問 + 部署選択）が起動し、化学者向けにカスタマイズされた部署と作業ディレクトリが一括生成される。生成される指示ファイルは Codex CLI の標準である **AGENTS.md** 形式。

詳細手順は [環境構築](/codex-cli/setup/) を参照。

## なぜ Codex CLI を Tier 2 に置くか

- **OpenAI 系モデル（GPT-5 系）を活用できる**：Claude Code が Anthropic 系であるのに対し、研究室のメンバー構成や所属機関の契約に応じて選択肢を持てる
- **AGENTS.md は universal な標準**：Codex CLI / Gemini CLI 等の他 CLI エージェントも参照可能で、将来的にエージェント乗り換えが容易
- **異なるレビュー観点が得られる**：Claude = 構文 / DRY、Codex = 物理意味論という棲み分けの実例あり（応用編で詳述）
- **Anthropic 単独依存リスクの回避策**

## Claude Code 版との関係

| 観点 | Claude Code 版 | Codex 版 |
|---|---|---|
| インストール | `/plugin install caw@chemist-ai-workflow` | `codex plugin install caw` |
| プラグイン構造 | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` |
| 生成される指示ファイル | `<dept>/CLAUDE.md` | `<dept>/AGENTS.md` |
| 部署テンプレ内容 | 同一 | 同一 |
| Playbook 雛形 | 同一 | 同一 |
| 配布元 | `dr-neoueda/chemist-ai-workflow`（同一リポジトリ） | 同左 |

両版は同じ `chemist-ai-workflow` リポジトリから並列配信。研究室で Claude Code 派と Codex CLI 派が混在しても、共通の `.company/` メソッドで運用できる。

## 章立て

1. [Codex CLI セットアップ + caw プラグイン導入](/codex-cli/setup/)
2. `AGENTS.md` の書き方 — Claude Code の `CLAUDE.md` との対応（執筆予定）
3. ルールの記述方法と粒度（執筆予定）
4. [Claude + Codex 二段レビュー連携](/claude-code/two-stage-review/)（応用編、Claude Code 章を参照）

## 著者メモ（応用編）

実例：MD 自由エネルギー計算で Widom 式の `-RT` 項抜けを Codex が検出し、ナレッジベース登録前に補正。構文・DRY は Claude が、物理意味論は Codex が拾うという役割分担が有効。

詳細は [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) を参照。AI エージェント運用に慣れてからの導入を推奨します。

## ステータス

**caw v1.0.0（2026-05-13）公開済み**：マーケットプレイス（`dr-neoueda/chemist-ai-workflow`）経由で導入可能。Claude Code 版（`/caw`）と内容は基本同一で、AGENTS.md ターゲットに対応。
