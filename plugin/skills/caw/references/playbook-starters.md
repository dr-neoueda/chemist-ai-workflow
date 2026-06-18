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

## Psi4

### computation/playbooks/psi4.md

````markdown
---
tool: Psi4
last_updated: "{{TODAY}}"
---

# Psi4 Playbook

## 概要

Psi4 の量子化学計算ノウハウ集積。OSS、Python ベースで script 化しやすい。

## 基本ルール

- 入力ファイル: `.in`（Python ベース）または対話的 `psi4` シェル
- 実行: `psi4 input.in -o output.out` または Python から `psi4.energy("scf/cc-pVDZ", molecule=mol)`
- 出力: `.out`、wfn オブジェクトを HDF5 で保存可能
- 並列: `psi4 -n <ncores>` でマルチスレッド

## デフォルト推奨パラメータ

- 単点: `energy('scf/cc-pVDZ')`
- 構造最適化: `optimize('b3lyp/6-31G(d)')`
- 振動数解析: `frequency('b3lyp/6-31G(d)')`
- 励起状態: `energy('eom-ccsd/cc-pVDZ')`
- 溶媒効果: `set pcm true` + PCM ブロック

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://psicode.org/
- Documentation: https://psicode.org/psi4manual/master/
````

---

## NAMD

### computation/playbooks/namd.md

````markdown
---
tool: NAMD
last_updated: "{{TODAY}}"
---

# NAMD Playbook

## 概要

NAMD の MD 計算ノウハウ集積。大規模生体分子系で実績あり、CHARMM FF と相性が良い。

## 基本ルール

- 入力ファイル: `.namd`（config）, `.psf`（topology）, `.pdb`（構造）, parameter file
- 実行: `namd3 +p<ncores> input.namd > output.log`
- 出力: `.dcd`（軌跡）, `.coor`/`.vel`/`.xsc`（restart）, `.log`

## デフォルト推奨パラメータ

- 平衡化（NVT）: `langevin on`, `langevinTemp 300`, `langevinDamping 1.0`
- 本計算（NPT）: `langevinPiston on`, `langevinPistonTarget 1.01325`, `langevinPistonPeriod 100`
- timestep: `timestep 2.0` (fs) with `rigidBonds all`
- cutoff: `cutoff 12.0`, `switching on`, `switchdist 10.0`, `pairlistdist 14.0`
- PME: `PME on`, `PMEGridSpacing 1.0`

## Force Field

- CHARMM36 / CHARMM-GUI 生成セットを推奨
- AMBER force field も読み込み可能（`amber on`, `parmfile`/`coordinates` で .prmtop/.inpcrd を指定）

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.ks.uiuc.edu/Research/namd/
- Tutorial: https://www.ks.uiuc.edu/Training/Tutorials/namd/namd-tutorial-unix-html/
````

---

## LAMMPS

### computation/playbooks/lammps.md

````markdown
---
tool: LAMMPS
last_updated: "{{TODAY}}"
---

# LAMMPS Playbook

## 概要

LAMMPS の MD 計算ノウハウ集積。Sandia 発の汎用 MD。potentialの自由度が高く、材料系・MLIP との連携で実績多い。

## 基本ルール

- 入力ファイル: `in.<system>`（コマンドスクリプト形式）, `data.<system>`（構造 + topology）
- 実行: `lmp -in in.<system> -log log.<system>`
- 出力: `dump.*.lammpstrj`, `log.*`, `restart.*`

## デフォルト推奨パラメータ

- units: `units real`（一般有機）または `units metal`（材料）
- atom_style: `atom_style full`（OPLS/GAFF 系）or `atomic`（金属）
- pair_style: `pair_style lj/cut/coul/long 10.0` + `kspace_style pppm 1.0e-4`
- thermostat: `fix nvt all nvt temp 300.0 300.0 100.0`
- barostat: `fix npt all npt temp 300 300 100 iso 1.0 1.0 1000`
- timestep: `timestep 1.0` (fs, units real) or `timestep 0.001` (ps, units metal)

## MLIP 連携

- MACE: `pair_style mace`（lammps-mace パッケージ）
- DeePMD-kit: `pair_style deepmd`（OSS）
- NequIP: `pair_style nequip`

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.lammps.org/
- Manual: https://docs.lammps.org/
- Examples: https://github.com/lammps/lammps/tree/develop/examples
````

---

## OpenMM

