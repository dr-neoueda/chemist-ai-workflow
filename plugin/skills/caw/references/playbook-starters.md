# 計算ソフト Playbook 雛形集

`/caw` のオンボーディング Step 3 で、computation 部署が選択され、かつ Q2 で計算カテゴリが指定された場合に、該当ソフトの Playbook を `computation/playbooks/<tool>.md` として配置するためのテンプレート。

各 Playbook は最小限のエントリで起動して、運用中にユーザーと AI 部署が**罠と処方**を追記していく前提。

---

## Gaussian

### computation/playbooks/gaussian.md

````markdown
---
tool: Gaussian
last_updated: "{{TODAY}}"
---

# Gaussian Playbook

## 概要

Gaussian の入力作成・実行・log 解析でのノウハウ集積。罠と処方を Lessons Learned に追記していく。

## 基本ルール

- 入力ファイル `.gjf` / `.com`、出力 `.log` / `.chk` / `.fchk`
- 計算レベルの命名: `<functional>/<basis>` 例: `B3LYP/6-31G(d)`
- chk ファイルから geom 抽出: `formchk *.chk` → `.fchk` を cclib で解析
- HPC ジョブ submission: `g16 input.gjf` または `qsub run.sh`

## デフォルト推奨パラメータ

- 構造最適化: `opt freq=noraman`
- TS 探索: `opt=(ts,calcfc,recalcfc=20,maxstep=6) freq=noraman`
- 単点計算: `# B3LYP/6-31G(d) sp`
- 溶媒効果: `scrf=(pcm,solvent=water)`

## Lessons Learned

（実運用で得られた罠と処方を時系列で追記）

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:
- 参照:

## 参考リンク

- 公式: https://gaussian.com/
- cclib（log 解析）: https://cclib.github.io/
````

---

## GROMACS

### computation/playbooks/gromacs.md

````markdown
---
tool: GROMACS
last_updated: "{{TODAY}}"
---

# GROMACS Playbook

## 概要

GROMACS の MD 計算でのノウハウ集積。

## 基本ルール

- 入力ファイル: `.mdp`（パラメータ）, `.gro`（構造）, `.top`（topology）, `.ndx`（index）
- 実行: `gmx grompp -f md.mdp -c init.gro -p topol.top -o md.tpr` → `gmx mdrun -deffnm md`
- 結果: `.xtc`（軌跡）, `.edr`（エネルギー）, `.log`, `.gro`
- バージョン依存挙動に注意（特に `mdp` のキー名）

## デフォルト推奨パラメータ

- 平衡化（NVT）: `integrator = md, dt = 0.002, nsteps = 100000, tcoupl = v-rescale`
- 本計算（NPT）: `integrator = md, dt = 0.002, pcoupl = Parrinello-Rahman, tau_p = 2.0`
- cutoff scheme: `cutoff-scheme = Verlet, rcoulomb = 1.0, rvdw = 1.0`
- 出力頻度: 用途別に調整（軌跡保存は 10 ps 間隔程度）

## Force Field

- 一般有機: OPLS-AA, AMBER (GAFF), CHARMM36
- 水: TIP3P, SPC/E, TIP4P/2005
- イオン: Joung-Cheatham
- それぞれ `.top` の `[ defaults ]` セクションで明記

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.gromacs.org/
- MDAnalysis（解析）: https://www.mdanalysis.org/
````

---

## CP2K

### computation/playbooks/cp2k.md

````markdown
---
tool: CP2K
last_updated: "{{TODAY}}"
---

# CP2K Playbook

## 概要

CP2K（Quickstep DFT-MD）の計算ノウハウ集積。BOMD/AIMD、結晶系最適化、MLIP 訓練データ生成などをカバー。

## 基本ルール

- 入力ファイル: `.inp`（メイン）, `.psf` / `.pdb`（構造を別ファイルで参照する場合）
- 実行: `cp2k.psmp -i input.inp -o output.log`
- 出力: `<project_name>-1.restart`, `*.cell`, `*.xyz`, `*.ener`
- 並列実行: MPI + OpenMP のハイブリッド推奨

## デフォルト推奨パラメータ

- 単点 / 構造最適化: `RUN_TYPE GEO_OPT` または `ENERGY`
- BOMD: `RUN_TYPE MD`, `ENSEMBLE NVT` + `NOSE` thermostat
- AIMD: 同上、`MOTION/MD/TIMESTEP` を 0.5 fs 程度に
- 基底関数: `BASIS_SET_FILE_NAME GTH_BASIS_SETS`, `POTENTIAL_FILE_NAME GTH_POTENTIALS`
- 汎関数: `BLYP-D3` または `PBE-D3`
- cutoff: `CUTOFF 400` (Ry), `REL_CUTOFF 60` (Ry)
- SCF: `EPS_SCF 1.0E-6`, `MAX_SCF 50`

## 結晶系の運用

