---
name: caw-setup
description: >
  caw を十分に使うための外部ツール（Python・poppler・python-pptx 等）の不足を検出し、
  計画を提示して一度の承認のうえ順番にインストールする。OS（macOS / Windows）を判定し、
  既に入っているものはスキップ。CLI/Node 自体の導入は配布リポジトリの bootstrap スクリプトへ誘導。
trigger: /caw-setup
---

# caw-setup — 前提ツールの検出と順次インストール

## いつ使うか

- ユーザーが「環境を整えて」「必要なツールを入れて」「セットアップして」と言ったとき
- `/caw` オンボーディング直後に、スライド・図・PDF 機能を使う予定なのに依存が無いとき
- スクリプト実行が `ModuleNotFoundError` や `command not found`（pdftoppm 等）で失敗したとき

このスキルは **CLI（Claude Code / Codex CLI）が既に動いている前提**なので、CLI 本体・Node.js の
導入は対象外（それらは鶏卵問題のため、配布リポジトリの `setup/caw-setup.sh` / `setup/caw-setup.ps1`
を案内する）。本スキルは **Python・poppler・Python パッケージ・任意ツール**の補完を担う。

## 安全方針（厳守）

- **計画提示 → 一度だけ承認 → 順番に実行**。各ツールごとに毎回確認はしない（任意ツールのみ個別確認）
- **冪等**：既に入っているものはスキップ
- **sudo / 管理者権限は使わない**。Homebrew（user 権限）/ winget / Scoop / pip --user の範囲で行う
- 各ステップの**成否を記録**し、失敗しても止めずに続行、最後にまとめて報告
- インストールは計画を提示して `[y/N]` 相当の同意を取ってから実行する

## ワークフロー

### Step 1: OS 判定

`uname -s` を実行。`Darwin` なら macOS、それ以外で Windows（`OS` 環境変数 = `Windows_NT`）なら Windows。
対応 OS は **macOS と Windows** のみ。判定できない場合はユーザーに確認する。

### Step 2: 現状チェック（冪等の素）

以下を `command -v`（macOS）/ `Get-Command`（Windows）で確認し、導入済み / 不足を表にまとめる：

| ツール | チェック | 必須度 |
|---|---|---|
| Python 3 | `python3` / `python` | 必須（スライド・図・PDF） |
| poppler | `pdftoppm` | PDF を扱うなら必須 |
| python-pptx / matplotlib / pillow / numpy | `python3 -c "import pptx, matplotlib, PIL, numpy"` | 必須 |
| GitHub CLI (gh) | `gh` | 任意 |
| LibreOffice | `soffice` | 任意 |

CLI 本体（`claude` / `codex`）・`node` も確認し、**無ければ** bootstrap スクリプトを案内（Step 5）。

### Step 3: 計画提示 → 承認（一度だけ）

不足ツールと、それぞれの**実行予定コマンド**（OS 別）を一覧で見せ、まとめて 1 回だけ同意を取る。

- macOS: `brew install <pkg>` / `python3 -m pip install <pkgs>`（PEP 668 で弾かれたら `--user --break-system-packages` で再試行）
- Windows: `winget install -e --id <id>` / poppler は `scoop install poppler`（Scoop 無ければ導入を提案）/ `python -m pip install <pkgs>`

Homebrew / winget / Scoop が前提として無い場合は、その導入も計画に含めて明示する。

### Step 4: 順番にインストール

承認後、上から順に実行。各ステップで「installing … → OK / FAIL」を表示。**必須 → Python パッケージ →
任意（任意のみ個別に y/N）** の順。失敗は記録して次へ進む。

### Step 5: CLI / Node が無い場合（bootstrap 誘導）

`claude`/`codex` や `node` が無い環境では、本スキルだけでは完結できない。配布リポジトリの
ワンステップ・スクリプトを案内する：

- macOS: `bash setup/caw-setup.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File setup/caw-setup.ps1`

これらは CLI・Node・git も含めて順番に導入する（同じ「計画提示 → 一括」方式）。

### Step 6: 動作確認と報告

```
node -v / git --version / python(3) --version / pdftoppm -v / claude --version
python -c "import pptx, matplotlib, PIL, numpy; print('python deps OK')"
```

導入済み / 今回入れた / 失敗 / 任意で見送り、を表で報告。最後に「`work/gaussian/_past-data/` 等に
過去データを入れて『取り込んで』と言うと Playbook を最適化できます」と次の一歩を添える。

## 重要な注意事項

- **対応 OS は macOS と Windows**。Windows の caw Hooks は bash なので Git Bash / WSL2 が要る点も伝える
- インストールコマンドは固定の信頼できるものだけを使い、ユーザー入力をそのままシェルに渡さない
- 失敗時はログ（bootstrap は一時ファイルに出力）と再実行方法を案内する
- 詳細な OS 別手順は LP「必要なツールとインストール」に対応
