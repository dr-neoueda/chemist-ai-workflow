#!/usr/bin/env bash
# caw-setup.sh — macOS 向け caw 前提ツールの一括セットアップ
#
# 方針: OS を検出し、必要なツールの有無を確認 → 計画を提示 → 一度だけ承認 →
#       順番にインストール。既に入っているものはスキップ（冪等）。
# 安全: sudo は使わない（Homebrew は user 権限）。各ステップの成否を記録し、
#       失敗しても続行して最後にまとめて報告する。
#
# 使い方:
#   bash caw-setup.sh
#
# 対応 OS: macOS。Windows は caw-setup.ps1 を使う。

set -u
LOG="${TMPDIR:-/tmp}/caw-setup-$(date +%Y%m%d-%H%M%S).log"

c_blue=$'\033[0;34m'; c_green=$'\033[0;32m'; c_red=$'\033[0;31m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
say()  { printf '%s\n' "$*"; }
head() { printf '\n%s== %s ==%s\n' "$c_blue" "$*" "$c_off"; }
ok()   { printf '%s  OK %s %s\n' "$c_green" "$c_off" "$*"; }
skip() { printf '%s skip%s %s\n' "$c_dim" "$c_off" "$*"; }
fail() { printf '%s FAIL%s %s\n' "$c_red" "$c_off" "$*"; }

if [ "$(uname -s)" != "Darwin" ]; then
  say "このスクリプトは macOS 用です。Windows では caw-setup.ps1 を使ってください。"
  exit 1
fi

have() { command -v "$1" >/dev/null 2>&1; }

# --- 計画づくり -------------------------------------------------------------
# 各ツール: "表示名|チェックコマンド|インストールコマンド"
REQUIRED=(
  "Node.js|node|brew install node"
  "git|git|brew install git"
  "Python 3|python3|brew install python"
  "poppler (pdftoppm)|pdftoppm|brew install poppler"
)
OPTIONAL=(
  "GitHub CLI (gh)|gh|brew install gh"
  "LibreOffice|soffice|brew install --cask libreoffice"
)
PY_PKGS=(python-pptx matplotlib pillow numpy)

head "現在の状態"
plan_req=(); plan_opt=()
for entry in "${REQUIRED[@]}"; do
  IFS='|' read -r name chk inst <<<"$entry"
  if have "$chk"; then ok "$name は導入済み"; else say "  ・$name → インストール予定"; plan_req+=("$entry"); fi
done
# Claude Code（CLI 本体。node があれば npm 経由で導入可能）
claude_plan=0
if have claude; then ok "Claude Code は導入済み"; else say "  ・Claude Code → npm でインストール予定"; claude_plan=1; fi
# Python パッケージ
py_missing=()
if have python3; then
  for p in "${PY_PKGS[@]}"; do
    mod="${p//-/_}"; [ "$p" = "pillow" ] && mod="PIL"; [ "$p" = "python-pptx" ] && mod="pptx"
    if python3 -c "import $mod" >/dev/null 2>&1; then ok "Python: $p は導入済み"; else say "  ・Python: $p → インストール予定"; py_missing+=("$p"); fi
  done
else
  say "  ・Python パッケージ → Python 導入後にまとめてインストール予定"; py_missing=("${PY_PKGS[@]}")
fi
say ""
say "任意（あると便利。後でも入れられます）:"
for entry in "${OPTIONAL[@]}"; do
  IFS='|' read -r name chk inst <<<"$entry"
  if have "$chk"; then ok "$name は導入済み"; else say "  ・$name → 任意でインストール"; plan_opt+=("$entry"); fi
done

if [ ${#plan_req[@]} -eq 0 ] && [ ${#py_missing[@]} -eq 0 ] && [ $claude_plan -eq 0 ]; then
  head "必須ツールはすべて揃っています"
  say "任意ツールを入れたい場合のみ続行してください。"
fi

# --- 承認（一度だけ） -------------------------------------------------------
head "上記の計画でインストールを実行します"
say "（ログ: $LOG）"
printf 'よろしいですか？ [y/N]: '
read -r ans
case "$ans" in y|Y|yes|YES) ;; *) say "中止しました。"; exit 0;; esac

