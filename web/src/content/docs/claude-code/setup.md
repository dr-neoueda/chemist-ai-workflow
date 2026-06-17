---
title: 環境構築
description: Claude Code のインストール、認証、IDE 連携、モデル設定、office/ 初期化までの一通り
---

このページでは、Claude Code をゼロから「化学プロジェクトで動く `office/` 部署システム」が立ち上がるところまで、一通り通します。**Claude Code 自体に触るのが初めての方も対象**です。

## 動作環境

caw の対応 OS は **Windows** と **macOS** です。

- **macOS**（Apple Silicon / Intel）
- **Windows**：Claude Code はネイティブ動作。caw の Hooks は bash スクリプトのため、Git Bash または WSL2 を併用します

必要な外部ツールと OS 別のインストール手順は [必要なツールとインストール](/requirements/) にまとめています。著者環境は macOS Tahoe（M5 Max, 128 GB RAM）。

## インストール

### npm 経由（推奨）

```bash
npm install -g @anthropic-ai/claude-code
```

最新版へ更新：

```bash
npm update -g @anthropic-ai/claude-code
```

### 公式 docs

最新の正式な手順は [Anthropic 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code) を参照してください。本ページの内容は変わる可能性があり、Phase 2 開始時に再 verify します。

## 認証

初回起動時に認証フローが走ります：

```bash
claude
```

ブラウザが開き、Anthropic Console でのログイン後、CLI に戻ってきます。

API キー直接指定も可能：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

ログアウトは `claude --logout`。

## 初期確認

```bash
claude --version
claude --help
```

最初のセッション：

```bash
cd ~/your-project
claude
```

`/help` でヘルプ、`/quit` で終了。

## 推奨 IDE

Claude Code は CLI ですが、**IDE（統合開発環境、Integrated Development Environment）** と組み合わせると体験が大きく向上します。エディタとファイルツリー、ターミナル、git 操作を一画面で扱えるためです。

### 主要な IDE 選択肢

| IDE | 特徴 | Claude Code 連携 |
|---|---|---|
| **VS Code**（Microsoft） | 無料、最も普及、拡張エコシステム最大 | 公式拡張機能あり、内蔵ターミナルで `claude` 起動、Edit / Write 結果を diff で表示 |
| **Cursor** | VS Code フォーク、AI 機能内蔵 | VS Code 互換 + 独自 AI（タブ補完など）と Claude Code を併用可能 |
| **JetBrains IDEs**（PyCharm / IntelliJ / WebStorm 等） | 言語別の高機能 IDE、リファクタリング・デバッガが強い | プラグインで連携、内蔵ターミナルで `claude` |
| **Zed** | 軽量・高速、Rust 製 | Claude 統合あり |
| **Windsurf**（Codeium） | AI-first エディタ | ターミナル統合 |

### IDE で Claude Code を使うメリット

- ターミナル + エディタ + ファイルツリーが 1 画面で完結
- Claude の Edit / Write 結果が IDE の **diff ビュー**で視覚的に確認できる
- 拡張機能でショートカット化・パネル化
- Git の操作（commit, branch, blame）が GUI で並行できる
- 化学プロジェクトでは `.csv` / `.pdb` / `.mol2` / `.xyz` / `.log` / Jupyter Notebook など多様なファイルを扱うため、IDE の preview / プラグインが便利
- VS Code / Cursor は **Python 拡張**が成熟しており、numpy / pandas / matplotlib のホバー表示・型補完・デバッガが揃う

### 推奨：VS Code または Cursor から始める

化学者の研究環境は Python が中心になることが多いので、**VS Code（無料）** か **Cursor（VS Code 互換 + AI 内蔵）** が無難です。Cursor は VS Code との設定互換性があるため、後から乗り換えも容易。

JetBrains 派（PyCharm 愛用者）なら、そのまま PyCharm の内蔵ターミナルで `claude` を起動するだけで運用できます。

## モデル + 思考レベル切替

Claude Code は **モデル**と**思考レベル**の 2 軸で挙動を調整できます。

### モデル切替（`/model`）

