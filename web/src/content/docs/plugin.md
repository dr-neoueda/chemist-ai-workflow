---
title: 配布プラグイン（caw）
description: Chemist's AI Workflow プラグイン — 部署システム・Playbook・スキル一式を Claude Code に一括導入
---

本商品の中核成果物は、Claude Code プラグイン **`caw`（Chemist's AI Workflow）** として配布されます。化学研究プロジェクトで使う AI 部署システム・Playbook・スキルを一式まとめて提供する MIT ライセンスの OSS プラグインです。

## プラグインの位置付け

化学研究には、汎用 AI エージェント運用がカバーしない領域があります：

- **計算ソフト Playbook**：Gaussian / GROMACS / CP2K / VASP / ORCA / Quantum ESPRESSO など、CLI ベースの計算ソフト全般の「既知の罠と処方」
- **論文管理パイプライン**：PDF → ナレッジベース + クラウドストレージ（[対応ツール一覧](/tools/) のマトリクスに準拠）
- **申請書ワークフロー**：学振 DC2 / 科研費 等の文体プロファイル + 字数制約
- **LaTeX / Word 両対応**：[論文執筆](/tools/) で示した実装パスをスキル化
- **段階的な習熟**：Claude Code 未経験者向けの初期セットアップから、AI 分業運用に慣れた読者向けの応用機能まで

`caw` プラグインはこれらを **一括配布** します。

## インストール

### Claude Code 版

```bash
claude
> /plugin marketplace add dr-neoueda/chemist-ai-workflow
> /plugin install caw
```

`/plugin list` で `caw` が `enabled` 表示されれば導入完了。

### Codex CLI 版

```bash
codex plugin marketplace add dr-neoueda/chemist-ai-workflow
codex plugin install caw
```

`codex plugin list` で `caw` が `enabled` 表示されれば導入完了。Claude Code 版と同一のリポジトリから配信され、内容は基本同一（生成される指示ファイルが `CLAUDE.md` → `AGENTS.md` に変わる点のみ）。

導入後の起動：

```bash
cd ~/your-research-project
codex
> caw
```

Codex CLI ではスラッシュ不要。`caw` と入力するか、「化学プロジェクトの環境を作って」など自然言語で指示すれば、スキルが発火します。

### 両 CLI の起動作法（比較）

| エージェント | インストール | 起動 |
|---|---|---|
| Claude Code | `/plugin marketplace add ...` → `/plugin install caw` | `/caw` |
| Codex CLI | `codex plugin marketplace add ...` → `codex plugin install caw` | `caw`（または自然言語） |

Claude Code はスキル発火を `/` 構文に統合、Codex CLI は `/` を明示的コマンド専用に予約しスキルは自然言語マッチで発火する設計の違いがあります。

## クイックスタート

```bash
cd ~/your-research-project
claude
> /caw
```

`.company/` が存在しない場合、対話的オンボーディングが起動し、研究プロファイル（4 問）と立ち上げる部署を選択。選択内容に応じて、`.company/` 部署と作業ディレクトリ（`gaussian/`、`papers/` 等）が一括生成されます。

2 回目以降の `/caw` は運営モードで起動し、秘書を窓口にした対話型の研究支援に入ります。

詳細手順は [環境構築](/claude-code/setup/) を参照。

## 現バージョン（v1.1.0）に含まれる内容

| カテゴリ | 内容 |
|---|---|
| **Skills** | `/caw`（オンボーディング → 自動スキャフォールド → 運営モード）<br>`/caw-paper`（論文検索 + PDF メタデータ抽出 + ナレッジベース・クラウドストレージ自動登録）<br>`/caw-input`（6 ソフトの入力ファイル雛形生成 + ジョブ記録）<br>`/caw-playbook`（計算 log 解析 → Lessons Learned 自動追記） |
| **Hooks** | SessionStart で `.company/secretary/notes` と関連 Playbook を自動注入、Stop で学びの記録漏れをリマインド |
| **部署テンプレート** | secretary / research / engineering / computation / analysis / writing / review / presentation の 8 部署 CLAUDE.md |
| **Playbook 雛形** | Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用 |
| **作業ディレクトリ** | 選択した計算ソフトに応じて `gaussian/` / `orca/` 等、選択した部署に応じて `papers/` / `manuscripts/` / `slides/` を自動生成 |

## 今後の機能拡張

| 予定機能 | 内容 |
|---|---|
| `caw-apply` | 申請書ワークフロー（文体プロファイル + 字数制約） |
| `caw-chem-reviewer` | 化学物理意味論レビュー（応用編） |

## 配布計画

| Phase | 期間 | 内容 |
|---|---|---|
| Phase 1 | 2026-05 | スケルトン構築、`/caw` スキル設計、ローカル実機テスト ✅ |
| Phase 2 | 2026-05-13 | マーケットプレイス公開（v1.0.0）✅ |
| Phase 3 | 2026-05-13 | 追加スキル（`/caw-paper` / `/caw-input` / `/caw-playbook`）+ Hooks 実装、v1.1.0 公開 ✅ |
| Phase 4 | 2026-06〜 | ベータユーザー試用、フィードバック反映、`caw-apply` 等の応用スキル追加 |
| Phase 5 | 2026-07〜 | 商品配布物として組み込み |

## 開発リポジトリ

- **公開先**: [`dr-neoueda/chemist-ai-workflow`](https://github.com/dr-neoueda/chemist-ai-workflow)（GitHub、MIT ライセンス、Claude Code + Codex CLI 並列配信）

**Claude Code 版（`plugin/`）**:
- `.claude-plugin/marketplace.json` ─ Claude Code 用マーケットプレイス manifest
- `plugin/.claude-plugin/plugin.json` ─ プラグインマニフェスト
- `plugin/skills/caw/SKILL.md` ─ メインスキル（trigger: `/caw`）
- `plugin/skills/caw/references/claude-md-template.md` ─ ルート CLAUDE.md 生成テンプレ
- `plugin/skills/caw/references/chemistry-departments.md` ─ 8 部署 CLAUDE.md テンプレ集
- `plugin/skills/caw/references/playbook-starters.md` ─ 計算ソフト Playbook 雛形（Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用）

**Codex CLI 版（`codex-plugin/`）**:
- `.agents/plugins/marketplace.json` ─ Codex 用マーケットプレイス manifest
- `codex-plugin/.codex-plugin/plugin.json` ─ プラグインマニフェスト
- `codex-plugin/skills/caw/SKILL.md` ─ メインスキル（trigger: `/caw`、AGENTS.md ターゲット）
- `codex-plugin/skills/caw/references/agents-md-template.md` ─ ルート AGENTS.md 生成テンプレ
- `codex-plugin/skills/caw/references/chemistry-departments.md` ─ 8 部署 AGENTS.md テンプレ集
- `codex-plugin/skills/caw/references/playbook-starters.md` ─ 計算ソフト Playbook 雛形（Claude Code 版と同一）

## ライセンス

MIT License。商用・私用問わず自由に利用・改変・再配布可能（コピーライト表示を残すこと）。

## ステータス

**v1.1.0（2026-05-13）公開**：マーケットプレイス経由で導入可能。`/caw` の基本フローに加え、`/caw-paper` / `/caw-input` / `/caw-playbook` の追加スキルと Hooks（SessionStart / Stop）が同梱。
