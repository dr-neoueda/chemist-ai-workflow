# 化学全領域カバレッジ監査 と caw の役割境界

> 実施: 2026-07-01。化学 16 サブ領域を並列エージェントでオープンアクセス論文に基づき監査
> （実験→生データ/装置→解析→計算のワークフローを抽出し、現行 caw v1.61.0 で対応可能かを判定）。

## 結論（正直に）

**「化学の全分野に本当に対応できる」とは言えない。** 実態は **「どの分野でも破綻せず、下流の定量解析と
組織運営は回る中立ハブ」**。監査した **16 領域すべてが `partial`**（covered 0・gap 0）で、これは構造的な帰結:

1. **器（9 部署）は全 16 領域に過不足なくマップ** — 部署割り当てにギャップは無い。
2. **raw → 数値化が済んだ後の下流解析は全領域で強い** — 汎用 Python＋規律がむしろ武器。
3. **各分野を"定義"する一次工程（ベンダーバイナリ取込＋専用ソフトでの raw 還元）を caw が起動・orchestrate・
   規律付けできない** — これが全 16 領域で共通して `partial` を生む唯一の原因。

## 領域依存性

- **深く噛む（解析が Python に収斂）**: 計算化学・物理化学（速度論/熱力学）・ケモインフォ/創薬・光物理の global 解析。
- **下流＋執筆＋playbook でしか関与できない（非 Python モノリスが工程を独占）**: 結晶学 SCXRD・cryo-EM・
  EXAFS・EPR・XPS 定量・LCA・地球化学平衡。

## caw の役割境界（設計上の正典）

caw は次の **3 つを担うハブ**であり、それ以外は外部連携に委ねる。**「全分野対応」とは謳わない。**

1. **全 16 領域の組織運営** — 9 部署（experiment 含む）でワークフローを回す。
2. **raw → 数値化後の下流定量解析＋規律** — 汎用ツール（pandas/scipy/lmfit/RDKit/ASE/pymatgen 等）で
   fit・回帰・統計・誤差開示・作図。使うほど playbook で分野特化。
3. **執筆・文献・playbook** — caw-write / caw-research / caw-register / caw-playbook。

**担わない（正直に明記）**: ベンダー GUI/MATLAB 専用ソフトでの**対話的 raw 還元**
（SCXRD 精密化 SHELX/Olex2・XPS 定量 CasaXPS・EPR シミュ EasySpin・cryo-EM 再構成 RELION 等）。
これらは caw のスコープ外で、**ユーザーが専用ソフトで還元 → caw が post-export の下流解析＋妥当性検証＋執筆で協働**する。

## 横断ギャップへの対処（手法別スキルを増やさない）

監査の共通ギャップは、抽象フレームワークの内側で **3 つの汎用資産** に集約して対処する
（詳細は [`plugin/skills/caw-analyze/references/analysis-conventions.md`](../plugin/skills/caw-analyze/references/analysis-conventions.md)）:

- **取込アダプタ規約** — ベンダーバイナリ → 中立形式の変換レシピ（OSS リーダ or native 実装）を playbook 蓄積。
- **外部専用ソフト orchestration 契約** — scriptable ソフト（GSAS-II scriptable・xraylarch・phreeqpython・
  pyglotaran・impedance.py 等）は caw-analyze が駆動し規律をラップ。GUI/MATLAB 専用は外部委譲と明示。
- **高リスク解析の規律チェックリスト** — モデル依存工程（EIS 回路選択・TA ターゲット・EXAFS パス数・XPS 背景 等）の
  誤帰属防止（前提開示・代替モデル比較・過剰フィット検知・一意性）。

さらに **caw-input を「幾何＋メソッド＋エンジン方言アダプタ」に分離**し、新エンジンは playbook にテンプレ 1 枚で
拡張できる構造にする（CREST/xtb・DP4+・PHREEQC・AutoDock Vina を標準レシピ化）。

## 期待値（ユーザーの過大期待を防ぐ）

| 領域タイプ | caw の関与度 |
|---|---|
| 解析が Python に収斂（計算化学・物理化学速度論/熱力学・ケモインフォ創薬・光物理 global） | **深い**（取込〜下流〜執筆） |
| 一次還元が非 Python モノリス独占（結晶学 SCXRD・cryo-EM・EXAFS・EPR・XPS 定量・LCA・地球化学平衡） | **限定**（下流＋妥当性検証＋執筆＋playbook） |
