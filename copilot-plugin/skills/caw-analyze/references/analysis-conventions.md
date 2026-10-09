# caw-analyze 解析規約 — 取込アダプタ / 外部ソフト orchestration / 高リスク解析ガードレール

> 根拠: 化学全16領域のカバレッジ監査（2026-07-01）。全領域が partial ＝ 下流解析は汎用ツールで回るが、
> **一次データ還元（ベンダーバイナリ取込・専用ソフト依存）** が共通の境界。ここを **手法別スキルを増やさず、
> 3 つの汎用規約＋playbook レシピ** で埋める。設計背景は [`docs/chemistry-coverage-audit.md`](../../../../docs/chemistry-coverage-audit.md)。

## 資産 1 — 取込アダプタ規約（ベンダーバイナリ → 中立形式）

汎用 Python（pandas/numpy）は測定装置の**独自バイナリを直読できない**。手法別パーサは出荷しない。代わりに
**「独自形式 → 中立形式（CSV / mzML / ASCII / extxyz / JSON）への変換レシピ」を都度組み、ユーザーの playbook に蓄積**する。

1. **OSS リーダを優先**（インストールしてその場で使う）:
   - 質量分析/クロマト: **msconvert (ProteoWizard)** で `.raw/.d/.wiff` → `mzML`；`pyteomics`/`psims`/`matchms` で読む。
   - 電気化学: `galvani`（BioLogic `.mpr`）・`NewareNDA`（`.nda/.ndax`）。
   - 蛍光寿命/過渡吸収: `sdtfile`（`.sdt`）・`readPTU`（`.ptu`）。
   - 電顕: `mrcfile`（`.mrc`）・`hyperspy`（`.dm3/.dm4/.emd`）。
   - 回折/結晶: `fabio`（フレーム）・`gemmi`（CIF/mmCIF/MTZ）。
   - IR: `brukeropus` 等（OPUS `.0/.spa`）。
2. **OSS が対象環境で壊れている形式は native 実装を検討**（判断軸＝(a) 対象環境で動くか (b) 合成フィクスチャで TDD 可能か）。
   例: `nmrglue` は numpy≥2 で import 破綻の実績 → Bruker FID を `acqus`+`fid` から stdlib 直読する native パーサを 1 回だけ書き playbook 化。**合成不可のバイナリ（`.mpr` 等）は据え置き、ユーザーのエクスポートを前提**にする。
3. **合成フィクスチャで TDD** してから配布物に入れる（無テストのバイナリパーサは出さない）。
4. **取込＝レシピ**：確立した変換手順は `work/analyses/_playbook/<topic>.md` に「元形式・使ったリーダ/native 手順・落とし穴」を残す（使うほど装置スタックに特化）。

## 資産 2 — 外部専用 CLI/ライブラリの orchestration 契約

各分野を定義する raw 還元は 40 年分の専用ソフト資産に依存する。**scriptable なものは caw-analyze が駆動し規律をラップ**、
**GUI/MATLAB でしか回せないものは正直にスコープ外**と宣言する（できることを誇張しない）。

- **caw-analyze が orchestrate できる（scriptable / Python-API）** — `subprocess` か Python API で駆動し、
  入出力の規律（**バージョン・パラメータ・R²/Rwp/χ²/残差を正直に開示**）を caw 側でラップする:
  - 結晶: **GSAS-II scriptable**（Le Bail/Rietveld）・`cctbx`/`gemmi`。
  - XAS: **xraylarch**（正規化・EXAFS）。地球化学: **phreeqpython**（PHREEQC）。
  - 時間分解: **pyglotaran/KiMoPack**（global/target）。電気化学: **impedance.py/pyDRTtools**（EIS 等価回路/DRT）。
  - 質量分析: `MassCube/asari/XCMS`（feature 検出）。分子: DP4+ 相当の Boltzmann 平均＋Student-t（純 numpy 実装が容易）。
- **スコープ外（対話 GUI / MATLAB / 商用）** — caw は起動も規律付けもしない。**「ユーザーが専用ソフトで還元 → caw が
  post-export の下流解析＋妥当性検証＋執筆で協働」**という分担を明記する:
  - SHELX（対話精密化）・Olex2・CrysAlisPro・JANA、CasaXPS（XPS 定量）、EasySpin（EPR、MATLAB）、
    RELION/cryoSPARC/PHENIX/Coot（構造生物）、MaxQuant/Proteome Discoverer（一部 MS 一次処理）、SimaPro/openLCA、ASTRA（SEC）。

## 資産 3 — 高リスク解析の規律チェックリスト（モデル依存工程の誤帰属防止）

「数値が生まれる肝の工程」はモデル依存で**尤もらしい誤答**を生む。手法別スキルにせず、各 playbook に共通の
ガードレール節を持たせる。該当工程では必ず:

- **前提を正直に開示**（選んだモデル・固定したパラメータ・除外したデータ）。
- **代替モデル比較**（複数の妥当な仮定で結果が変わらないか）。
- **過剰フィット検知**（パラメータ数 vs データ点、残差構造、情報量規準 AIC/BIC）。
- **一意性チェック**（別初期値・別モデルで同じ解に収束するか）。

特に注意（監査で頻出）: **EIS 等価回路の選択**・**過渡吸収のターゲットモデル（誤ると偽 SAS）**・**EXAFS のパス数/配位数**・
**XPS の背景モデル（Shirley/Tougaard）**・**NMR/クロマトの重なりピーク分離**・**cryo-EM の particle picking**・
**多形/相同定の指数付け（大 cell で非識別的）**。これらは **caw が積分/帰属そのものを代替できないことも多い**ので、
その場合は「ユーザーが還元 → caw が妥当性検証で協働」と役割を明示する。

---

**要点**：3 資産はいずれも **汎用（手法非依存）**。取込は「変換レシピ」、専用ソフトは「orchestrate か外部委譲かを線引き」、
高リスク工程は「共通ガードレール」で扱う。per-technique スキル・固定パーサは作らない（caw の抽象フレームワークを保つ）。
