#!/bin/bash
# PostToolUse hook (caw plugin v1.3+)
# Edit/Write/MultiEdit が .company/<dept>/<旧パス>/ に書き込もうとした時に
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

# 旧構造（成果物が .company/<dept>/X/ に入るパターン）を検出
case "$rel_path" in
    .company/research/papers/*)
        suggest_path="papers/${rel_path##*.company/research/papers/}"
        ;;
    .company/research/topics/*)
        suggest_path="topics/${rel_path##*.company/research/topics/}"
        ;;
    .company/research/reports/*)
        suggest_path="reports/${rel_path##*.company/research/reports/}"
        ;;
    .company/writing/manuscripts/*)
        suggest_path="manuscripts/${rel_path##*.company/writing/manuscripts/}"
        ;;
    .company/analysis/results/*)
        suggest_path="analyses/${rel_path##*.company/analysis/results/}"
        ;;
    .company/analysis/figures/*)
        suggest_path="figures/${rel_path##*.company/analysis/figures/}"
        ;;
    .company/analysis/notebooks/*)
        suggest_path="notebooks/${rel_path##*.company/analysis/notebooks/}"
        ;;
    .company/presentation/slides/*)
        suggest_path="slides/${rel_path##*.company/presentation/slides/}"
        ;;
    .company/presentation/figures/*)
        suggest_path="figures/${rel_path##*.company/presentation/figures/}"
        ;;
    .company/engineering/scripts/*)
        suggest_path="scripts/${rel_path##*.company/engineering/scripts/}"
        ;;
    .company/engineering/tools/*)
        suggest_path="tools/${rel_path##*.company/engineering/tools/}"
        ;;
    *)
        exit 0
        ;;
esac

cat <<EOF
[caw output-location-check]

⚠️ 成果物配置の二層原則違反を検出

書き込んだパス: $rel_path

caw v1.2 以降では、AI が生成する成果物は project root 直下に置くルールです。
.company/ は AI 部署の運営情報専用エリア（macOS Finder / Linux では標準で非表示、
Windows Explorer では表示されるが運営情報と混ざる）。要約 md・スライド・グラフ・
ノートをここに置くと、ユーザーが成果物を見つけにくくなります。

推奨パス: $suggest_path

修正手順：
  1. ファイルを移動：
     mkdir -p \$(dirname "$project_dir/$suggest_path")
     mv "$path" "$project_dir/$suggest_path"
  2. 必要なら top-level dir に README.md を追加
  3. 移動先のパスでリンクや参照を更新

参照: \${CLAUDE_PLUGIN_ROOT}/skills/caw/SKILL.md の「成果物配置の二層原則」セクション
EOF

exit 0
