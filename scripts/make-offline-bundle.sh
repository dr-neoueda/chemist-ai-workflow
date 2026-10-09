#!/usr/bin/env bash
# make-offline-bundle.sh — USB 等で手渡しするためのオフライン導入バンドルを作る
#
# 用途: GitHub からのダウンロードが制限されている相手に caw を届ける。
#       ネット接続そのものは前提（CLI がモデル API を呼ぶため必須）。
#
# 使い方:
#   bash scripts/make-offline-bundle.sh ~/Desktop/caw-bundle
#   （出力先は存在しないか空である必要がある。既存を上書きしない）
#
# 設計原則:
#   ★ バンドルの中身は marketplace 配布と byte 一致でなければならない。
#     ここで内容を加工すると「第 3 の配布面」が生まれてドリフトする。
#     本スクリプトは copy と除外だけを行い、中身を書き換えない。最後に一致を検証する。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-}"

if [ -z "$OUT" ]; then
  echo "usage: bash scripts/make-offline-bundle.sh <出力先ディレクトリ>" >&2
  exit 2
fi

red=$'\033[0;31m'; grn=$'\033[0;32m'; dim=$'\033[2m'; off=$'\033[0m'
ok()  { printf '%s OK %s %s\n' "$grn" "$off" "$1"; }
bad() { printf '%s BAD%s %s\n' "$red" "$off" "$1" >&2; FAIL=1; }
FAIL=0

# 既存ディレクトリを破壊しない：無ければ作る、あれば空であることを要求する
if [ -e "$OUT" ]; then
  if [ ! -d "$OUT" ]; then
    echo "出力先がディレクトリではありません: $OUT" >&2; exit 2
  fi
  if [ -n "$(ls -A "$OUT" 2>/dev/null)" ]; then
    echo "出力先が空ではありません: $OUT" >&2
    echo "既存の中身を壊さないため中止します。空のディレクトリを指定するか、先に自分で退避してください。" >&2
    exit 2
  fi
else
  mkdir -p "$OUT"
fi
OUT="$(cd "$OUT" && pwd)"

if [ "$OUT" = "$REPO_ROOT" ]; then
  echo "出力先がリポジトリ自身です。別のディレクトリを指定してください。" >&2; exit 2
fi

echo "リポジトリ : $REPO_ROOT"
echo "出力先     : $OUT"
echo

# --- 1. 各 CLI の marketplace マニフェスト + プラグイン本体 -----------------
# 3 つのマニフェストは読まれる場所が異なるので同じバンドルに同居できる。
# 受け取った人は自分の CLI に合わせて「同じディレクトリ」を登録すればよい。
#
# gemini-plugin は凍結（gemini-plugin/FROZEN.md）のため同梱しない。

copy_pair() {  # <manifest 相対パス> <プラグイン dir> <表示名>
  local manifest="$1" plugdir="$2" label="$3"
  if [ ! -f "$REPO_ROOT/$manifest" ] || [ ! -d "$REPO_ROOT/$plugdir" ]; then
    bad "$label: $manifest または $plugdir が無い"; return
  fi
  mkdir -p "$OUT/$(dirname "$manifest")"
  cp "$REPO_ROOT/$manifest" "$OUT/$manifest"
  # 出力先は空を保証済みなので上書き削除は不要。
  # .DS_Store と __pycache__ は配布物に不要なので写さない（中身は加工しない）。
  ( cd "$REPO_ROOT" && find "$plugdir" -type d -print0 ) \
    | ( cd "$OUT" && xargs -0 -I{} mkdir -p "{}" )
  ( cd "$REPO_ROOT" && find "$plugdir" -type f \
      ! -name '.DS_Store' ! -path '*/__pycache__/*' -print0 ) \
    | while IFS= read -r -d '' f; do cp "$REPO_ROOT/$f" "$OUT/$f"; done
  # 空になった __pycache__ ディレクトリを畳む（rmdir は空のときだけ成功する）
  find "$OUT/$plugdir" -type d -name '__pycache__' -exec rmdir {} + 2>/dev/null || true
  ok "$label: $manifest + $plugdir/"
}

copy_pair ".agents/plugins/marketplace.json"  "codex-plugin"   "Codex CLI（本命）"
copy_pair ".claude-plugin/marketplace.json"   "plugin"         "Claude Code"
copy_pair ".github/plugin/marketplace.json"   "copilot-plugin" "GitHub Copilot CLI"

# --- 2. 前提ツールの導入スクリプト・ライセンス -----------------------------
mkdir -p "$OUT/setup"
cp "$REPO_ROOT/setup/caw-setup.sh"  "$OUT/setup/" 2>/dev/null && ok "setup/caw-setup.sh"
cp "$REPO_ROOT/setup/caw-setup.ps1" "$OUT/setup/" 2>/dev/null && ok "setup/caw-setup.ps1"
cp "$REPO_ROOT/LICENSE" "$OUT/" 2>/dev/null && ok "LICENSE"

# --- 3. 受け取った人が実行するインストーラと手順書 -------------------------
# テンプレートは scripts/bundle-templates/ に実ファイルで持つ（生成しない）。
# スクリプトがスクリプトを書き出す形は読みづらく、壊れても気づきにくいため。
TPL="$REPO_ROOT/scripts/bundle-templates"
if [ ! -d "$TPL" ]; then
  bad "テンプレートが無い: $TPL"
else
  for f in "install.sh" "install.ps1" "はじめにお読みください.md"; do
    if [ -f "$TPL/$f" ]; then
      cp "$TPL/$f" "$OUT/$f"
      ok "$f"
    else
      bad "テンプレート欠落: $f"
    fi
  done
  chmod +x "$OUT/install.sh" 2>/dev/null || true
fi

# --- 4. 検証: バンドルがリポジトリと byte 一致か ---------------------------
echo
echo "--- 検証（バンドル ↔ リポジトリの byte 一致）---"
for d in codex-plugin plugin copilot-plugin; do
  [ -d "$OUT/$d" ] || continue
  if diff -r -x '.DS_Store' -x '__pycache__' "$REPO_ROOT/$d" "$OUT/$d" >/dev/null 2>&1; then
    ok "byte 一致: $d/"
  else
    bad "バンドルがリポジトリと異なる: $d/"
    diff -r -x '.DS_Store' -x '__pycache__' "$REPO_ROOT/$d" "$OUT/$d" | head -5 >&2
  fi
done

# --- 5. 同梱した版を表示（受け渡し記録用） ---------------------------------
echo
echo "--- 同梱した版 ---"
for f in "$OUT/codex-plugin/.codex-plugin/plugin.json" \
         "$OUT/plugin/.claude-plugin/plugin.json" \
         "$OUT/copilot-plugin/plugin.json"; do
  [ -f "$f" ] || continue
  v=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$f" | head -1)
  printf '%s    %-46s %s%s\n' "$dim" "${f#"$OUT"/}" "$v" "$off"
done

echo
echo "サイズ: $(du -sh "$OUT" | cut -f1)"
if [ "$FAIL" -eq 0 ]; then
  printf '%s\nバンドル作成完了: %s%s\n' "$grn" "$OUT" "$off"
  echo "この中身をまるごと USB にコピーして手渡してください。"
else
  printf '%s\n検証に失敗しました。上の BAD を確認してください。%s\n' "$red" "$off"
  exit 1
fi
