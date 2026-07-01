---
name: caw-playbook
description: >
  計算ソフトの log 解析（収束・エラー・パラメータ起因の挙動）に加え、**解析の再利用レシピ**も
  蓄積するスキル。計算は `computation/playbooks/<tool>.md` の Lessons Learned に、解析手順は
  `work/analyses/_playbook/<topic>.md` に追記し、会話を重ねるほどユーザーに特化する。
trigger: /caw-playbook
---

# caw-playbook — 計算 log 解析と Playbook 追記

## いつ使うか

- `/caw-playbook` を実行したとき
- ユーザーが「log を解析して」「Playbook に追記して」「この計算から何を学べる？」と言ったとき
- 計算ジョブ完了後の振り返り段階
- 計算が想定外の挙動を示した（収束しない / 異常終了 / 物理的にあり得ない値）とき
- **`caw-analyze` で行った解析が再利用に値するとき**（手順・使った汎用ツール・罠・検証観点を残す）

`office/computation/playbooks/`（計算）や `work/analyses/_playbook/`（解析）が無ければ、`/caw` で対応部署を追加するよう促す。

## 2 種類の Playbook（同じ「使うほど特化」の仕組み）

| 対象 | 置き場 | 追記する内容 |
|---|---|---|
| **計算ソフト**（Gaussian/CP2K/MACE 等） | `office/computation/playbooks/<tool>.md` の `## Lessons Learned` | 収束の罠・推奨パラメータ・失敗の教訓・ベンチ値 |
| **解析**（`caw-analyze` 由来・手法問わず） | `work/analyses/_playbook/<topic>.md` | 手順・使った汎用ツール（pandas/scipy/RDKit 等）・**取込アダプタ（ベンダーバイナリ→中立形式の変換手順）**・**外部専用ソフトの orchestrate 手順**・前処理・検証観点・単位・罠 |

どちらも **`### YYYY-MM-DD - 一行サマリ` で時系列に末尾追記**（既存の上書き禁止）。解析レシピは**ユーザーのローカルに空から育つ**（caw が手法別パイプラインを出荷する代わりに、ユーザーごとのレシピが蓄積する＝`docs/analysis-companion-design.md` §B。スターター素材は同梱しない）。

---

## はじめてモードを尊重する

このスキルを実行する前に `office/CLAUDE.md`（Codex CLI / GitHub Copilot CLI では `AGENTS.md`）を読み、冒頭に `> 運用モード: はじめて` があれば、`caw` skill の「はじめてモードの挙動」を全応答に適用する：**平易な日本語**で話し、専門用語（化学・計算手法・書誌の用語）は初出で 1 行説明を添え、各ステップの最後に**「次はこれをしましょう」を 1 つ**だけ提示する。元に戻せない操作（削除・上書き・外部登録・送信）は必ず事前確認する。

## ワークフロー

### Step 1: 対象 log の特定

ユーザー指定がない場合、`AskUserQuestion` で対象 log を確認：

- ファイルパス指定（例: `work/gaussian/benzene_ts_20260513/benzene_ts.log`）
- 最新ジョブから自動検出（mtime 上位）
- 失敗ジョブを優先（"Error termination" 等を含むもの）

検出した log の **ソフトウェア**（Gaussian / ORCA / CP2K / GROMACS / VASP / QE / ChimeraX）を判定し、対応する Playbook を読み込む：
- `office/computation/playbooks/<tool>.md`

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

#### ChimeraX

- 終了・エラー: log の `Error` / Python traceback
- フィット品質: `fitmap` の correlation / overlap・average map value、`measure correlation`
- マップ設定: 閾値（level）・解像度、`molmap` の resolution
- cryo-EM 構築: ISOLDE の clashes / rotamer / Ramachandran outliers
- ヘッドレス: `--nogui` / `--offscreen`（OSMesa）の描画・ライブラリ関連メッセージ

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

ファイル: work/gaussian/<molecule>_ts_20260508/<molecule>_ts.log
ソフト: Gaussian
終了状態: walltime exceeded（76 step 経過、未収束）

抽出した知見（追記候補）：

### YYYY-MM-DD - TS opt 終盤の Hessian 陳腐化は Lambda0 → 0 で検出可能

- **状況**: 78 atom + BS-UHF + scf=qc 系の opt=(ts,calcfc) で 76 step 経過、Lambda0=1.797e-6 まで小さくなり saddle 以外の soft mode が出現しかけ
- **原因**: calcfc は初回 1 度のみで以降は updatefc（BFGS-like）。76 step 経過で Hessian update が陳腐化
- **教訓**: `opt=(ts,calcfc,recalcfc=20,maxstep=6)` をデフォルトに（20 step ごとに Hessian 再評価で陳腐化リセット）
- **参照**: jobs/2026-05-08-<molecule>-ts.md