### computation/playbooks/openmm.md

````markdown
---
tool: OpenMM
last_updated: "{{TODAY}}"
---

# OpenMM Playbook

## 概要

OpenMM の MD 計算ノウハウ集積。Python ネイティブ、GPU 加速が標準、HPC でも個人 workstation でも回しやすい。

## 基本ルール

- 入力: Python script、構造は `.pdb` / `.psf` / `.prmtop`
- 実行: `python sim.py` または notebook 内
- 出力: `DCDReporter` / `StateDataReporter` で軌跡・log

## デフォルト推奨パターン

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

pdb = PDBFile('input.pdb')
forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
                                  nonbondedCutoff=1.0*nanometer,
                                  constraints=HBonds)
integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
simulation = Simulation(pdb.topology, system, integrator)
simulation.context.setPositions(pdb.positions)
simulation.minimizeEnergy()
simulation.reporters.append(DCDReporter('out.dcd', 1000))
simulation.reporters.append(StateDataReporter('out.log', 1000, step=True, potentialEnergy=True, temperature=True))
simulation.step(500000)
```

## Force Field

- Amber14 / Amber99sb-ildn
- CHARMM36（CHARMM-GUI 経由）
- OpenFF（OpenForceField initiative、化学多様性高）

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://openmm.org/
- Documentation: http://docs.openmm.org/
- Cookbook: https://github.com/openmm/openmm-cookbook
````

---

## ChimeraX

### computation/playbooks/chimerax.md

---
tool: ChimeraX
last_updated: 2026-06-18
---

# ChimeraX Playbook

## 概要

UCSF ChimeraX の構造可視化・密度マップフィッティング・解析でのノウハウ集積。`fitmap`（モデルの density map へのフィット）・`molmap`・`measure correlation`・`matchmaker`・`morph`・ISOLDE 連携（cryo-EM モデル構築）・ヘッドレス実行をカバー。

## 基本ルール

- コマンドスクリプトは `.cxc`、複雑なロジックは `.py`（`runscript`）。セッションは `.cxs`
- バッチ/ヘッドレスは `chimerax --nogui --script x.cxc --exit`。サーバで画像レンダが要るなら `--offscreen`（Linux/OSMesa・GPU 不使用）
- `fitmap` は局所最適化。フィット前にモデルをマップ付近へ初期配置する（ずれていると収束しない）
- 密度マップは閾値（level）と解像度を明示。`molmap` で計算マップを作るときは解像度を実験値に合わせる

## デフォルト推奨パラメータ

- フィット: `fit #1 inMap #2`（複数開始点を試すなら `search N`）。剛体フィットが基本、柔軟化は ISOLDE
- 相関の確認: `measure correlation #1 #2`、`fitmap` 出力の correlation / overlap / average map value
- 画像: `save image.png width 2000 height 1500 supersample 3`

## Lessons Learned

<!-- 計算を重ねるごとに知見を追記。最新のものを上に。 -->

### YYYY-MM-DD - <一行サマリ>

- **状況**:
- **原因**:
- **教訓**:
- **参照**: jobs/YYYY-MM-DD-<system>-fit.md

## 参考リンク

- UCSF ChimeraX User Guide（`fitmap` / `molmap` / `measure correlation` コマンド）
- ISOLDE（cryo-EM モデル rebuilding プラグイン）

## Python ライブラリ Playbook

化学計算ソフトの入出力だけでなく、Python ライブラリの API quirks・version 依存挙動・よくある罠も Playbook 化しておく。AI が新しいスクリプトを書く際に必ず最新の Playbook を読み、過去の失敗を再発させない。

### computation/playbooks/rdkit.md

````markdown
---
tool: RDKit
type: python-library
last_updated: "{{TODAY}}"
---

# RDKit Playbook

## 概要

RDKit（cheminformatics Python ライブラリ）の API 利用ノウハウ。SMILES 操作・分子描画・記述子計算・反応スキーム解析など。

## 基本ルール

- import: `from rdkit import Chem; from rdkit.Chem import AllChem, Draw, Descriptors`
- 分子読み込み: `Chem.MolFromSmiles("CCO")`、`Chem.MolFromMolFile("mol.mol")`、`Chem.MolFromPDBFile("input.pdb")`
- 3D 化: `mol = Chem.AddHs(mol); AllChem.EmbedMolecule(mol); AllChem.UFFOptimizeMolecule(mol)`
- 出力: `Chem.MolToSmiles(mol)`, `Chem.MolToMolFile(mol, "out.mol")`

