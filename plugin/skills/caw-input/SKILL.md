---
name: caw-input
description: >
  計算ソフト別の入力ファイル雛形を対話的に生成するスキル。
  Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO に対応。
  Playbook のデフォルト推奨値を起点に、ユーザーの系と目的に合わせて入力ファイルとジョブ記録を 1 計算 1 サブディレクトリ単位で配置する。
trigger: /caw-input
---

# caw-input — 計算入力ジェネレータ

## いつ使うか

- `/caw-input` を実行したとき
- ユーザーが「Gaussian で benzene の構造最適化したい」「ORCA の入力ファイル作って」「CP2K の AIMD 雛形くれる？」など、**計算ソフト + 目的**を指定したとき
- 計算ジョブの新規立ち上げ時

`office/computation/` が存在しない場合、`/caw` で computation 部署を追加することを促す。

---

## はじめてモードを尊重する

このスキルを実行する前に `office/CLAUDE.md`（Codex CLI / GitHub Copilot CLI では `AGENTS.md`）を読み、冒頭に `> 運用モード: はじめて` があれば、`caw` skill の「はじめてモードの挙動」を全応答に適用する：**平易な日本語**で話し、専門用語（化学・計算手法・書誌の用語）は初出で 1 行説明を添え、各ステップの最後に**「次はこれをしましょう」を 1 つ**だけ提示する。元に戻せない操作（削除・上書き・外部登録・送信）は必ず事前確認する。

## ワークフロー

### Step 1: 計算ソフトの確定

ユーザー入力から計算ソフトを判定。曖昧な場合は `AskUserQuestion` で 1 問確認：

```
Q1: どの計算ソフトの入力ファイルを生成しますか？
  - Gaussian
  - ORCA
  - CP2K
  - GROMACS
  - VASP
  - Quantum ESPRESSO
```

選択されたソフトに対応する Playbook を最初に読む：
- `office/computation/playbooks/<tool>.md`（存在しない場合は `references/playbook-starters.md` から該当セクションを参照）

あわせて `office/computation/CLAUDE.md`（Codex / GitHub Copilot は `AGENTS.md`、Gemini は `GEMINI.md`）も読む — オンボーディングの計算環境（Q6）で記録された **submission の既定**（HPC か local か、queue・walltime・並列数・module load・account など）を、後段の実行スクリプト生成（Step 5）で使う。

### Step 2: 計算目的の確定

ソフトごとに用途を確認（`AskUserQuestion` 推奨）：

#### Gaussian / ORCA

- 単点エネルギー（SP）
- 構造最適化（Opt）
- 構造最適化 + 振動解析（Opt + Freq）
- 遷移状態探索（TS）
- IRC 計算
- 励起状態（TD-DFT）

#### CP2K

- 単点（SP, RUN_TYPE=ENERGY）
- 構造最適化（GEO_OPT）
- AIMD（MD, NVT/NPT）
- セル最適化（CELL_OPT）

#### GROMACS

- エネルギー最小化（em.mdp）
- NVT 平衡化
- NPT 平衡化
- プロダクション MD

#### VASP

- 単点（IBRION=-1, NSW=0）
- 構造最適化（IBRION=2, ISIF=3）
- AIMD（IBRION=0, MDALGO=2）
- DFT+U / HSE / SOC

#### Quantum ESPRESSO

- SCF（pw.x）
- 構造最適化（vc-relax）
- フォノン（ph.x）
- バンド構造

### Step 3: 系（system）情報の取得

以下を `AskUserQuestion` または対話で収集：

- 系の通称（例: "benzene", "C6H6 ring", "MOF-5 unit cell"）
- 電荷・スピン多重度（量子化学の場合）
- 初期座標：
  - 既存ファイル指定（`.xyz`, `.gjf`, `.cif`, `.pdb` 等）
  - SMILES → RDKit で 3D 生成
  - 既知の幾何（D6h benzene 等）→ 内部生成
- 周期境界（周期系 DFT / MD の場合）：cell parameters
- 力場（GROMACS の場合）：OPLS-AA / CHARMM36 / GAFF 等

### Step 4: 計算条件の確定（Playbook デフォルト起点）

Playbook の「デフォルト推奨パラメータ」を基準にしつつ、**`## Lessons Learned` の新しい教訓で上書き**して提示する（例: Lessons Learned に「`recalcfc=20` を既定に」とあれば推奨値へ反映）。**デフォルトブロックと Lessons Learned が食い違うときは、後から追記された Lessons Learned を優先**する。ユーザーが OK なら採用、変更要望があれば調整。

例（Gaussian Opt + Freq）:

```
推奨パラメータ：
- 汎関数: B3LYP
- 基底: 6-31G(d)
- 計算種: opt freq=noraman
- 並列: %nprocshared=8
- メモリ: %mem=8GB

これで進めますか？ それとも調整しますか（例: M06-2X / def2-TZVP / D3BJ）？
```

例（ORCA Opt + Freq）:

```
推奨パラメータ：
! B3LYP def2-SVP D3BJ Opt Freq TightSCF
%pal nprocs 8 end
%maxcore 2000

これで進めますか？
```

### Step 5: 作業ディレクトリ + 入力ファイル生成

**配置場所のルール（caw 規約）**: `<tool>/<system>_<purpose>_<YYYYMMDD>/`

