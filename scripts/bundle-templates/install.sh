#!/usr/bin/env bash
# caw オフライン導入インストーラ（macOS / Linux）
#
# USB メモリの中でダブルクリック、またはターミナルで
#   bash install.sh
# を実行してください。
#
# このスクリプトがやること:
#   1. USB の中身を、あなたの PC の中（既定 ~/caw-plugin）にコピーする
#   2. お使いの AI CLI に「そのコピー先」を登録する
#   3. caw プラグインをインストールする
#
# ★ なぜコピーするのか
#   USB のパスを直接登録すると、USB を抜いた時点で caw が動かなくなります。
#   （ローカルパスの marketplace は、その場所を参照し続ける仕様のため）
#   なので必ず PC の中にコピーしてから登録します。

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CAW_DEST:-$HOME/caw-plugin}"
MARKETPLACE="chemist-ai-workflow"

bold=$'\033[1m'; grn=$'\033[0;32m'; ylw=$'\033[0;33m'; red=$'\033[0;31m'; dim=$'\033[2m'; off=$'\033[0m'
say()  { printf '%s\n' "$*"; }
ok()   { printf '%s✓%s %s\n' "$grn" "$off" "$*"; }
warn() { printf '%s!%s %s\n' "$ylw" "$off" "$*"; }
err()  { printf '%s✗%s %s\n' "$red" "$off" "$*" >&2; }

say ""
say "${bold}caw（化学者のための AI エージェント導入伴走）オフライン導入${off}"
say "${dim}コピー元: $SRC${off}"
say "${dim}コピー先: $DEST${off}"
say ""

# --- 0. 中身の確認 ----------------------------------------------------------
if [ ! -d "$SRC/codex-plugin" ] && [ ! -d "$SRC/plugin" ] && [ ! -d "$SRC/copilot-plugin" ]; then
  err "このフォルダに caw のファイルが見つかりません。"
  err "USB の中の 'caw-bundle' フォルダごとコピーできているか確認してください。"
  exit 1
fi

# --- 1. PC の中にコピー -----------------------------------------------------
if [ -e "$DEST" ]; then
  STAMP="$(date +%Y%m%d-%H%M%S)"
  BACKUP="${DEST}.old-${STAMP}"
  warn "既に $DEST があります。"
  say "  古いほうを $BACKUP に退避してから、新しいものを入れます。"
  say "  （削除はしません。不要になったらご自身で捨ててください）"
  printf "続けますか？ [y/N]: "
  read -r ans
  case "$ans" in
    [yY]*) ;;
    *) say "中止しました。"; exit 0 ;;
  esac
  mv "$DEST" "$BACKUP"
  ok "退避しました: $BACKUP"
fi

mkdir -p "$DEST"
# install.sh 自身と Windows 用スクリプトはコピー先に不要
( cd "$SRC" && tar -cf - \
    --exclude='install.sh' --exclude='install.ps1' --exclude='.DS_Store' . ) \
  | ( cd "$DEST" && tar -xf - )
ok "PC の中にコピーしました: $DEST"
say ""

# --- 2. 使える CLI を探す ---------------------------------------------------
FOUND=0
try_cli() {  # <コマンド名> <表示名> <marketplace add> <install>
  local cmd="$1" label="$2"
  command -v "$cmd" >/dev/null 2>&1 || { say "${dim}  - $label: 見つかりません（スキップ）${off}"; return; }
  FOUND=1
  say "${bold}$label が見つかりました${off}"
  printf "  caw を %s に導入しますか？ [Y/n]: " "$label"
  read -r ans
  case "$ans" in
    [nN]*) say "  スキップしました。"; return ;;
  esac

  case "$cmd" in
    codex)
      codex plugin marketplace add "$DEST" && \
      codex plugin add "caw@${MARKETPLACE}" && ok "$label に導入しました"
      ;;
    claude)
      claude plugin marketplace add "$DEST" && \
      claude plugin install "caw@${MARKETPLACE}" && ok "$label に導入しました"
      ;;
    copilot)
      warn "GitHub Copilot CLI 版はまだ実機確認が済んでいません。"
      warn "うまくいかなかったら配布元にご連絡ください。"
      copilot plugin marketplace add "$DEST" && \
      copilot plugin install caw && ok "$label に導入しました"
      ;;
  esac
}

say "お使いの AI CLI を探しています..."
try_cli codex   "Codex CLI"
try_cli claude  "Claude Code"
try_cli copilot "GitHub Copilot CLI"
say ""

if [ "$FOUND" -eq 0 ]; then
  err "AI CLI が 1 つも見つかりませんでした。"
  say ""
  say "先に次のどれかを導入してください（インターネット接続が必要です）:"
  say "  Codex CLI    : npm install -g @openai/codex     ← おすすめ"
  say "  Claude Code  : npm install -g @anthropic-ai/claude-code"
  say ""
  say "npm が無い場合は、先に Node.js（LTS 版）を入れてください。"
  say "その後もう一度 bash install.sh を実行してください。"
  exit 1
fi

# --- 3. 次の一歩 ------------------------------------------------------------
say "${bold}導入が終わりました。${off}"
say ""
say "使い方:"
say "  1. 研究プロジェクト用のフォルダを作る（例: ~/my-research）"
say "  2. そのフォルダでターミナルを開き、CLI を起動する"
say "       codex      （または claude）"
say "  3. こう話しかける:"
say "       caw"
say ""
say "はじめての質問に答えていくと、office/（AI 部署）と work/（成果物置き場）が"
say "自動で作られます。詳しくは同じフォルダの「はじめにお読みください.md」を見てください。"
say ""