## よくある罠

- **`Chem.MolFromSmiles` は失敗時に `None` を返す**（例外を投げない）。必ず `if mol is None: ...` でチェック
- **アロマ化フラグ**：`Chem.SanitizeMol` を通さないとアロマ判定が反映されないことがある
- **Atom ordering** は入力順とは限らない。`mol.GetAtoms()` 順を信頼するなら `Chem.GetMolFrags(mol)` で確認
- **3D embedding の seed**：`AllChem.EmbedMolecule(mol, randomSeed=42)` で再現性確保

## デフォルト推奨パターン

- 記述子計算: `Descriptors.MolWt(mol)`, `Descriptors.MolLogP(mol)`, `Descriptors.NumHAcceptors(mol)`
- 類似性: `from rdkit import DataStructs; DataStructs.TanimotoSimilarity(fp1, fp2)`
- フィンガープリント: `AllChem.GetMorganFingerprintAsBitVect(mol, 2, 1024)`

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.rdkit.org/
- Documentation: https://www.rdkit.org/docs/
- Blog: https://greglandrum.github.io/rdkit-blog/
````

### computation/playbooks/ase.md

````markdown
---
tool: ASE
type: python-library
last_updated: "{{TODAY}}"
---

# ASE Playbook

## 概要

ASE（Atomic Simulation Environment）の API 利用ノウハウ。構造操作・I/O（Gaussian / VASP / Quantum ESPRESSO / CIF 等の変換）、calculator 抽象化、MD・最適化の上位ラッパー。

## 基本ルール

- import: `from ase import Atoms; from ase.io import read, write; from ase.calculators.<...> import <Calc>`
- 構造読み込み: `atoms = read("system.cif")` / `read("POSCAR")` / `read("input.xyz")` / `read("out.log")`（Gaussian/VASP log にも対応）
- 構造書き出し: `write("out.xyz", atoms)`, `write("POSCAR", atoms)`, `write("input.gjf", atoms)`
- Calculator: `atoms.calc = EMT()` / `Gaussian(...)` / `Vasp(...)` / `MACECalculator(model_path)`

## よくある罠

- **PBC 設定**：`atoms.set_pbc([True, True, True])` を忘れると周期境界が無視される
- **cell 設定**：`atoms.set_cell([a, b, c])` の単位は Å。3x3 行列でも OK
- **wrap / unwrap**：MD 軌跡から bond 計算する時は `atoms.wrap()` の挙動に注意（unwrap 必須のケース多数）
- **neighbor list**：`from ase.neighborlist import NeighborList; nl = NeighborList(...)` で構築。cutoff の単位は Å、bothways=True 推奨
- **energy / force の単位**：ASE 内部は eV / eV·Å⁻¹

## MLIP との連携

- MACE: `from mace.calculators import MACECalculator; atoms.calc = MACECalculator(model_path)`
- Allegro: `from allegro.calculators import AllegroCalculator`
- M3GNet: `from m3gnet.models import M3GNet; atoms.calc = M3GNet.load()`

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://wiki.fysik.dtu.dk/ase/
- ase.io 一覧: https://wiki.fysik.dtu.dk/ase/ase/io/io.html
````

### computation/playbooks/mdanalysis.md

````markdown
---
tool: MDAnalysis
type: python-library
last_updated: "{{TODAY}}"
---

# MDAnalysis Playbook

## 概要

MDAnalysis の API 利用ノウハウ。GROMACS / NAMD / LAMMPS / AMBER 等の trajectory を統一 API で解析。

## 基本ルール

- import: `import MDAnalysis as mda`
- Universe: `u = mda.Universe("topol.tpr", "traj.xtc")`（topology + trajectory）
  - GROMACS: `.tpr` + `.xtc`/`.trr`
  - NAMD: `.psf` + `.dcd`
  - LAMMPS: `.data` + `.lammpstrj`（custom dump 形式は要 reader 指定）
  - AMBER: `.prmtop` + `.nc`/`.trj`
- AtomGroup 選択: `u.select_atoms("name CA and resid 1-100")`
- フレーム反復: `for ts in u.trajectory: ...`、`u.trajectory[i]` で indexing 可能

## よくある罠