これを `office/computation/playbooks/gaussian.md` の Lessons Learned に追記してよろしいですか？
```

### Step 5: Playbook への追記

ユーザーが OK と言ったら、対応する Playbook を **Read → Edit append** で更新：

1. `office/computation/playbooks/<tool>.md` を Read
2. `## Lessons Learned` セクション末尾を特定
3. 新エントリを末尾に Edit append（既存エントリは絶対に上書きしない）
4. frontmatter の `last_updated` を今日の日付に Edit 更新
5. **その教訓が「既定の推奨値を変えるべき」内容なら**（例: `recalcfc=20` を既定化、cutoff を上げる等）、Playbook の「**デフォルト推奨パラメータ**」ブロックの該当箇所も Edit で更新し、変更理由を 1 行添える（旧値 → 新値）。これで次回 `caw-input` の既定起点が最新になる（**Lessons Learned への追記だけで終わらせない**＝学習ループを閉じる）。

エントリフォーマット：

```markdown
### YYYY-MM-DD - <一行サマリ>

- **状況**: ...
- **原因**: ...
- **教訓**: ...
- **参照**: jobs/YYYY-MM-DD-<system>-<purpose>.md
```

### Step 6: 汎用知見の昇格判定（オプション）

知見が **特定の計算ソフトを超えた一般則** だった場合、汎用知見として保存を提案する。**保存先は使っている環境による**：

- **Claude Code で auto-memory を使っている場合**：`~/.claude/projects/<project>/memory/` に feedback memory を新規作成。
- **それ以外（Codex / Gemini、または memory 機能を使っていない）**：`office/computation/CLAUDE.md`（Codex/Copilot は `AGENTS.md`、Gemini は `GEMINI.md`）の「共通知見」節、または秘書の `secretary/notes/` に 1 行で記録。

```
この教訓は Gaussian だけでなく一般則として「PBC supercell の connectivity-based 分子抽出は必ず unwrap を伴う」に拡張できそうです。
（Claude Code なら memory に、そうでなければ computation の共通知見に）記録しますか？
```

ユーザーが OK なら、環境に応じた場所へ保存する。

### Step 7: 完了報告

```
追記完了：

- Playbook: office/computation/playbooks/gaussian.md
- 追加エントリ: ### 2026-05-13 - TS opt 終盤の Hessian 陳腐化は Lambda0 → 0 で検出可能
- last_updated: 2026-05-13 に更新
- memory feedback 昇格: ✅ feedback_gaussian_ts_hessian_staleness.md 新規作成

次セッション以降、関連キーワード（"TS opt", "Lambda0", "recalcfc"）の対話時に、本知見が自動参照されます。
```

---

## 過去データ一括取り込み（`_past-data/`）

ユーザーが「過去データを取り込んで」と言った場合、または計算ソフトディレクトリの
`_past-data/` にファイルが置かれている場合に発動する。初心者がオンボーディング直後に
過去の自分の計算を入れるだけで、Playbook がその人向けに最適化される導線。

### 手順

1. 対象ディレクトリ（例 `work/gaussian/_past-data/`）を走査し、入力・出力ファイルを列挙する
   （`.gjf`/`.com`/`.log`/`.inp`/`.out`/`.mdp` 等。サブフォルダも再帰）
2. 各入力から**繰り返し使われている設定**を集計する：
   - Gaussian: 汎関数・基底関数・`opt`/`freq`/`scrf` 等のルート、`%mem`/`%nproc`
   - GROMACS: integrator・dt・thermostat/barostat・cutoff scheme
   - CP2K: `RUN_TYPE`・汎関数+D3・`EPS_SCF`・basis/potential
3. 各出力から**成否と典型的な落とし穴**を集計する（正常終了率、よくあるエラー、
   収束に要した step 数の傾向など）
4. 集計結果を「この人の既定傾向」として `## Lessons Learned` に **1 エントリで seed**：
   - ヘッダ `### YYYY-MM-DD - _past-data 取り込み: 既定傾向の初期化`
   - 本文に「よく使う汎関数/basis」「標準的な mem/nproc」「頻出エラーと対処」を箇条書き
5. **生データは move/コピーしない**（`_past-data/` に置いたまま）。解析は読み取りのみ
6. 取り込み結果のサマリを報告し、`/caw-input` が以後この seed を既定起点に使うことを伝える

### 注意

- 過去データが大量なら全件読まず、**代表サンプリング**（直近・成功・失敗の各数件）で傾向を出す
- 個人の生データなので、要約のみを Playbook に書き、ファイル名や絶対パスの羅列は避ける
- 既存 Lessons Learned があれば**末尾追記**（既存方針どおり上書き禁止）

---

## 重要な注意事項

- **既存 Lessons Learned エントリは絶対に上書きしない**。末尾追記のみ
- **解析サマリ・Lessons Learned エントリは日本語（ユーザーの言語）で書く**（log は英語でも、抽出した知見は日本語に）
- **frontmatter の `last_updated` を必ず更新**（playbook の鮮度管理）
- **化学物理の用語は正確に**：汎関数名・基底関数・force field・cell parameter の表記揺れを起こさない
- **数値には単位を明記**：エネルギー (Hartree / eV / kcal/mol)、長さ (Å / bohr)、時間 (fs / ps / ns)、温度 (K)
- **再現性が確認できない知見は採用しない**：1 回限りの異常は「観測例」として記録、複数事例で確証された場合のみ「教訓」に昇格
- **Codex 二段レビューで防げた誤り**は積極的に記録（python-reviewer は構文、Codex は物理意味論の役割分担を残す）
- **ベンチマーク値はそのまま転記**：drift 率・wall time・parity slope 等は加工せず生数値で