run() { # 表示名, コマンド...
  local name="$1"; shift
  printf '%s installing%s %s ...\n' "$c_blue" "$c_off" "$name"
  if "$@" >>"$LOG" 2>&1; then ok "$name"; return 0; else fail "$name（詳細は $LOG）"; return 1; fi
}

# --- Homebrew（多くのインストールの前提） -----------------------------------
need_brew=0
{ [ ${#plan_req[@]} -gt 0 ] || [ ${#plan_opt[@]} -gt 0 ]; } && need_brew=1
if [ $need_brew -eq 1 ] && ! have brew; then
  head "Homebrew の導入"
  say "Homebrew が必要です。次の公式コマンドで導入します:"
  say '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  printf 'Homebrew を導入しますか？ [y/N]: '
  read -r b
  case "$b" in y|Y|yes|YES) /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || fail "Homebrew 導入" ;;
    *) say "Homebrew をスキップ。brew が要るツールは飛ばします。";; esac
fi

# --- 必須ツール -------------------------------------------------------------
head "必須ツールのインストール"
for entry in "${plan_req[@]}"; do
  IFS='|' read -r name chk inst <<<"$entry"
  if have brew; then run "$name" bash -c "$inst"; else skip "$name（brew 未導入のため）"; fi
done

# --- Claude Code ------------------------------------------------------------
if [ $claude_plan -eq 1 ]; then
  head "Claude Code (CLI)"
  if have npm; then run "Claude Code" npm install -g @anthropic-ai/claude-code
  else skip "Claude Code（npm 未導入。Node.js 導入後に再実行してください）"; fi
fi

# --- 代替 AI CLI（任意・案内のみ） -----------------------------------------
# caw は Claude Code を既定（Tier 1）として導入するが、Codex CLI / GitHub Copilot CLI でも動く。
# 好みに応じて npm（Node.js 導入後）で個別に追加できる。
head "代替 AI CLI（任意）"
if have codex;   then ok "Codex CLI は導入済み";          else say "  ・Codex CLI を使う場合: npm install -g @openai/codex"; fi
if have copilot; then ok "GitHub Copilot CLI は導入済み"; else say "  ・GitHub Copilot CLI を使う場合: npm install -g @github/copilot（Node.js 22 以上）"; fi

# --- Python パッケージ ------------------------------------------------------
if [ ${#py_missing[@]} -gt 0 ] && have python3; then
  head "Python パッケージ"
  if python3 -m pip install "${py_missing[@]}" >>"$LOG" 2>&1; then ok "Python packages: ${py_missing[*]}"
  elif python3 -m pip install --user --break-system-packages "${py_missing[@]}" >>"$LOG" 2>&1; then ok "Python packages（--user）: ${py_missing[*]}"
  else fail "Python packages（詳細は $LOG）。venv の利用も検討してください"; fi
fi

# --- 任意ツール -------------------------------------------------------------
if [ ${#plan_opt[@]} -gt 0 ]; then
  head "任意ツール"
  for entry in "${plan_opt[@]}"; do
    IFS='|' read -r name chk inst <<<"$entry"
    printf '%s を入れますか？ [y/N]: ' "$name"; read -r o
    case "$o" in y|Y|yes|YES) have brew && run "$name" bash -c "$inst" || skip "$name（brew 未導入）";; *) skip "$name";; esac
  done
fi

# --- 動作確認 ---------------------------------------------------------------
head "動作確認"
for c in "node -v" "git --version" "python3 --version" "pdftoppm -v" "claude --version"; do
  bin="${c%% *}"
  if have "$bin"; then printf '  %s: ' "$bin"; eval "$c" 2>&1 | head -1; else fail "$bin が見つかりません"; fi
done
if have python3; then
  python3 -c "import pptx, matplotlib, PIL, numpy; print('  python deps OK')" 2>/dev/null || fail "Python パッケージの import に失敗"
fi

head "完了"
say "詳細ログ: $LOG"
say "次は、研究プロジェクトのフォルダで 'claude'（または 'codex' / 'copilot'）を起動し caw を実行してください。"
