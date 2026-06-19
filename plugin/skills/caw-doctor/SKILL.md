---
name: caw-doctor
description: >
  `office/` 構造の健全性チェックと修復提案（研究・就活の両トラックに対応）。ルート設定・秘書部・各部署の存在確認、
  旧構造（成果物が `office/<dept>/X/` に入っている）の検出、研究なら Playbook 更新滞り・計算ソフト投入フォルダ、
  就活なら就活部署と成果物フォルダ（work/companies/ work/documents/ 等）を総点検し、修復コマンドを提示する。
trigger: /caw-doctor
---

# caw-doctor — `office/` 構造健全性チェック

## いつ使うか

- `/caw-doctor` を実行したとき
- ユーザーが「caw の状態を確認」「構造に問題が無いかチェック」「caw 健康診断」と言ったとき
- 研究トラック・就活トラックのどちらでも使える（トラックは自動判定）
- 月 1 回程度の定期点検として
- v1.0 / v1.1 から v1.2 へアップグレード後の初回（旧構造の検出と移行案内に有用）

---

## 検査項目

### 0. トラック判定（最初に実施）

ルート `office/CLAUDE.md`（Codex CLI / GitHub Copilot CLI では `AGENTS.md`）を読み、冒頭の **`> トラック:`** 行でトラックを判定する：

- **`> トラック: 就活`** → 就活トラック。§1・§2・§7・§8（共通）と **§J（就活トラックの検査）**を実施。研究向けの §5（Playbook）・§6/§6b（計算ソフト・研究成果物）はスキップ
- **`> トラック: 研究`** → 研究トラック。§1〜§8 をそのまま実施
- **`> トラック:` 行が無い（旧 office）** → `work/companies/` があれば就活、`work/papers/`・`work/topics/` があれば研究と推定（判別不能なら 1 問尋ねる）。**判定したトラックの `> トラック: <値>` 行を office 冒頭に追記してマーカーを補記**（旧 office の移行。設定本文の他部分は変更しない）

### 1. ルート構造

- [ ] `office/` が存在する
- [ ] `office/CLAUDE.md` が存在し、空でない
- [ ] `office/secretary/` が存在する
- [ ] `office/secretary/CLAUDE.md` が存在する

### 2. 秘書部の運用状況

- [ ] `office/secretary/inbox/` 存在
- [ ] `office/secretary/todos/` 存在
- [ ] `office/secretary/notes/` 存在
- [ ] 今日 or 直近 7 日に `secretary/todos/YYYY-MM-DD.md` が更新されているか
- [ ] 直近 14 日に `secretary/notes/YYYY-MM-DD-decisions.md` が 1 件以上あるか（活動継続の指標）

### 3. 各部署の構造

化学者モードの全部署 (research / engineering / computation / analysis / writing / review / presentation) ごとに：

- [ ] `office/<dept>/CLAUDE.md` が存在
- [ ] `office/<dept>/` 配下のサブディレクトリが運営情報のみ（成果物ディレクトリが含まれていない）

### 4. 旧構造（v1.0 / v1.1 → v1.2 migration 未完了）の検出

以下のパスにファイルが残っていたら **旧構造**として警告：

- `office/research/papers/`
- `office/research/topics/`
- `office/writing/manuscripts/`
- `office/analysis/results/`
- `office/analysis/figures/`
- `office/analysis/notebooks/`
- `office/presentation/slides/`
- `office/presentation/figures/`
- `office/engineering/scripts/`
- `office/engineering/tools/`

これらに該当するファイルがあれば、project root 直下の対応ディレクトリ（`work/papers/`, `work/topics/`, `work/manuscripts/`, `work/analyses/`, `work/figures/`, `work/notebooks/`, `work/presentations/slides/`, `work/scripts/`, `work/tools/`, `work/profile/`）への移動を提案。

### 5. Playbook の更新状況

- [ ] `office/computation/playbooks/<tool>.md` の `last_updated` が 30 日以内
- [ ] 更新が 60 日以上滞っているソフトを警告
- [ ] 各 Playbook に `## Lessons Learned` セクションがあり、最低 1 件のエントリがあるか

### 6. `work/` 配下 成果物ディレクトリの確認

部署選択に応じて、対応する `work/` 配下 ディレクトリが存在するか：

| 部署 | 期待される `work/` 配下 dir |
|---|---|
| research | `work/papers/`, `work/topics/` |
| writing | `work/manuscripts/` |
| analysis | `work/analyses/`, `work/notebooks/`, `work/figures/` |
| presentation | `work/presentations/slides/` |
| engineering | `work/scripts/`, `work/tools/` |

存在しなければ `README.md` 付きで作成を提案。

### 6b. 初心者向け投入フォルダ（inbox / _past-data）

オンボーディングで作られる「投入フォルダ」が消えていないか確認（消えていると初心者が PDF・過去データの置き場で迷う）：

- [ ] research を選択している場合、`work/papers/pdf/`（PDF）と `work/papers/md/`（要約）が存在する
- [ ] 統合 `inbox/`（caw-intake の投入口：何でも入れて『処理して』）が存在する
- [ ] 各計算ソフトディレクトリ（`work/gaussian/` `work/gromacs/` `work/cp2k/` 等）に `inbox/` と `_past-data/` が存在する