| モデル | 用途 |
|---|---|
| **Sonnet 4.6** | 日常のコーディング・執筆（バランス型、デフォルト） |
| **Opus 4.7** | 複雑な設計判断・大規模リファクタ・research・架空シナリオ検討 |
| **Haiku 4.5** | 大量並列の小タスク・ライトな実行・コスト削減 |

`/model` コマンドでセッション中に切り替え可能。

### 思考レベル切替（`/effort`）

`/effort` コマンドで **Claude が推論にかける深さ**を変更できます：

| レベル | 性質 | 化学プロジェクトでの使い分け例 |
|---|---|---|
| **low** | 速く軽く | バッチ処理・繰り返しタスク・テンプレ生成 |
| **medium** | バランス（デフォルト） | 計算入力ファイル生成・log 解析・通常の対話 |
| **high** | 深く考える | 複雑な実験設計の議論・難しいデバッグ・申請書の論理構成 |

タスクの複雑さに応じて使い分けることでコストと品質のバランスが取れます。同じセッション内で何度でも切り替え可能。

## `office/` 部署システムの構築

研究プロジェクトの中心となる `office/` 部署システムを構築します。本書では **`caw` プラグイン**による自動構築を推奨します。プラグインを使わない手動セットアップも代替ルートとして利用可能です。

### caw プラグインで自動構築（推奨）

`caw`（Chemist's AI Workflow）は本書の中核成果物として配布される Claude Code プラグインです。`/caw` 1 コマンドで研究分野・使用ソフト・ナレッジベース等を対話的にヒアリングし、化学者向けにカスタマイズされた `office/` 部署と作業ディレクトリを一括で構築します。

#### 配布ステータス

- **v1.0.0 公開済み（2026-05-13）**: 公式 marketplace（`dr-neoueda/chemist-ai-workflow`、MIT ライセンス）から導入可能
- **今後の機能拡張**: 追加スキル（`caw-paper` / `caw-playbook` / `caw-input` / `caw-apply`）と Hooks を順次追加予定（詳細は [配布プラグイン（caw）](/plugin/) 参照）

#### Step 1：プラグインのインストール

```bash
claude
> /plugin marketplace add dr-neoueda/chemist-ai-workflow
> /plugin install caw
```

`/plugin list` で `caw` が `enabled` 表示されれば導入完了。

#### Step 2：オンボーディング

```bash
cd ~/your-research-project
claude
> /caw
```

`office/` が存在しない場合、`caw` は対話的なオンボーディングモードに入ります。

**研究プロファイル（4 問）**

1. 主な研究分野（有機化学・生命化学 / 物理化学・分析化学 / 材料・無機・結晶化学 / 計算化学・理論化学 等）
2. 使う計算ソフトのカテゴリ（量子化学 / 古典 MD / 周期系 DFT。複数選択可）
3. ナレッジベース（Notion / Obsidian / Logseq 等）
4. クラウドストレージ（Google Drive / Dropbox / OneDrive 等）

**部署選択**

立ち上げる部署を 7 つから複数選択（秘書部は常設）。

#### Step 3：自動スキャフォールド

選択内容に応じて以下が一括生成されます。

| 場所 | 内容 |
|---|---|
| `office/CLAUDE.md` | ルート組織図 + 化学者向け運用ルール |
| `office/secretary/` | 秘書部（窓口・TODO・意思決定ログ・学び） |
| `office/<選択部署>/` | 選択した各部署の CLAUDE.md とサブフォルダ |
| `office/computation/playbooks/` | 選択した計算ソフトの Playbook 雛形 |
| ルート直下 `work/gaussian/` `work/orca/` 等 | 選択した計算ソフトの作業ディレクトリ（README 付き） |
| ルート直下 `work/papers/` `work/manuscripts/` `slides/` | 選択した部署に対応するドメイン作業ディレクトリ |

詳細な部署構成・スキャフォールド内容は [配布プラグイン（caw）](/plugin/) を参照。

### 手動セットアップ（caw を使わない場合）

`caw` プラグインを使わずに `office/` を手動で構築することも可能です。プラグインの動作をカスタマイズしたい場合や、テンプレートの中身を学びながら段階的に立ち上げたい場合に利用してください。

<details>
<summary>手動セットアップ手順を展開</summary>

#### Step 1：プロジェクトに `office/` を作る

```bash
cd ~/your-research-project
mkdir -p office/secretary/{inbox,todos,notes}
```

