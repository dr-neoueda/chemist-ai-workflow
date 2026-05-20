---
name: caw-playbook
description: >
  計算ソフトの log ファイルを解析し、収束状況・エラー・パラメータ起因の挙動を抽出して
  Playbook の Lessons Learned に自動追記するスキル。会話を重ねるほどスペシャリスト化する。
---

# caw-playbook — 計算 log 解析と Playbook 追記

## いつ使うか

- log 解析・Playbook 追記を依頼されたとき
- ユーザーが「log を解析して」「Playbook に追記して」「この計算から何を学べる？」と言ったとき
- 計算ジョブ完了後の振り返り段階
- 計算が想定外の挙動を示した（収束しない / 異常終了 / 物理的にあり得ない値）とき

`.company/computation/playbooks/` が存在しない場合、caw で computation 部署を追加することを促す。

---

## ワークフロー

### Step 1: 対象 log の特定

ユーザー指定がない場合、`AskUserQuestion` で対象 log を確認：

- ファイルパス指定（例: `gaussian/benzene_ts_20260513/benzene_ts.log`）
- 最新ジョブから自動検出（mtime 上位）
- 失敗ジョブを優先（"Error termination" 等を含むもの）

検出した log の **ソフトウェア**（Gaussian / ORCA / CP2K / GROMACS / VASP / QE）を判定し、対応する Playbook を読み込む：
- `.company/computation/playbooks/<tool>.md`

### Step 2: log の解析

ソフトごとに重要なパターンを抽出：

#### Gaussian

- 終了状態: `Normal termination` / `Error termination`
- 収束: `Stationary point found` / `Convergence failure`
- SCF: `SCF Done` / `Convergence failure on cycle`
- 振動: `imaginary frequencies` の数（TS は 1、極小点は 0）
- 異常パターン: `Lambda0=` の値（TS opt 中の Hessian 陳腐化兆候）
- 計算時間: `Job cpu time` / `Elapsed time`

#### ORCA

- 終了: `ORCA TERMINATED NORMALLY` / `ABORTING THE RUN`
- 収束: `THE OPTIMIZATION HAS CONVERGED` / `Convergence ... FAILED`
- SCF: `SCF CONVERGED AFTER` / `SCF DID NOT CONVERGE`
- 虚振動: `Number of imaginary modes:`
- TightSCF / NormalSCF の差異

#### CP2K

- 終了: `PROGRAM ENDED` / `*ERROR*`
- SCF: `SCF run converged in` / `SCF run NOT converged`
- MD: `MD| ENERGY DRIFT` の値（< 1e-5 が目安）
- セル: `CELL_TOP|` 周辺で cell parameters

#### GROMACS

- 終了: `Finished mdrun` / `Fatal error`
- 平衡化: 温度・圧力・密度の時間プロット領域
- LINCS warnings / constraints violation
- 性能: `ns/day` 指標

#### VASP

- 終了: `General timing and accounting informations`
- 収束: `EDIFF is reached` / `convergence not reached`
- 構造: `reached required accuracy - stopping structural energy minimisation`
- 警告: `WARNING:` 行の集約

#### Quantum ESPRESSO

- 終了: `JOB DONE.` / `Error in routine`
- SCF: `convergence has been achieved` / `convergence NOT achieved`
- 構造: `bfgs converged`

### Step 3: 知見の抽出と分類

解析結果から以下のカテゴリで知見を整理：

| カテゴリ | 内容例 |
|---|---|
| **成功レシピ** | 「B3LYP/def2-SVP D3BJ で benzene Opt+Freq、22 step で収束、虚振動 0」 |
| **失敗教訓** | 「opt=(ts,calcfc) で 76 step 後 Lambda0=1.8e-6 → Hessian 陳腐化、recalcfc=20 推奨」 |
| **新しい罠** | 「PBC supercell の connectivity-based 分子抽出で Kabsch RMSD 爆発 → unwrap 必須」 |
| **ベンチマーク値** | 「v8-MP NPT 450K で V drift -0.64% / 4 ps（Phase A Go 条件 ±2% を 3× margin でクリア）」 |
| **Codex 二段検証で防げた誤り** | 「python-reviewer は構文/DRY、Codex は物理意味論（Stationary point filter 不在）」 |

