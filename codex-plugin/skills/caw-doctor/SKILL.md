---
name: caw-doctor
description: >
  `.company/` 構造の健全性チェックと修復提案（研究・就活の両トラックに対応）。ルート設定・秘書部・各部署の存在確認、
  旧構造（成果物が `.company/<dept>/X/` に入っている）の検出、研究なら Playbook 更新滞り・計算ソフト投入フォルダ、
  就活なら就活部署と成果物フォルダ（companies/ documents/ 等）を総点検し、修復コマンドを提示する。
---

# caw-doctor — `.company/` 構造健全性チェック

## いつ使うか

- caw の健全性チェックを依頼されたとき
- ユーザーが「caw の状態を確認」「構造に問題が無いかチェック」「caw 健康診断」と言ったとき
- 研究トラック・就活トラックのどちらでも使える（トラックは自動判定）
- 月 1 回程度の定期点検として
- v1.0 / v1.1 から v1.2 へアップグレード後の初回（旧構造の検出と移行案内に有用）

---

## 検査項目

### 0. トラック判定（最初に実施）

ルート `.company/AGENTS.md`（Claude Code では `CLAUDE.md`）を読み、冒頭の **`> トラック: 就活`** の有無でトラックを判定する。

- **`> トラック: 就活` がある** → 就活トラック。§1・§2・§7・§8（共通）と **§J（就活トラックの検査）**を実施。研究向けの §5（Playbook）・§6/§6b（計算ソフト・研究成果物）はスキップ
- **無い（既定）** → 研究トラック。§1〜§8 をそのまま実施

### 1. ルート構造

- [ ] `.company/` が存在する
- [ ] `.company/AGENTS.md` が存在し、空でない
- [ ] `.company/secretary/` が存在する
- [ ] `.company/secretary/AGENTS.md` が存在する

### 2. 秘書部の運用状況

- [ ] `.company/secretary/inbox/` 存在
- [ ] `.company/secretary/todos/` 存在
- [ ] `.company/secretary/notes/` 存在
- [ ] 今日 or 直近 7 日に `secretary/todos/YYYY-MM-DD.md` が更新されているか
- [ ] 直近 14 日に `secretary/notes/YYYY-MM-DD-decisions.md` が 1 件以上あるか（活動継続の指標）

### 3. 各部署の構造

選択された部署 (research / engineering / computation / analysis / writing / review / presentation) ごとに：

- [ ] `.company/<dept>/AGENTS.md` が存在
- [ ] `.company/<dept>/` 配下のサブディレクトリが運営情報のみ（成果物ディレクトリが含まれていない）

### 4. 旧構造（v1.0 / v1.1 → v1.2 migration 未完了）の検出

以下のパスにファイルが残っていたら **旧構造**として警告：

- `.company/research/papers/`
- `.company/research/topics/`
- `.company/writing/manuscripts/`
- `.company/analysis/results/`
- `.company/analysis/figures/`
- `.company/analysis/notebooks/`
- `.company/presentation/slides/`
- `.company/presentation/figures/`
- `.company/engineering/scripts/`
- `.company/engineering/tools/`

これらに該当するファイルがあれば、project root 直下の対応ディレクトリ（`papers/`, `topics/`, `manuscripts/`, `analyses/`, `figures/`, `notebooks/`, `presentations/slides/`, `scripts/`, `tools/`）への移動を提案。

### 5. Playbook の更新状況

- [ ] `.company/computation/playbooks/<tool>.md` の `last_updated` が 30 日以内
- [ ] 更新が 60 日以上滞っているソフトを警告
- [ ] 各 Playbook に `## Lessons Learned` セクションがあり、最低 1 件のエントリがあるか

### 6. top-level 成果物ディレクトリの確認

部署選択に応じて、対応する top-level ディレクトリが存在するか：

| 部署 | 期待される top-level dir |
|---|---|
| research | `papers/`, `topics/` |
| writing | `manuscripts/` |
| analysis | `analyses/`, `notebooks/`, `figures/` |
| presentation | `presentations/slides/` |
| engineering | `scripts/`, `tools/` |

存在しなければ `README.md` 付きで作成を提案。

### 6b. 初心者向け投入フォルダ（inbox / _past-data）

オンボーディングで作られる「投入フォルダ」が消えていないか確認（消えていると初心者が PDF・過去データの置き場で迷う）：

- [ ] research を選択している場合、`papers/inbox/` が存在する
- [ ] 各計算ソフトディレクトリ（`gaussian/` `gromacs/` `cp2k/` 等）に `inbox/` と `_past-data/` が存在する
- [ ] START HERE 文書 `はじめにお読みください.md` が project root に存在する（はじめてモードで特に重要）

存在しなければ「`caw` で再生成するか、手動で作成」を提案する。

### J. 就活トラックの検査（トラック=就活 のとき）

研究向けの §5・§6・§6b の代わりに、就活モードの構造を点検する。

#### J-1. 就活部署の構造
立ち上げた就活部署ごとに（`company-research` / `self-analysis` / `documents` / `interview` のうち作った分）：
- [ ] `.company/<dept>/` に部署設定ファイル（`CLAUDE.md` または `AGENTS.md`）が存在
- [ ] `.company/<dept>/` 配下が運営情報のみ（ES・企業研究まとめ等の成果物が混ざっていない）

#### J-2. 就活の成果物ディレクトリ（top-level）
| 部署 | 期待される top-level dir |
|---|---|
| company-research | `companies/` |
| documents | `documents/` |
| self-analysis | `self-analysis/` |
| interview | `interview-prep/` |

存在しなければ `README.md` 付きで作成を提案。

#### J-3. 投入フォルダと START HERE
- [ ] `documents/inbox/`（過去 ES の取り込み用）が存在する
- [ ] START HERE 文書 `はじめにお読みください.md` が project root に存在する（はじめてモードで特に重要）

