#!/bin/bash
# SessionStart hook (caw plugin)
# カレントプロジェクトの office/ を検出し、直近の secretary/notes と
# computation/playbooks/ をコンテキストに注入する。
# ユーザー個人パスをハードコードしない（プラグイン配布版）。

set -euo pipefail
cat > /dev/null  # Claude Code から渡される JSON を読み捨て

# Claude Code が CLAUDE_PROJECT_DIR を提供する。未定義なら cwd フォールバック。
project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
company_dir="$project_dir/office"

[ -d "$company_dir" ] || exit 0

sec_dir="$company_dir/secretary/notes"
playbooks_dir="$company_dir/computation/playbooks"

cat <<EOF
## caw SessionStart コンテキスト

プロジェクト: $project_dir
office/ 検出済。秘書を窓口に運営モードで起動。

EOF

if [ -d "$sec_dir" ]; then
    # mtime 降順で直近 3 件。ls -t は macOS / Linux / WSL / Git Bash 共通（POSIX）。
    # BSD 専用の `stat -f` / GNU 専用の `stat -c` を避ける。
    files=$(ls -t "$sec_dir"/*-decisions.md "$sec_dir"/*-learnings.md 2>/dev/null | head -3)
    if [ -n "$files" ]; then
        echo "### 直近の意思決定・学び（mtime 上位 3 件・各 30 行）"
        echo ""
        while IFS= read -r f; do
            [ -z "$f" ] && continue
            echo "#### $(basename "$f")"
            echo ""
            head -30 "$f"
            echo ""
            echo "---"
            echo ""
        done <<< "$files"
    fi
fi

if [ -d "$playbooks_dir" ]; then
    pb_files=$(find "$playbooks_dir" -maxdepth 1 -type f -name "*.md" 2>/dev/null | sort)
    if [ -n "$pb_files" ]; then
        echo "### 利用可能な Playbook（必要に応じて Read tool で全文ロード）"
        echo ""
        while IFS= read -r f; do
            [ -z "$f" ] && continue
            echo "- $f"
        done <<< "$pb_files"
        echo ""
    fi
fi

today=$(date +%F)
todo_file="$company_dir/secretary/todos/$today.md"
if [ -s "$todo_file" ]; then
    echo "### 今日の TODO（$today）"
    echo ""
    head -30 "$todo_file"
    echo ""
fi