### Step 4: 追記候補の提示

ユーザーに以下を提示し、確認を求める：

```
log 解析完了：

ファイル: gaussian/<molecule>_ts_20260508/<molecule>_ts.log
ソフト: Gaussian
終了状態: walltime exceeded（76 step 経過、未収束）

抽出した知見（追記候補）：

### YYYY-MM-DD - TS opt 終盤の Hessian 陳腐化は Lambda0 → 0 で検出可能

- **状況**: 78 atom + BS-UHF + scf=qc 系の opt=(ts,calcfc) で 76 step 経過、Lambda0=1.797e-6 まで小さくなり saddle 以外の soft mode が出現しかけ
- **原因**: calcfc は初回 1 度のみで以降は updatefc（BFGS-like）。76 step 経過で Hessian update が陳腐化
- **教訓**: `opt=(ts,calcfc,recalcfc=20,maxstep=6)` をデフォルトに（20 step ごとに Hessian 再評価で陳腐化リセット）
- **参照**: jobs/2026-05-08-<molecule>-ts.md

これを `.company/computation/playbooks/gaussian.md` の Lessons Learned に追記してよろしいですか？
```

### Step 5: Playbook への追記

ユーザーが OK と言ったら、対応する Playbook を **Read → Edit append** で更新：

1. `.company/computation/playbooks/<tool>.md` を Read
2. `## Lessons Learned` セクション末尾を特定
3. 新エントリを末尾に Edit append（既存エントリは絶対に上書きしない）
4. frontmatter の `last_updated` を今日の日付に Edit 更新

エントリフォーマット：

```markdown
### YYYY-MM-DD - <一行サマリ>

- **状況**: ...
- **原因**: ...
- **教訓**: ...
- **参照**: jobs/YYYY-MM-DD-<system>-<purpose>.md
```

### Step 6: memory 昇格判定（オプション）

知見が **特定の計算ソフトを超えた一般則** だった場合、memory feedback への昇格を提案：

```
この教訓は Gaussian だけでなく一般則として「PBC supercell の connectivity-based 分子抽出は必ず unwrap を伴う」に拡張できそうです。
~/.claude/projects/<project>/memory/ に新規 feedback memory を作成しますか？
```

ユーザーが OK なら、memory ファイルを生成。

### Step 7: 完了報告

```
追記完了：

- Playbook: .company/computation/playbooks/gaussian.md
- 追加エントリ: ### 2026-05-13 - TS opt 終盤の Hessian 陳腐化は Lambda0 → 0 で検出可能
- last_updated: 2026-05-13 に更新
- memory feedback 昇格: ✅ feedback_gaussian_ts_hessian_staleness.md 新規作成

次セッション以降、関連キーワード（"TS opt", "Lambda0", "recalcfc"）の対話時に、本知見が自動参照されます。
```

---

## 重要な注意事項

- **既存 Lessons Learned エントリは絶対に上書きしない**。末尾追記のみ
- **frontmatter の `last_updated` を必ず更新**（playbook の鮮度管理）
- **化学物理の用語は正確に**：汎関数名・基底関数・force field・cell parameter の表記揺れを起こさない
- **数値には単位を明記**：エネルギー (Hartree / eV / kcal/mol)、長さ (Å / bohr)、時間 (fs / ps / ns)、温度 (K)
- **再現性が確認できない知見は採用しない**：1 回限りの異常は「観測例」として記録、複数事例で確証された場合のみ「教訓」に昇格
- **Codex 二段レビューで防げた誤り**は積極的に記録（python-reviewer は構文、Codex は物理意味論の役割分担を残す）
- **ベンチマーク値はそのまま転記**：drift 率・wall time・parity slope 等は加工せず生数値で