- **frame 番号の base**：0-based。論文・実験慣習の 1-based と混同しない
- **time vs step**：`ts.time` は ps 単位、`ts.frame` はインデックス
- **PBC**：`u.select_atoms(...).positions` は wrap 座標。bond 計算前に `u.atoms.unwrap()` を呼ぶ
- **memory load**：`mda.Universe(..., in_memory=True)` で全 frame を一括ロード。大きい trajectory は streaming で
- **selection 高速化**：`u.select_atoms("...")` は frame ごとに再評価。固定なら `ag = u.select_atoms("...")` で 1 回だけ評価し、`ag.positions` を frame ごとに参照

## デフォルト推奨パターン

```python
# RMSD 解析
from MDAnalysis.analysis import rms
R = rms.RMSD(u, u, select="backbone").run()
# R.rmsd shape: (n_frames, 3)  [frame, time, rmsd]

# RDF 解析
from MDAnalysis.analysis.rdf import InterRDF
g_OO = InterRDF(O_atoms, O_atoms, nbins=200, range=(0, 10)).run()
```

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://www.mdanalysis.org/
- User Guide: https://userguide.mdanalysis.org/
- API: https://docs.mdanalysis.org/
````

### computation/playbooks/pymatgen.md

````markdown
---
tool: pymatgen
type: python-library
last_updated: "{{TODAY}}"
---

# pymatgen Playbook

## 概要

pymatgen（Python Materials Genomics）の API 利用ノウハウ。VASP / QE / Gaussian の入出力、Materials Project API、結晶構造解析。

## 基本ルール

- import: `from pymatgen.core import Structure, Lattice, Molecule; from pymatgen.io.vasp import Vasprun, Poscar`
- Structure: `Structure.from_file("POSCAR")` / `Structure.from_file("input.cif")`
- Molecule: `Molecule.from_file("mol.xyz")` / `Molecule.from_file("input.gjf")`
- 書き出し: `s.to(filename="POSCAR")` / `s.to(fmt="cif", filename="out.cif")`

## VASP 解析

- run の解析: `vr = Vasprun("vasprun.xml")`, `vr.final_energy`, `vr.eigenvalue_band_properties`
- DOS: `dos = vr.complete_dos`, `plotter = DosPlotter(); plotter.add_dos("Total", dos)`
- Band: `bs = vr.get_band_structure()`, `BSPlotter(bs).get_plot()`

## Materials Project 連携

```python
from mp_api.client import MPRester
with MPRester(api_key=os.environ["MP_API_KEY"]) as mpr:
    docs = mpr.materials.summary.search(elements=["Li", "Co", "O"], num_chunks=1)
```

## よくある罠

- **VASP version**：vasprun.xml のフォーマットは VASP version で微妙に異なる。新しい pymatgen でないと parse error
- **CIF symmetry**：`Structure.from_file("foo.cif")` で symmetry 情報を保持。`Structure(lattice, species, coords)` 直接構築だと P1 扱い
- **fractional vs cartesian**：`Structure.frac_coords` と `Structure.cart_coords` の混同に注意
- **MP API key**：環境変数 `MP_API_KEY` が必要、登録は無料

## Lessons Learned

### YYYY-MM-DD - <一行サマリ>

- 状況:
- 原因:
- 教訓:

## 参考リンク

- 公式: https://pymatgen.org/
- API: https://pymatgen.org/pymatgen.html
- Materials Project: https://materialsproject.org/
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

---

## 計算外ソフトの Playbook（参考）

スライド生成・論文執筆・申請書執筆など、計算ソフト以外の **再現可能な手順** が必要な部署にも同じ Playbook 思想が適用できる。これらは個別の Skill で実装されている:

| 部署 | Skill | Playbook 相当の知見の場所 |
|---|---|---|
| presentation | `caw-slides` | `references/style-guide.md`（14 セクション + canonical 実装パターン）+ `references/pptx_helpers.py`（1000+ 行ヘルパ）+ 4 用途バリアントテンプレート |
| writing | （Phase 2 で追加予定） | `work/manuscripts/_style/` 配下の文体プロファイル |

`caw-slides` の場合、新しい失敗パターン（フォント豆腐・shape 重なり・L1 違反など）を見つけたら `office/presentation/CLAUDE.md` (or AGENTS.md) の Lessons Learned セクションに追記する。スタイルガイド本体（plugin 同梱の `references/style-guide.md`）は plugin 更新で上書きされるため触らない。
