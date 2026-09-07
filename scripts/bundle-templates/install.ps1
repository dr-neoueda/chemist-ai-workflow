# caw オフライン導入インストーラ（Windows / PowerShell）
#
# USB メモリの中でこのファイルを右クリック →「PowerShell で実行」
# またはプロンプトで:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#
# このスクリプトがやること:
#   1. USB の中身を、あなたの PC の中（既定 %USERPROFILE%\caw-plugin）にコピーする
#   2. お使いの AI CLI に「そのコピー先」を登録する
#   3. caw プラグインをインストールする
#
# ★ なぜコピーするのか
#   USB のパスを直接登録すると、USB を抜いた時点で caw が動かなくなります。
#   （ローカルパスの marketplace は、その場所を参照し続ける仕様のため）
#   なので必ず PC の中にコピーしてから登録します。

$ErrorActionPreference = 'Stop'

$Src  = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dest = if ($env:CAW_DEST) { $env:CAW_DEST } else { Join-Path $env:USERPROFILE 'caw-plugin' }
$Marketplace = 'chemist-ai-workflow'

function Say  ($m) { Write-Host $m }
function OK   ($m) { Write-Host "[OK] $m"   -ForegroundColor Green }
function Warn ($m) { Write-Host "[!] $m"    -ForegroundColor Yellow }
function Err  ($m) { Write-Host "[X] $m"    -ForegroundColor Red }

Say ''
Say 'caw（化学者のための AI エージェント導入伴走）オフライン導入'
Say "  コピー元: $Src"
Say "  コピー先: $Dest"
Say ''

# --- 0. 中身の確認 ----------------------------------------------------------
$hasAny = @('codex-plugin','plugin','copilot-plugin') |
          Where-Object { Test-Path (Join-Path $Src $_) }
if (-not $hasAny) {
  Err 'このフォルダに caw のファイルが見つかりません。'
  Err "USB の中の 'caw-bundle' フォルダごとコピーできているか確認してください。"
  exit 1
}

# --- 1. PC の中にコピー -----------------------------------------------------
if (Test-Path $Dest) {
  $stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
  $backup = "$Dest.old-$stamp"
  Warn "既に $Dest があります。"
  Say  "  古いほうを $backup に退避してから、新しいものを入れます。"
  Say  '  （削除はしません。不要になったらご自身で捨ててください）'
  $ans = Read-Host '続けますか？ [y/N]'
  if ($ans -notmatch '^[yY]') { Say '中止しました。'; exit 0 }
  Move-Item -Path $Dest -Destination $backup
  OK "退避しました: $backup"
}

New-Item -ItemType Directory -Path $Dest -Force | Out-Null
Get-ChildItem -Path $Src -Force |
  Where-Object { $_.Name -notin @('install.sh','install.ps1','.DS_Store') } |
  ForEach-Object { Copy-Item -Path $_.FullName -Destination $Dest -Recurse -Force }
OK "PC の中にコピーしました: $Dest"
Say ''

# --- 2. 使える CLI を探す ---------------------------------------------------
$found = $false

function Try-Cli ($cmd, $label, $addArgs, $installArgs) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Say "  - ${label}: 見つかりません（スキップ）"
    return $false
  }
  Say "$label が見つかりました"
  $ans = Read-Host "  caw を $label に導入しますか？ [Y/n]"
  if ($ans -match '^[nN]') { Say '  スキップしました。'; return $true }

  & $cmd @addArgs
  & $cmd @installArgs
  OK "$label に導入しました"
  return $true
}

Say 'お使いの AI CLI を探しています...'
if (Try-Cli 'codex'  'Codex CLI'    @('plugin','marketplace','add',$Dest) @('plugin','add',"caw@$Marketplace"))     { $found = $true }
if (Try-Cli 'claude' 'Claude Code'  @('plugin','marketplace','add',$Dest) @('plugin','install',"caw@$Marketplace")) { $found = $true }
if (Get-Command 'copilot' -ErrorAction SilentlyContinue) {
  Warn 'GitHub Copilot CLI 版はまだ実機確認が済んでいません。'
  Warn 'うまくいかなかったら配布元にご連絡ください。'
  if (Try-Cli 'copilot' 'GitHub Copilot CLI' @('plugin','marketplace','add',$Dest) @('plugin','install','caw'))     { $found = $true }
}
Say ''

if (-not $found) {
  Err 'AI CLI が 1 つも見つかりませんでした。'
  Say ''
  Say '先に次のどれかを導入してください（インターネット接続が必要です）:'
  Say '  Codex CLI    : npm install -g @openai/codex     ← おすすめ'
  Say '  Claude Code  : npm install -g @anthropic-ai/claude-code'
  Say ''
  Say 'npm が無い場合は、先に Node.js（LTS 版）を入れてください。'
  Say 'その後もう一度 install.ps1 を実行してください。'
  exit 1
}

# --- 3. 次の一歩 ------------------------------------------------------------
Say '導入が終わりました。'
Say ''
Say '使い方:'
Say '  1. 研究プロジェクト用のフォルダを作る（例: %USERPROFILE%\my-research）'
Say '  2. そのフォルダで PowerShell を開き、CLI を起動する'
Say '       codex      （または claude）'
Say '  3. こう話しかける:'
Say '       caw'
Say ''
Say 'はじめての質問に答えていくと、office/（AI 部署）と work/（成果物置き場）が'
Say '自動で作られます。詳しくは同じフォルダの「はじめにお読みください.md」を見てください。'
Say ''