```bash
mkdir -p <tool>/<system>_<purpose>_<YYYYMMDD>
```

例: `work/gaussian/benzene_opt_20260513/` / `work/orca/benzene_opt_20260513/` / `work/cp2k/water-box_aimd_20260513/`

このサブディレクトリに **入力ファイル + 実行スクリプト** を配置：

#### Gaussian

- `<system>.gjf` — 入力
- `run_<system>.sh` — qsub / sbatch 用ジョブスクリプト（HPC 利用時）

#### ORCA

- `<system>.inp` — 入力
- `run_<system>.sh` — ジョブスクリプト

#### CP2K

- `<system>.inp` — 入力（&GLOBAL / &FORCE_EVAL / &MOTION の階層構造）
- `run_<system>.sh` — ジョブスクリプト

#### GROMACS

- `<purpose>.mdp` — MD パラメータ（em.mdp / nvt.mdp / npt.mdp / md.mdp）
- 既存の `.gro` / `.top` を参照
- `run_<system>.sh` — `gmx grompp` + `gmx mdrun` の連続実行

#### VASP

- `INCAR` / `POSCAR` / `KPOINTS`（POTCAR は別途準備促す）
- `run_<system>.sh`

#### Quantum ESPRESSO

- `<system>.in` — namelist 形式
- `run_<system>.sh`

### Step 6: ジョブ記録の作成

`office/computation/jobs/YYYY-MM-DD-<system>-<purpose>.md` に記録：

```markdown
# YYYY-MM-DD <system> <purpose>

## 目的

<計算の目的、何を確認したいか>

## 入力

- 入力ファイル: `../../../<tool>/<system>_<purpose>_<YYYYMMDD>/<system>.<ext>`
- 系: <分子式・charge・multiplicity>
- 初期構造: <出典 or 生成方法>

## パラメータ

- 汎関数 / force field: ...
- 基底 / cutoff: ...
- 計算種: ...
- 並列: ...
- Playbook: `../playbooks/<tool>.md`

## 実行コマンド

\`\`\`bash
cd ../../../<tool>/<system>_<purpose>_<YYYYMMDD>/
<実行コマンド>
\`\`\`

## 結果

- [ ] 実行待ち
- 最終 SCF / エネルギー: TBD
- 収束判定: TBD
- 振動解析（該当時）: TBD

## 次のアクション

- [ ] 実行 → log 確認
- [ ] 必要なら精度拡張 / 範囲拡張
- [ ] 知見があれば Playbook の Lessons Learned に追記
```

### Step 7: 完了報告

ユーザーに以下を報告：

```
入力ファイル生成完了：

- 作業ディレクトリ: <tool>/<system>_<purpose>_<YYYYMMDD>/
- 入力: <file>
- ジョブ記録: office/computation/jobs/YYYY-MM-DD-<system>-<purpose>.md

実行コマンド:
  cd <tool>/<system>_<purpose>_<YYYYMMDD>/
  <実行コマンド>

実行後、log の確認は秘書に「結果を確認して」と伝えてください。
```

---

## バッチ／スキャン生成（複数系・複数手法）

「benzene を B3LYP と M06-2X で」「複数分子をまとめて」のように **複数の系または手法（汎関数・基底のスキャン）** を指定された場合、各組み合わせを **1 計算 1 サブディレクトリ**で一括生成する：

- ディレクトリ名で組み合わせを区別：`work/<tool>/<system>_<purpose>_<method-slug>_<YYYYMMDD>/`（例 `work/gaussian/benzene_opt_b3lyp_20260618/`, `..._m062x_20260618/`）。
- 各々に入力＋実行スクリプト、`jobs/` 記録もそれぞれ作る。
- 件数が多いときは**生成する組み合わせ一覧を先に提示して確認**を取る（無断で大量生成しない）。
- 共通部分（系・基底など）は Playbook 既定を共有し、振る軸（汎関数など）だけ変える。

---

## 重要な注意事項

- **物理量には必ず単位コメント**（例: `# 1 fs`, `# 300 K`, `# 1 atm`, `# Å`）
- **エネルギー単位を統一**（Hartree / eV / kcal/mol / kJ/mol — ジョブ記録に明記）
- **乱数シードを固定**（MD の場合、再現性確保）
- **計算手法の選択は Playbook の Lessons Learned を踏まえる**（過去の失敗事例があれば回避策を組み込む）
- **HPC ジョブスクリプトは環境固有**：queue 名・walltime・並列数・モジュール load 順・account は、**まず `office/computation/CLAUDE.md` の submission 既定（オンボ Q6）** を使う。無ければ Playbook の過去事例、それも無ければユーザーに確認。**local 実行（SLURM 等を使わない）** 設定ならジョブスクリプトの代わりに直接実行コマンドを出す
- **入力ファイル・ジョブ記録は上書きしない**：同名サブディレクトリがあれば `<YYYYMMDD>` を `<YYYYMMDD>_v2` などに拡張。`jobs/...md` も同名があれば末尾に `-2` を付ける
- **化学物理の用語は正確に**：汎関数名（B3LYP は B3LYP）、基底（def2-SVP は def2-SVP）、force field（OPLS-AA / CHARMM36）の表記揺れを起こさない