- セル: `CELL/A`, `CELL/B`, `CELL/C` でラティスベクトル指定
- 周期境界: `PERIODIC XYZ`
- restart: `EXT_RESTART` で前ジョブの restart ファイルを継承

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.cp2k.org/
- Manual: https://manual.cp2k.org/
````

---

## ORCA

### computation/playbooks/orca.md

````markdown
---
tool: ORCA
last_updated: "{{TODAY}}"
---

# ORCA Playbook

## 概要

ORCA の量子化学計算ノウハウ集積。学術無料で人気の QC ソフト。

## 基本ルール

- 入力ファイル: `.inp`、出力 `.out` または `.log`
- 実行: `orca input.inp > output.out`
- 結果: `.gbw`（軌道）, `.xyz`（最適化構造）, `.hess`（Hessian）

## デフォルト推奨パラメータ

- 単点: `! B3LYP def2-SVP TightSCF`
- 構造最適化: `! B3LYP def2-SVP Opt Freq TightSCF`
- TS 探索: `! B3LYP def2-SVP OptTS NumFreq TightSCF`
- 溶媒効果: `! CPCM(water)` または `! SMD(water)`
- 並列: `! PAL8`（8 コア並列）

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.faccts.de/orca/
- Forum: https://orcaforum.kofo.mpg.de/
````

---

## VASP

### computation/playbooks/vasp.md

````markdown
---
tool: VASP
last_updated: "{{TODAY}}"
---

# VASP Playbook

## 概要

VASP の周期系 DFT 計算ノウハウ集積。材料科学・固体物理で標準的。

## 基本ルール

- 入力 4 点セット: `INCAR`（計算設定）, `POSCAR`（構造）, `KPOINTS`（k 点）, `POTCAR`（擬ポテンシャル）
- 実行: `vasp_std` または `vasp_gam`（gamma 点のみ）
- 出力: `OUTCAR`, `CHGCAR`, `WAVECAR`, `vasprun.xml`, `XDATCAR`

## デフォルト推奨パラメータ（INCAR）

- 単点: `IBRION=-1, NSW=0, ALGO=Fast, EDIFF=1E-5`
- 構造最適化: `IBRION=2, NSW=100, ISIF=3, EDIFF=1E-5, EDIFFG=-0.01`
- AIMD: `IBRION=0, NSW=1000, MDALGO=2, TEBEG=300, SMASS=0.5`
- DFT+U: `LDAU=.TRUE., LDAUTYPE=2, LDAUL/U/J=...`
- HSE: `LHFCALC=.TRUE., HFSCREEN=0.2, GGA=PE`
- 並列: `KPAR`, `NCORE`, `NPAR` を環境に合わせて調整

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.vasp.at/
- Wiki: https://www.vasp.at/wiki/
- pymatgen（解析）: https://pymatgen.org/
````

---

## Quantum ESPRESSO

### computation/playbooks/quantum-espresso.md

````markdown
---
tool: Quantum ESPRESSO
last_updated: "{{TODAY}}"
---

# Quantum ESPRESSO Playbook

## 概要

Quantum ESPRESSO（QE）の周期系 DFT 計算ノウハウ集積。OSS の平面波 DFT ソフト。

## 基本ルール

- 入力: `.in`（namelist 形式）, 擬ポテンシャル `.UPF`
- 実行モジュール: `pw.x`（SCF/relax/MD）, `ph.x`（フォノン）, `dos.x`（DOS）等
- 出力: `.out`, `<prefix>.save/` ディレクトリ

## デフォルト推奨パラメータ

- 単点: `calculation = 'scf', ecutwfc = 50, ecutrho = 400`
- 構造最適化: `calculation = 'vc-relax', ion_dynamics = 'bfgs', cell_dynamics = 'bfgs'`
- AIMD: `calculation = 'cp', dt = 5.0`
- k 点: 自動 `K_POINTS automatic` または明示
- 擬ポテンシャル: PBE / PBESol / LDA を SSSP / pslibrary から取得

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.quantum-espresso.org/
- SSSP: https://www.materialscloud.org/discover/sssp/
````

---

## その他の対応ソフト（雛形のみ）

ユーザーが Q2 で別のソフトを指定した場合の汎用雛形。`<tool>` を該当名に置換して配置。

### computation/playbooks/<tool>.md

````markdown
---
tool: <ToolName>
last_updated: "{{TODAY}}"
---

# <ToolName> Playbook

## 概要

<ToolName> の計算ノウハウ集積。

## 基本ルール

- 入力ファイル:
- 実行コマンド:
- 出力形式:

## デフォルト推奨パラメータ

（運用しながら埋める）

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式:
````

---

## Playbook の運用ルール（再掲）

- セッション開始時、対象計算ソフトの Playbook を**必ず最初に読む**
- 計算が失敗 / 想定外の挙動を示した時は、原因を解析して **Lessons Learned に追記**
- `last_updated` フィールドを必ず更新
- **既存エントリの上書き禁止、末尾追記のみ**
- 数値計算スクリプトのバグや汎関数 / basis の選択ミスなど、再現させない知見を体系化する
