#!/bin/bash
# Stop hook (caw plugin)
# 今日の活動（decisions / 新規 notes / playbook 更新 / 計算ジョブ記録）があるのに
# <today>-learnings.md がまだ無い場合、Claude を引き戻して学びを抽出させる。

set -euo pipefail
cat > /dev/null

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
company_dir="$project_dir/.company"

[ -d "$company_dir" ] || exit 0

today=$(date +%F)
sec_dir="$company_dir/secretary/notes"
learnings_file="$sec_dir/$today-learnings.md"
playbooks_dir="$company_dir/computation/playbooks"
jobs_dir="$company_dir/computation/jobs"

if [ -s "$learnings_file" ]; then
    exit 0
fi

activity=0

if [ -s "$sec_dir/$today-decisions.md" ]; then
    activity=1
fi

if [ "$activity" -eq 0 ] && [ -d "$sec_dir" ]; then
    new_notes=$(find "$sec_dir" -maxdepth 1 -type f -name "*.md" \
        ! -name "*-learnings.md" \
        -newermt "$today 00:00:00" 2>/dev/null | head -1)
    if [ -n "$new_notes" ]; then
        activity=1
    fi
fi

if [ "$activity" -eq 0 ] && [ -d "$playbooks_dir" ]; then
    updated_pb=$(find "$playbooks_dir" -maxdepth 1 -type f -name "*.md" \
        -newermt "$today 00:00:00" 2>/dev/null | head -1)
    if [ -n "$updated_pb" ]; then
        activity=1
    fi
fi

if [ "$activity" -eq 0 ] && [ -d "$jobs_dir" ]; then
    new_jobs=$(find "$jobs_dir" -maxdepth 1 -type f -name "$today-*.md" 2>/dev/null | head -1)
    if [ -n "$new_jobs" ]; then
        activity=1
    fi
fi

[ "$activity" -eq 0 ] && exit 0

cat <<EOF
[caw learnings-reminder]

今日 ($today) のセッションで decisions / notes / playbook / jobs に活動があるのに、
$learnings_file がまだ作成されていません。

セッション終了前に、以下を実行することを推奨：
  1. 今日の会話・編集から「学び 3-5 件」を抽出
     - 既存ノウハウと矛盾した事象、新レシピ、失敗教訓、ベンチマーク値等
  2. $learnings_file に保存（既存なら追記、無ければ新規）
  3. 各学びについて「playbook の Lessons Learned に昇格すべきか」を判定
  4. 該当があれば playbook に転記

学びが本当に何もなければ、空の learnings.md を作って "no learnings today" と書けば本警告は次回から出ません。
EOF