### 7. 同日ファイル重複

`secretary/notes/` や `secretary/todos/` に **同日の duplicate**（例: `2026-05-14.md` と `2026-05-14-2.md`）が無いか。あれば統合を提案。

### 8. 孤立ファイル

`.company/secretary/inbox/` の中で 30 日以上経過した未整理ファイル → 「inbox 整理」を提案。

---

## ワークフロー

### Step 1: ディレクトリ存在確認

```bash
ls -la .company/ 2>/dev/null || echo "ERROR: .company/ not found"
ls -la .company/secretary/ 2>/dev/null
```

`.company/` が存在しない場合は「caw でセットアップしてください」と案内して終了。

### Step 2: 構造スキャン

```bash
# .company/<dept>/ の一覧と各 AGENTS.md の有無
for dept in .company/*/; do
    dept_name=$(basename "$dept")
    [ "$dept_name" = "secretary" ] && continue
    if [ -f "${dept}AGENTS.md" ]; then
        echo "OK   $dept_name: AGENTS.md あり"
    else
        echo "WARN $dept_name: AGENTS.md なし"
    fi
done
```

### Step 3: 旧構造検出

```bash
# 旧パスにファイルが入っているか
for old in \
    ".company/research/papers:papers/" \
    ".company/research/topics:topics/" \
    ".company/writing/manuscripts:manuscripts/" \
    ".company/analysis/results:analyses/" \
    ".company/analysis/figures:figures/" \
    ".company/analysis/notebooks:notebooks/" \
    ".company/presentation/slides:presentations/slides/" \
    ".company/engineering/scripts:scripts/" \
    ".company/engineering/tools:tools/"
do
    old_dir="${old%%:*}"
    new_dir="${old##*:}"
    if [ -d "$old_dir" ] && [ -n "$(ls -A "$old_dir" 2>/dev/null)" ]; then
        echo "MIGRATE 旧構造検出: $old_dir → 推奨: $new_dir"
    fi
done
```

### Step 4: Playbook 更新状況

```bash
# クロスプラットフォーム: YYYY-MM-DD → epoch 秒
# GNU date（Linux / WSL / Git Bash）→ BSD date（macOS）の順で試す
to_epoch() {
    date -d "$1" +%s 2>/dev/null \
        || date -j -f "%Y-%m-%d" "$1" +%s 2>/dev/null \
        || echo 0
}

playbooks_dir=".company/computation/playbooks"
if [ -d "$playbooks_dir" ]; then
    now=$(date +%s)
    for pb in "$playbooks_dir"/*.md; do
        [ -f "$pb" ] || continue
        last_updated=$(grep -E "^last_updated:" "$pb" | head -1 | sed 's/last_updated: *"*\([^"]*\)"*/\1/')
        if [ -n "$last_updated" ]; then
            epoch=$(to_epoch "$last_updated")
            days=$(( ( now - epoch ) / 86400 ))
            if [ "$days" -gt 60 ]; then
                echo "STALE $(basename "$pb"): 最終更新 $last_updated ($days 日前)"
            fi
        fi
    done
fi
```

### Step 5: top-level 成果物ディレクトリの確認

選択された部署を `.company/AGENTS.md` の「部署一覧」テーブルから読み取り、対応する top-level dir の存在をチェック。

### Step 6: レポート生成

以下のフォーマットで **stdout に出力**：

```markdown
# caw-doctor レポート

実行日時: YYYY-MM-DD HH:MM
プロジェクト: <project-name>

## サマリ

- 重大な問題: <N> 件
- 警告: <N> 件
- 情報: <N> 件
- 状態: 🟢 正常 / 🟡 注意 / 🔴 修復必要

## 検査結果

### ✅ 健全な項目
- ...

### ⚠️ 警告
- ...

### 🔄 旧構造（v1.2 migration 推奨）
- ...

### 🔴 重大な問題（要修復）
- ...

## 修復コマンド集

（検出された旧構造のみ表示）

\`\`\`bash
mv .company/research/papers/* papers/ 2>/dev/null
mv .company/research/topics/* topics/ 2>/dev/null
mv .company/writing/manuscripts/* manuscripts/ 2>/dev/null
mv .company/analysis/results/* analyses/ 2>/dev/null
\`\`\`

## 次のアクション

- [ ] 旧構造の移行を実施
- [ ] Playbook の Lessons Learned を更新（X 日滞っている）
- [ ] inbox 整理（Y 件の古いファイル）
```

レポートは **そのまま表示するだけ**。ファイル保存は不要（情報は揮発で十分）。ただしユーザーが「結果を保存して」と言ったら `.company/operations/doctor/YYYY-MM-DD.md` に保存する。

### Step 7: ユーザー対話

レポート提示後、`AskUserQuestion` で「修復を実行するか？」を確認：

- **すぐ修復**：旧構造の `mv` コマンドを実行（dry-run なし、Bash で実施）
- **dry-run**：移動先・ファイル名だけリストアップ
- **見送り**：レポートのみで終了

---

## 重要な注意事項

- `.company/` が存在しない時は、caw での初期セットアップを促す（caw-doctor は既存環境前提）
- 旧構造の移動は **既存ファイルの上書きを避ける**。衝突時はユーザーに判断を仰ぐ
- Playbook の `last_updated` が古くても、内容に変更が無ければそれ自体は問題ない。「更新滞り」は **情報**レベルの警告で、ユーザーが見直すきっかけ提供
- レポートには絵文字を使う（🟢🟡🔴 ✅⚠️🔄⏳）。視覚的に状態が分かるように
- 1 回の実行で全項目をチェックし、まとめて報告する（対話的に項目ずつ聞かない）