これで秘書部の最小構成が立ち上がります。

#### Step 2：ルート CLAUDE.md を配置

`office/CLAUDE.md`：

```md
# Company - 仮想組織管理システム

## オーナープロフィール
- 専門：（例）有機化学
- 目標：研究プロセスの AI 化、論文・計算ジョブの効率化

## 組織構成
office/
└── secretary/    ← 窓口・TODO・壁打ち・意思決定

## 運営ルール
- ユーザーとの対話はまず秘書が受け取る
- 部署が必要になったら office/<部署名>/ を新設、CLAUDE.md を置く
- 同じ日付のファイルは追記、新規作成しない
```

#### Step 3：秘書部の CLAUDE.md

`office/secretary/CLAUDE.md`：

```md
# 秘書室

## 役割
窓口、TODO 管理、壁打ち、意思決定ログ

## 口調
丁寧だが堅すぎない。主体的に提案する。

## ルール
- TODO: todos/YYYY-MM-DD.md
- ノート: notes/YYYY-MM-DD-<topic>.md
- 意思決定: notes/YYYY-MM-DD-decisions.md
- 同日 1 ファイル、追記専用
```

#### Step 4：研究で使う部署を増やす

化学プロジェクトでよく使う部署は以下の 7 つです：

| 部署 | 役割 | 化学者向けの典型タスク |
|---|---|---|
| **research** | 文献調査 | 論文検索、要約、ナレッジベース登録 |
| **engineering** | Python ツール開発 | 計算入力ジェネレータ、解析スクリプト、CLI |
| **computation** | 計算ジョブ管理 + Playbook | Gaussian / GROMACS / CP2K / VASP 等 CLI 系計算ソフト |
| **analysis** | データ解析 | 解析スクリプト、可視化、統計処理 |
| **writing** | 論文執筆 | LaTeX / Word 原稿、図表、参考文献 |
| **review** | コード/計算レビュー | コード品質・計算妥当性の確認 |
| **presentation** | スライド生成 | python-pptx + matplotlib + RDKit |

各部署は `mkdir -p office/<name>/<sub>` でディレクトリを作り、`<name>/CLAUDE.md` に役割と運用ルールを記述。最初に使う部署すべてを立ち上げると、後から個別追加する手間を抑えられる。

#### Step 5：作業ディレクトリ

実研究データを置く作業ディレクトリも手動で用意します。

```bash
# 計算ソフト用（使うものだけ）
mkdir -p gaussian gromacs cp2k orca vasp quantum-espresso

# ドメイン作業（使うものだけ）
mkdir -p papers manuscripts slides
```

各ディレクトリに README.md を 1 枚配置して「何を置くか」を明示することを推奨。

</details>

### 試運転

どちらの構築方法でも運営モードは同じです。`claude` セッションを起動し、秘書を窓口にして以下のように対話できます。

| 入力例 | 動作 |
|---|---|
| 「今日の TODO を整理して」 | `secretary/todos/YYYY-MM-DD.md` を表示・編集 |
| 「Gaussian で benzene の構造最適化の雛形を作って」 | `work/gaussian/<system>_<purpose>_<YYYYMMDD>/` を作成し `.gjf` 雛形 + `office/computation/jobs/` にジョブ記録 |
| 「読んだ論文を登録して」 | PDF → `work/papers/<author-year>.md` に書誌情報付き md を生成、`work/papers/` のステージング PDF と紐付け |
| 「ここまでの会話で決めたことを記録して」 | `secretary/notes/YYYY-MM-DD-decisions.md` に追記 |

オンボーディング（caw 版）または初期セットアップ（手動版）は初回のみ。2 回目以降の起動は既存の `office/` を検出し、自動的に運営モードに入ります。

部署設計の詳細は [office/ 部署テンプレート](/claude-code/company-template/) を参照。

## 次のステップ

- [設定の階層と基礎](/claude-code/basics/) — `~/.claude/` と `.claude/`、`settings.json` の使い分けを理解
- [office/ 部署テンプレート](/claude-code/company-template/) — 部署を増やす判断基準と典型例
- [Skills の作り方](/claude-code/skills/) — プロジェクト固有のメソッドを独自スキル化
