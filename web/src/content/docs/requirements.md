---
title: 必要なツールとインストール
description: caw を十分に活用するために別途用意するソフトウェアと、Windows / macOS 別のインストール手順
---

## 対応 OS

caw が対象とする OS は **Windows** と **macOS** の 2 つです。どちらでもコア機能・Python 機能ともに利用できます。

## caw 本体と「十分に使う」ための差

caw のコア（オンボーディング、部署スキャフォールド、Playbook、運営モード）は markdown ベースのワークフローで動くため、AI CLI が 1 つあれば動作します。

一方で、**スライド生成・図の作成・PDF からの図／メタデータ抽出・解析スクリプト**といった機能まで十分に活かすには、下記の外部ツールを別途用意する必要があります。本ページでは、それらを Windows / macOS 別にまとめます。

## 必要なものの一覧

| 区分 | ツール | 役割 | 必須度 |
|---|---|---|---|
| 土台 | AI CLI（Claude Code または Codex CLI） | caw の実行環境 | いずれか必須 |
| 土台 | Node.js（LTS） | Claude Code 本体・npx ベースの MCP サーバー | 必須 |
| 土台 | git | プラグインの取得・バージョン管理 | 必須 |
| Python<br />機能 | Python 3.12 以上 | スライド・図・解析・PDF 処理の基盤 | 十分活用に必須 |
| Python<br />機能 | python-pptx / matplotlib / pillow / numpy | caw-slides の図・スライド生成 | 同上 |
| PDF 処理 | poppler（pdftoppm / pdftotext / pdfinfo） | 論文 PDF の図抽出・メタデータ抽出 | PDF を扱うなら必須 |
| Windows のみ | Git Bash または WSL2 | Hooks（bash スクリプト）の実行 | Windows で必須 |
| 任意 | GitHub CLI（gh） | engineering / review 部署の PR ワークフロー | 任意 |
| 任意 | LibreOffice | 生成した pptx を画像化して目視確認 | 任意 |
| 任意 | RDKit / ASE / pymatgen / MDAnalysis / cclib | 研究内容に応じた解析・前処理 | 任意 |
| 推奨 | VS Code または Cursor | 編集・diff・ターミナル統合 | 推奨 |

:::note
Python パッケージはシステム環境を汚さないよう、仮想環境（`python -m venv` など）に入れることを推奨します。
:::

## 一番かんたん：自動セットアップスクリプト

1 つずつ手で入れるのが不安な場合は、配布リポジトリの **セットアップスクリプト**が便利です。OS を判定し、
不足しているものを検出 → **やることを一覧で提示 → 一度だけ承認 → 順番にインストール**します（既に入って
いるものはスキップ）。

```bash
# macOS（ダウンロードして実行）
curl -fsSL https://raw.githubusercontent.com/dr-neoueda/chemist-ai-workflow/main/setup/caw-setup.sh -o caw-setup.sh
bash caw-setup.sh
```

```powershell
# Windows（PowerShell でダウンロードして実行）
iwr https://raw.githubusercontent.com/dr-neoueda/chemist-ai-workflow/main/setup/caw-setup.ps1 -OutFile caw-setup.ps1
powershell -ExecutionPolicy Bypass -File caw-setup.ps1
```

:::tip
すでに Claude Code / Codex CLI が動く環境なら、CLI の中で **`/caw-setup`**（Codex では「環境を整えて」）と
言うだけで、不足ツールの検出から導入まで同じ「計画提示 → 一括」方式で行えます。
:::

以下は、何が入るのかを把握したい場合の **手動インストール手順**です。

## macOS でのインストール

パッケージ管理には [Homebrew](https://brew.sh/) を使うのが簡単です。未導入の場合は公式手順で先に Homebrew を入れてください。

```bash
# 土台（Node.js / git / Python / poppler）
brew install node git python poppler

# AI CLI（Claude Code）
npm install -g @anthropic-ai/claude-code
# Codex CLI を使う場合（任意）
npm install -g @openai/codex

# Python パッケージ（caw-slides の図・スライド生成）
python3 -m pip install python-pptx matplotlib pillow numpy

# 任意：PR ワークフロー / pptx 目視確認
brew install gh
brew install --cask libreoffice
```

- **bash**：macOS には標準搭載のため、Hooks はそのまま動きます。
- **日本語フォント**：ヒラギノが標準搭載で、matplotlib が自動検出します（追加インストール不要）。
- 著者環境は macOS（Apple Silicon）です。

## Windows でのインストール

パッケージ管理には標準の [winget](https://learn.microsoft.com/windows/package-manager/) を使えます。poppler だけは winget に無いため、[Scoop](https://scoop.sh/) か conda を併用します。

```powershell
# 土台（Node.js / git＝Git Bash 同梱 / Python / gh / LibreOffice）
winget install OpenJS.NodeJS.LTS
winget install Git.Git
winget install Python.Python.3.12
winget install GitHub.cli
winget install TheDocumentFoundation.LibreOffice

# AI CLI（Claude Code）
npm install -g @anthropic-ai/claude-code
# Codex CLI を使う場合（任意）
npm install -g @openai/codex

# Python パッケージ
py -m pip install python-pptx matplotlib pillow numpy

# poppler（Scoop 経由。または conda install -c conda-forge poppler）
scoop install poppler
```

- **bash（Hooks 用）**：caw の Hooks は bash スクリプトです。`Git.Git` に同梱される **Git Bash** で動きます。WSL2 を使う場合は PowerShell で `wsl --install` を実行してください。
- **Python の PATH**：インストーラ利用時は「Add python.exe to PATH」を必ず有効にします。`py` ランチャー経由でも実行できます。
- **日本語フォント**：MS Gothic / Yu Gothic が標準搭載で matplotlib が自動検出します。図に □（豆腐）が出る場合は、フォント名を明示するか日本語フォントパッケージを追加してください。

## インストール後の動作確認

Windows / macOS 共通で、以下が表示されれば土台は揃っています。

```bash
node -v
git --version
python --version        # Windows は py --version でも可
claude --version
pdftoppm -v             # poppler
python -c "import pptx, matplotlib, PIL, numpy; print('python deps OK')"
```

## 関連ページ

- [Claude Code の環境構築](/claude-code/setup/) — Claude Code のインストール・認証・IDE 連携の詳細
- [Codex CLI の環境構築](/codex-cli/setup/) — Codex CLI を使う場合
- [対応ツール一覧](/tools/) — ナレッジベース・クラウドストレージ・計算ソフト・執筆環境の対応状況
- [配布プラグイン（caw）](/plugin/) — プラグイン本体の導入とスキル一覧
