---
title: はじめての方へ（ターミナル・IDE の基本）
description: パソコンのターミナルや IDE、AI エージェントを触ったことがない方に向けた、用語のやさしい説明と最初の準備（VS Code の導入・ターミナルの開き方・最初の起動）
---

このページは、**ターミナル・IDE・AI エージェントを触ったことがない方**を対象に、最初の一歩だけを案内します。
専門用語は最小限にし、出てくるものは 1 行で説明します。

## まずは用語をやさしく

| 用語 | かんたんに言うと |
|---|---|
| **ターミナル** | 文字でパソコンに指示を出す画面。マウスの代わりにコマンド（短い命令文）を打つ場所 |
| **コマンド** | ターミナルに打ち込む短い命令文。基本は「コピーして貼り付け → Enter」でよい |
| **IDE** | プログラムやファイルを編集する高機能エディタ。VS Code が定番。ターミナルも中に入っている |
| **AI エージェント** | 指示すると自分で考えて作業してくれる AI。caw は Claude Code / Codex CLI / GitHub Copilot CLI の上で動く |
| **caw** | Chemist's AI Workflow。研究の「研究以外」を手伝う AI 部署システム。秘書に話しかけるだけ |
| **MCP** | AI と外部サービス（Notion・Google Drive 等）をつなぐ仕組み。設定すれば連携が増える |
| **Hook** | 特定のタイミングで自動実行される小さな処理。caw では学びの記録などに使われる |

困ったら、caw の中で「**〇〇って何?**」と聞けば、その場でやさしく説明します。

## 準備の全体像（3 つだけ）

1. **VS Code を入れる**（編集とターミナルが 1 画面でできる）
2. **必要なツールを入れる**（自動セットアップスクリプトが順番にやってくれる）
3. **caw を入れて起動する**

順番に説明します。対応 OS は **Windows** と **macOS** です。

## 1. VS Code を入れる

[VS Code 公式サイト](https://code.visualstudio.com/) からインストーラをダウンロードして実行します（無料）。

- **Windows**: ダウンロードした `.exe` を実行し、画面の指示どおり進めます
- **macOS**: ダウンロードした `.zip` を展開し、出てきた「Visual Studio Code」を「アプリケーション」フォルダへ移動します

インストール後、VS Code を起動します。

## 2. VS Code でターミナルを開く

VS Code のメニューから **「ターミナル（Terminal）」→「新しいターミナル（New Terminal）」** を選びます。
画面の下半分に文字を打つ欄が出れば成功です。ここに以降のコマンドを「コピーして貼り付け → Enter」します。

:::note
Windows で **Claude Code 版** の caw を使う場合のみ、一部の機能（Hooks）が **Git Bash** という環境を使います（次の手順で Git も入ります）。
**Codex CLI / GitHub Copilot CLI 版には Hooks が無い**ため、標準の **PowerShell** だけで動き、Git Bash は不要です。
:::

## 3. 必要なツールと caw を入れる

[必要なツールとインストール](/requirements/) の **自動セットアップスクリプト**を使うのが一番簡単です。
ターミナルに次を貼り付けて Enter すると、何を入れるか一覧で確認したうえで順番に入ります。

```bash
# macOS
curl -fsSL https://raw.githubusercontent.com/dr-neoueda/chemist-ai-workflow/main/setup/caw-setup.sh -o caw-setup.sh
bash caw-setup.sh
```

```powershell
# Windows（PowerShell）
iwr https://raw.githubusercontent.com/dr-neoueda/chemist-ai-workflow/main/setup/caw-setup.ps1 -OutFile caw-setup.ps1
powershell -ExecutionPolicy Bypass -File caw-setup.ps1
```

終わったら、研究用のフォルダに移動して AI エージェントを起動します。

```bash
cd ~/your-research-project
claude
```

最初に `/caw` と打つと、セットアップが始まります。そこで **「はじめて」モード**を選ぶと、以後 caw が
**強めに手を引いて**くれます（毎回「次はこれをしましょう」と提示し、専門用語はその都度説明し、
取り消せない操作は必ず確認します）。プロジェクト直下にできる **`はじめにお読みください.md`** も最初に開いてください。

## 次のステップ

- [必要なツールとインストール](/requirements/) — 入れるものの一覧と OS 別の詳細
- [Claude Code の環境構築](/claude-code/setup/) — 認証・IDE 連携・モデル切替まで
- [配布プラグイン（caw）](/plugin/) — caw でできることの全体像
