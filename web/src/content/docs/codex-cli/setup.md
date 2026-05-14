---
title: 環境構築（Codex CLI）
description: Codex CLI のインストール、認証、caw プラグイン導入、.company/ 部署システムの初期化までの一通り
---

このページでは、Codex CLI をゼロから「化学プロジェクトで動く `.company/` 部署システム」が立ち上がるところまで一通り通します。**Codex CLI 自体に触るのが初めての方も対象**です。

## 動作環境

- **macOS**（Apple Silicon / Intel）
- **Linux**（主要ディストリビューション）
- **Windows**: WSL2 経由で Linux 同等の操作感

## インストール

### npm 経由（推奨）

```bash
npm install -g @openai/codex-cli
```

最新版へ更新：

```bash
npm update -g @openai/codex-cli
```

### 公式 docs

最新の正式な手順は [OpenAI Codex CLI 公式ドキュメント](https://github.com/openai/codex) を参照してください。

## 認証

初回起動時に認証フローが走ります：

```bash
codex
```

OpenAI アカウントでのログインを促されます。`codex login` で明示的にログイン、`codex logout` でログアウト。

## 初期確認

```bash
codex --version
codex --help
```

最初のセッション：

```bash
cd ~/your-project
codex
```

`/help` でヘルプ、`/quit` で終了。

## 推奨 IDE

Codex CLI は CLI ですが、**IDE** と組み合わせると体験が向上します。

| IDE | 特徴 | Codex CLI 連携 |
|---|---|---|
| **VS Code**（Microsoft） | 無料、最も普及、拡張エコシステム最大 | 内蔵ターミナルで `codex` 起動、diff ビュー利用可 |
| **Cursor** | VS Code フォーク、AI 機能内蔵 | VS Code 互換 + 独自 AI と Codex CLI を併用可能 |
| **JetBrains IDEs** | 言語別の高機能 IDE | 内蔵ターミナルで `codex` |

化学者の研究環境は Python 中心になることが多いので、**VS Code（無料）** か **Cursor** が無難。

## モデル + 思考レベル

Codex CLI は `~/.codex/config.toml` でデフォルトモデルと思考レベルを指定できます：

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"
```

セッション中の切り替えコマンドもあり（`codex --help` で確認）。

## `.company/` 部署システムの構築

研究プロジェクトの中心となる `.company/` 部署システムを構築します。**caw プラグイン**による自動構築を推奨。

### caw プラグインで自動構築（推奨）

`caw`（Chemist's AI Workflow）の Codex 版は、起動後に `caw` と入力（または「化学プロジェクトの環境を作って」など自然言語で指示）するだけで、研究分野・使用ソフト・ナレッジベース等を対話的にヒアリングし、化学者向けにカスタマイズされた `.company/` 部署と作業ディレクトリを一括で構築します。

#### 配布ステータス

- **Codex 1.2.1 公開済み（2026-05-14）**: 公式 marketplace（`dr-neoueda/chemist-ai-workflow`、MIT ライセンス）から導入可能。Claude Code 版と同じ 5 Skills（caw / caw-paper / caw-input / caw-playbook / caw-doctor）

#### Step 1: プラグインのインストール

Codex CLI のプラグイン管理は **marketplace 単位**です。marketplace を追加すると、含まれるプラグイン（caw）がそのまま利用可能になります（個別の `install` コマンドはありません）。

```bash
codex plugin marketplace add dr-neoueda/chemist-ai-workflow
```

`~/.codex/config.toml` に `[plugins."caw@chemist-ai-workflow"]` が追加されていれば導入完了。除去・更新の手順は [アンインストールと環境リセット](/codex-cli/uninstall/) を参照。

#### Step 2: オンボーディング

```bash
cd ~/your-research-project
codex
> caw
```

`.company/` が存在しない場合、対話的オンボーディングモードに入ります。

**研究プロファイル（4 問）**

1. 主な研究分野（有機化学・生命化学 / 物理化学・分析化学 / 材料・無機・結晶化学 / 計算化学・理論化学 等）
2. 使う計算ソフトのカテゴリ（量子化学 / 古典 MD / 周期系 DFT。複数選択可）
3. ナレッジベース（Notion / Obsidian / Logseq 等）
4. クラウドストレージ（Google Drive / Dropbox / OneDrive 等）

**部署選択**

立ち上げる部署を 7 つから複数選択（秘書部は常設）。

#### Step 3: 自動スキャフォールド

選択内容に応じて以下が一括生成されます。

| 場所 | 内容 |
|---|---|
| `.company/AGENTS.md` | ルート組織図 + 化学者向け運用ルール |
| `.company/secretary/` | 秘書部（窓口・TODO・意思決定ログ・学び） |
| `.company/<選択部署>/` | 選択した各部署の AGENTS.md とサブフォルダ |
| `.company/computation/playbooks/` | 選択した計算ソフトの Playbook 雛形 |
| ルート直下 `gaussian/` `orca/` 等 | 選択した計算ソフトの作業ディレクトリ（README 付き） |
| ルート直下 `papers/` `manuscripts/` `slides/` | 選択した部署に対応するドメイン作業ディレクトリ |

詳細な部署構成・スキャフォールド内容は [配布プラグイン（caw）](/plugin/) を参照（Claude Code 版と同じ部署構成）。

### 手動セットアップ（caw を使わない場合）

`caw` プラグインを使わずに `.company/` を手動で構築することも可能です。Claude Code 用の [手動セットアップ手順](/claude-code/setup/) と同じ流れで、各 `CLAUDE.md` を `AGENTS.md` に置き換えるだけで Codex 環境にも対応できます。

## 試運転

`codex` セッションを起動し、秘書を窓口にして以下のように対話できます。

| 入力例 | 動作 |
|---|---|
| 「今日の TODO を整理して」 | `secretary/todos/YYYY-MM-DD.md` を表示・編集 |
| 「ORCA で benzene の構造最適化の雛形を作って」 | `orca/<system>_<purpose>_<YYYYMMDD>/` を作成し `.inp` 雛形 + `.company/computation/jobs/` にジョブ記録 |
| 「読んだ論文を登録して」 | PDF → `.company/research/papers/<author-year>.md` に書誌情報付き md を生成 |
| 「ここまでの会話で決めたことを記録して」 | `secretary/notes/YYYY-MM-DD-decisions.md` に追記 |

オンボーディング（caw 版）または初期セットアップ（手動版）は初回のみ。2 回目以降の起動は既存の `.company/` を検出し、自動的に運営モードに入ります。

## 次のステップ

- [Codex CLI トップ](/codex-cli/) — Codex CLI 全体像
- [配布プラグイン（caw）](/plugin/) — caw の含まれる内容（Claude Code 版・Codex 版共通）
- [対応ツール一覧](/tools/) — 計算ソフト・ナレッジベース・クラウドストレージのマトリクス