存在しなければ「`/caw` で再生成するか、手動で作成」を提案する。

### J. 就活トラックの検査（トラック=就活 のとき）

研究向けの §5・§6・§6b の代わりに、就活モードの構造を点検する。

#### J-1. 就活部署の構造
立ち上げた就活部署ごとに（`research` / `analysis` / `writing` / `presentation` のうち作った分。フォルダ名は化学トラックと共通）：
- [ ] `office/<dept>/` に部署設定ファイル（`CLAUDE.md` または `AGENTS.md`）が存在
- [ ] `office/<dept>/` 配下が運営情報のみ（ES・企業研究まとめ等の成果物が混ざっていない）

#### J-2. 就活の成果物ディレクトリ（`work/` 配下）
| 部署（化学と共通フォルダ） | 期待される `work/` 配下 dir |
|---|---|
| `research` | `work/companies/` `work/recruit/` |
| `writing` | `work/documents/` |
| `analysis` | `work/self-analysis/` |
| `presentation` | `work/interview-prep/` |

存在しなければ `README.md` 付きで作成を提案。

#### J-3. 投入フォルダ
- [ ] 統合 `inbox/`（過去資料の投入口：何でも入れて『処理して』）が存在する

### 7. 同日ファイル重複

`secretary/notes/` や `secretary/todos/` に **同日の duplicate**（例: `2026-05-14.md` と `2026-05-14-2.md`）が無いか。あれば統合を提案。

### 8. 孤立ファイル

`office/secretary/inbox/` の中で 30 日以上経過した未整理ファイル → 「inbox 整理」を提案。

---

## ワークフロー

### Step 1: ディレクトリ存在確認

```bash
ls -la office/ 2>/dev/null || echo "ERROR: office/ not found"
ls -la office/secretary/ 2>/dev/null
```

`office/` が存在しない場合は「`/caw` でセットアップしてください」と案内して終了。

### Step 2: 構造スキャン

```bash
# office/<dept>/ の一覧と各 CLAUDE.md の有無
for dept in office/*/; do
    dept_name=$(basename "$dept")
    [ "$dept_name" = "secretary" ] && continue
    if [ -f "${dept}CLAUDE.md" ]; then
        echo "OK   $dept_name: CLAUDE.md あり"
    else
        echo "WARN $dept_name: CLAUDE.md なし"
    fi
done
```

### Step 3: 旧構造検出

```bash
# 旧パスにファイルが入っているか
for old in \
    "office/research/papers:work/papers/" \
    "office/research/topics:work/topics/" \
    "office/writing/manuscripts:work/manuscripts/" \
    "office/analysis/results:work/analyses/" \
    "office/analysis/figures:work/figures/" \
    "office/analysis/notebooks:work/notebooks/" \
    "office/presentation/slides:work/presentations/slides/" \
    "office/engineering/scripts:work/scripts/" \
    "office/engineering/tools:work/tools/"
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

playbooks_dir="office/computation/playbooks"
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

### Step 5: `work/` 配下 成果物ディレクトリの確認

`office/CLAUDE.md` の「部署一覧」テーブルの全部署について、対応する `work/` 配下 dir の存在をチェック。

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
mv office/research/papers/* work/papers/ 2>/dev/null
mv office/research/topics/* work/topics/ 2>/dev/null
mv office/writing/manuscripts/* work/manuscripts/ 2>/dev/null
mv office/analysis/results/* work/analyses/ 2>/dev/null
\`\`\`

## 次のアクション

- [ ] 旧構造の移行を実施
- [ ] Playbook の Lessons Learned を更新（X 日滞っている）
- [ ] inbox 整理（Y 件の古いファイル）
```

レポートは **そのまま表示するだけ**。ファイル保存は不要（情報は揮発で十分）。ただしユーザーが「結果を保存して」と言ったら `office/operations/doctor/YYYY-MM-DD.md` に保存する。

### Step 7: ユーザー対話

レポート提示後、`AskUserQuestion` で「修復を実行するか？」を確認：

- **すぐ修復**：旧構造の `mv` コマンドを実行（dry-run なし、Bash で実施）
- **dry-run**：移動先・ファイル名だけリストアップ
- **見送り**：レポートのみで終了

---

## 重要な注意事項

- `office/` が存在しない時は、`/caw` での初期セットアップを促す（caw-doctor は既存環境前提）
- 旧構造の移動は **既存ファイルの上書きを避ける**。衝突時はユーザーに判断を仰ぐ
- Playbook の `last_updated` が古くても、内容に変更が無ければそれ自体は問題ない。「更新滞り」は **情報**レベルの警告で、ユーザーが見直すきっかけ提供
- レポートには絵文字を使う（🟢🟡🔴 ✅⚠️🔄⏳）。視覚的に状態が分かるように
- 1 回の実行で全項目をチェックし、まとめて報告する（対話的に項目ずつ聞かない）
