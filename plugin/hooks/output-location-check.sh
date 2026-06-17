#!/bin/bash
# PostToolUse hook (caw plugin v1.3+)
# Edit/Write/MultiEdit が office/<dept>/<旧パス>/ に書き込もうとした時に
# 「成果物配置の二層原則」違反として警告を出す。
# Block はしない（exit 0）。警告のみ stdout に出力し Claude が次ターンで読む。

set -euo pipefail

input=$(cat)

# jq 不在環境のフォールバック判定
if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

tool_name=$(echo "$input" | jq -r '.tool_name // ""')
case "$tool_name" in
    Edit|Write|MultiEdit) ;;
    *) exit 0 ;;
esac

path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
[ -n "$path" ] || exit 0

# 絶対パスを project_dir 相対に変換
project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
rel_path="${path#"$project_dir/"}"

# 旧構造（成果物が office/<dept>/X/ に入るパターン）を検出
case "$rel_path" in
    office/research/papers/*)
        suggest_path="work/papers/${rel_path##*office/research/papers/}"
        ;;
    office/research/topics/*)
        suggest_path="work/topics/${rel_path##*office/research/topics/}"
        ;;
    office/research/reports/*)
        suggest_path="work/reports/${rel_path##*office/research/reports/}"
        ;;
    office/writing/manuscripts/*)
        suggest_path="work/manuscripts/${rel_path##*office/writing/manuscripts/}"
        ;;
    office/analysis/results/*)
        suggest_path="work/analyses/${rel_path##*office/analysis/results/}"
        ;;
    office/analysis/figures/*)
        suggest_path="work/figures/${rel_path##*office/analysis/figures/}"
        ;;
    office/analysis/notebooks/*)
        suggest_path="work/notebooks/${rel_path##*office/analysis/notebooks/}"
        ;;
    office/presentation/slides/*)
        suggest_path="work/presentations/slides/${rel_path##*office/presentation/slides/}"
        ;;
    office/presentation/figures/*)
        suggest_path="work/figures/${rel_path##*office/presentation/figures/}"
        ;;
    office/engineering/scripts/*)
        suggest_path="work/scripts/${rel_path##*office/engineering/scripts/}"
        ;;
    office/engineering/tools/*)
        suggest_path="work/tools/${rel_path##*office/engineering/tools/}"
        ;;
    *)
        exit 0
        ;;
esac

cat <<EOF
[caw output-location-check]

⚠️ 成果物配置の二層原則違反を検出

書き込んだパス: $rel_path

caw v1.2 以降では、AI が生成する成果物は `work/` 配下に置くルールです。
office/ は AI 部署の運営情報専用エリア（可視フォルダだが運営情報専用）。要約 md・スライド・グラフ・
ノートをここに置くと、ユーザーが成果物を見つけにくくなります。

推奨パス: $suggest_path

修正手順：
  1. ファイルを移動：
     mkdir -p \$(dirname "$project_dir/$suggest_path")
     mv "$path" "$project_dir/$suggest_path"
  2. 必要なら work/ 配下の dir に README.md を追加
  3. 移動先のパスでリンクや参照を更新

参照: \${CLAUDE_PLUGIN_ROOT}/skills/caw/SKILL.md の「成果物配置の二層原則」セクション
EOF

exit 0
