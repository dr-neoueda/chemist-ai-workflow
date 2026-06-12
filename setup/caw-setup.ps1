# caw-setup.ps1 — Windows 向け caw 前提ツールの一括セットアップ
#
# 方針: 必要なツールの有無を確認 → 計画を提示 → 一度だけ承認 → 順番にインストール。
#       既に入っているものはスキップ（冪等）。失敗しても続行し、最後にまとめて報告。
# 前提: winget（標準搭載）。poppler は winget に無いため Scoop を使う。
#
# 使い方（PowerShell で）:
#   powershell -ExecutionPolicy Bypass -File caw-setup.ps1
#
# 対応 OS: Windows。macOS は caw-setup.sh を使う。

$ErrorActionPreference = 'Continue'
$log = Join-Path $env:TEMP ("caw-setup-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))

function Say  { param($m) Write-Host $m }
function Head { param($m) Write-Host "`n== $m ==" -ForegroundColor Cyan }
function OK   { param($m) Write-Host "  OK  $m" -ForegroundColor Green }
function Skip { param($m) Write-Host " skip $m" -ForegroundColor DarkGray }
function Fail { param($m) Write-Host " FAIL $m" -ForegroundColor Red }
function Have { param($c) [bool](Get-Command $c -ErrorAction SilentlyContinue) }

function Invoke-Step {
  param([string]$Name, [scriptblock]$Action)
  Write-Host "installing $Name ..." -ForegroundColor Cyan
  try {
    & $Action *>> $log
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { Fail "$Name (詳細は $log)"; return }
    OK $Name
  } catch { Fail "$Name (詳細は $log): $_" }
}

# 必須: 表示名, チェックコマンド, winget ID
$required = @(
  @{ name='Node.js';            check='node';     id='OpenJS.NodeJS.LTS' },
  @{ name='git';                check='git';      id='Git.Git' },
  @{ name='Python 3';           check='python';   id='Python.Python.3.12' }
)
# 任意
$optional = @(
  @{ name='GitHub CLI (gh)';    check='gh';       id='GitHub.cli' },
  @{ name='LibreOffice';        check='soffice';  id='TheDocumentFoundation.LibreOffice' }
)
$pyPkgs = @('python-pptx','matplotlib','pillow','numpy')

Head '現在の状態'
$planReq = @(); $planOpt = @()
foreach ($t in $required) {
  if (Have $t.check) { OK "$($t.name) は導入済み" } else { Say "  ・$($t.name) → インストール予定"; $planReq += $t }
}
$claudePlan = -not (Have 'claude')
if (Have 'claude') { OK 'Claude Code は導入済み' } else { Say '  ・Claude Code → npm でインストール予定' }
$popplerPlan = -not (Have 'pdftoppm')
if (Have 'pdftoppm') { OK 'poppler (pdftoppm) は導入済み' } else { Say '  ・poppler → Scoop でインストール予定' }

$pyMissing = @()
if (Have 'python') {
  foreach ($p in $pyPkgs) {
    $mod = $p -replace '-','_'; if ($p -eq 'pillow') { $mod = 'PIL' }; if ($p -eq 'python-pptx') { $mod = 'pptx' }
    python -c "import $mod" 2>$null
    if ($LASTEXITCODE -eq 0) { OK "Python: $p は導入済み" } else { Say "  ・Python: $p → インストール予定"; $pyMissing += $p }
  }
} else { Say '  ・Python パッケージ → Python 導入後にまとめてインストール予定'; $pyMissing = $pyPkgs }

Say ''
Say '任意（あると便利。後でも入れられます）:'
foreach ($t in $optional) {
  if (Have $t.check) { OK "$($t.name) は導入済み" } else { Say "  ・$($t.name) → 任意でインストール"; $planOpt += $t }
}

# --- 承認（一度だけ） ---
Head '上記の計画でインストールを実行します'
Say "（ログ: $log）"
$ans = Read-Host 'よろしいですか？ [y/N]'
if ($ans -notmatch '^(y|Y|yes|YES)$') { Say '中止しました。'; exit 0 }

if (-not (Have 'winget') -and ($planReq.Count -gt 0 -or $planOpt.Count -gt 0)) {
  Fail 'winget が見つかりません。Microsoft Store の「アプリ インストーラー」を導入してから再実行してください。'
}

# --- 必須ツール（winget） ---
Head '必須ツールのインストール'
foreach ($t in $planReq) {
  if (Have 'winget') {
    Invoke-Step $t.name { winget install -e --id $t.id --accept-package-agreements --accept-source-agreements }
  } else { Skip "$($t.name)（winget 未導入）" }
}

# --- Claude Code（npm） ---
if ($claudePlan) {
  Head 'Claude Code (CLI)'
  if (Have 'npm') { Invoke-Step 'Claude Code' { npm install -g '@anthropic-ai/claude-code' } }
  else { Skip 'Claude Code（npm 未導入。Node.js 導入後に再実行してください）' }
}

# --- 代替 AI CLI（任意・案内のみ） ---
# caw は Claude Code を既定（Tier 1）として導入するが、Codex CLI / GitHub Copilot CLI でも動く。
Head '代替 AI CLI（任意）'
if (Have 'codex')   { OK 'Codex CLI は導入済み' }          else { Say '  ・Codex CLI を使う場合: npm install -g @openai/codex' }
if (Have 'copilot') { OK 'GitHub Copilot CLI は導入済み' } else { Say '  ・GitHub Copilot CLI を使う場合: npm install -g @github/copilot（Node.js 22 以上）' }

# --- poppler（Scoop） ---
if ($popplerPlan) {
  Head 'poppler'
  if (-not (Have 'scoop')) {
    Say 'poppler の導入には Scoop が必要です。導入コマンド:'
    Say "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned; irm get.scoop.sh | iex"
    $s = Read-Host 'Scoop を導入しますか？ [y/N]'
    if ($s -match '^(y|Y|yes|YES)$') {
      try { Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force; Invoke-RestMethod get.scoop.sh | Invoke-Expression } catch { Fail "Scoop 導入: $_" }
    } else { Skip 'poppler（Scoop 未導入。conda install -c conda-forge poppler でも可）' }
  }
  if (Have 'scoop') { Invoke-Step 'poppler' { scoop install poppler } }
}

# --- Python パッケージ ---
if ($pyMissing.Count -gt 0 -and (Have 'python')) {
  Head 'Python パッケージ'
  Invoke-Step ("Python packages: " + ($pyMissing -join ' ')) { python -m pip install @pyMissing }
}

# --- 任意ツール ---
if ($planOpt.Count -gt 0) {
  Head '任意ツール'
  foreach ($t in $planOpt) {
    $o = Read-Host "$($t.name) を入れますか？ [y/N]"
    if ($o -match '^(y|Y|yes|YES)$') {
      if (Have 'winget') { Invoke-Step $t.name { winget install -e --id $t.id --accept-package-agreements --accept-source-agreements } }
      else { Skip "$($t.name)（winget 未導入）" }
    } else { Skip $t.name }
  }
}

# --- 動作確認 ---
Head '動作確認'
foreach ($c in @('node -v','git --version','python --version','pdftoppm -v','claude --version')) {
  $bin = ($c -split ' ')[0]
  if (Have $bin) { Write-Host "  $c :"; Invoke-Expression $c 2>&1 | Select-Object -First 1 } else { Fail "$bin が見つかりません" }
}
if (Have 'python') {
  python -c "import pptx, matplotlib, PIL, numpy; print('  python deps OK')" 2>$null
  if ($LASTEXITCODE -ne 0) { Fail 'Python パッケージの import に失敗' }
}

Head '完了'
Say "詳細ログ: $log"
Say "次は、研究プロジェクトのフォルダで 'claude'（または 'codex' / 'copilot'）を起動し caw を実行してください。"
Say "（caw の Hooks は bash を使うため、Git Bash か WSL2 を併用してください）"
