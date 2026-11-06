# `office/AGENTS.md` 生成テンプレート

`/caw` のオンボーディング Step 3 で `office/AGENTS.md` を生成するためのテンプレート。`{{...}}` の変数はオンボーディングの回答で置換する。

---

## テンプレート本体

````markdown
# Company - 研究プロジェクト管理システム

> トラック: 研究

## オーナープロフィール

- **研究分野**: {{RESEARCH_FIELD}}
- **分野の群**: {{FIELD_GROUP}}
- **使う計算ソフト**: {{COMPUTATION_CATEGORIES}}
- **ナレッジベース**: {{KNOWLEDGE_BASE}}
- **クラウドストレージ**: {{CLOUD_STORAGE}}
- **作成日**: {{CREATED_DATE}}

## 組織構成

```
office/
├── AGENTS.md
└── secretary/
    ├── AGENTS.md
    ├── inbox/
    ├── todos/
    └── notes/
{{DEPARTMENT_TREE}}
```

## 部署一覧

| 部署 | フォルダ | 役割 |
|------|---------|------|
| 秘書室 | secretary | 窓口・相談役。TODO 管理、壁打ち、メモ、意思決定ログ。常設。 |
{{DEPARTMENT_TABLE_ROWS}}

## 運営ルール

### 成果物配置の二層原則（CRITICAL）

このプロジェクトのディレクトリは **明確に二層** に分かれる。

**第 1 層：`office/` 配下 — 運営情報のみ**

- 秘書の TODO / 意思決定 / 学び / Inbox
- 各部署の AGENTS.md（運営ルール）
- 計算 Playbook と job 記録
- 内部品質ゲート記録（コードレビュー、validation）
- 中間メタデータ（Notion 同期状況、DOI 取得ログなど）

`office/` は**先頭ドットを付けない可視フォルダ**で、macOS Finder / Windows Explorer のどちらでも見える。「AI 部署の運営情報専用エリア」という位置づけで、成果物とは混在させない。**caw はユーザーのプロジェクトに先頭ドット始まりの不可視フォルダを作らない（絶対）。**

**第 2 層：プロジェクトルート直下 — 成果物そのもの**

ユーザーが ファイラーで開いて中身を確認するファイルは **必ず `work/` 配下** に置く：

| ディレクトリ | 中身 |
|---|---|
| `work/papers/` | `pdf/`＝原本 PDF ／ `md/`＝文献要約 |
| `work/topics/` | 調査トピックまとめ |
| `work/manuscripts/` | 論文ドラフト（.tex / .docx） |
| `slides/` | 発表資料（.pptx）と生成スクリプト |
| `work/analyses/` | 解析結果 |
| `work/notebooks/` | Jupyter Notebook |
| `work/figures/` | 解析・論文・スライド用の図表 |
| `work/scripts/` | 単発スクリプト |
| `work/tools/` | 再利用ツール |
| `work/reports/` | 報告書 |
| `work/<ツール名>/`（例：`work/gaussian/`・`work/openfoam/`） | 計算ソフトの入出力 |
| `work/experiments/` | 実験記録 |

❌ AI 生成成果物（要約 md、スライド、グラフ等）を `office/<dept>/` に置かない
✅ 部署運営ノートのみ `office/<dept>/` に置く

### 秘書が窓口

- ユーザーとの対話は常に秘書が担当する
- 秘書は丁寧だが親しみやすい口調で話す
- 壁打ち、相談、雑談、何でも受け付ける
- 部署の作業が必要な場合、秘書が直接該当部署のフォルダ（運営情報）または `work/` 配下 の成果物ディレクトリに書き込む

### 自動記録

- 意思決定、学び、アイデアは言われなくても記録する
- 意思決定 → `secretary/notes/YYYY-MM-DD-decisions.md`
- 学び → `secretary/notes/YYYY-MM-DD-learnings.md`
- アイデア → `secretary/inbox/YYYY-MM-DD.md`
- 計算ノウハウ（罠と処方）→ `computation/playbooks/<tool>.md`（computation 部署がある場合）

### 同日 1 ファイル

同じ日付のファイルがすでに存在する場合は追記する。新規作成しない。

### 日付チェック

ファイル操作の前に必ず今日の日付を確認する。

### ファイル命名規則

- 日次ファイル: `YYYY-MM-DD.md`
- トピックファイル: `kebab-case-title.md`
- 計算ジョブ記録: `YYYY-MM-DD-<system>-<purpose>.md`

### TODO 形式

```markdown
- [ ] タスク内容 | 優先度: 高/通常/低 | 期限: YYYY-MM-DD
- [x] 完了タスク | 完了: YYYY-MM-DD
```

### コンテンツルール

1. 迷ったら `secretary/inbox/` に入れる
2. 既存ファイルは上書きしない（追記のみ）
3. 追記時はタイムスタンプを付ける

## 研究分野の規律

{{FIELD_RULES}}

## パーソナライズメモ

{{PERSONALIZATION_NOTES}}
````

---

## 変数リファレンス

| 変数 | ソース | 説明 |
|------|--------|------|
| `{{RESEARCH_FIELD}}` | Q1〜Q2 | 研究分野（有機化学・凝縮系物理・構造生物学・機械工学 等） |
| `{{FIELD_GROUP}}` | Q1 | 分野の群（化学・材料 / 物理・地球惑星 / 生命科学 / 工学・情報 / 共通） |
| `{{FIELD_RULES}}` | Q1 | `field-rules.md` から群ごとに選ばれる規律（scaffold が差し込む） |
| `{{COMPUTATION_CATEGORIES}}` | Q4 | 計算ソフト（量子化学・MD・FEM・数値計算 等、複数可） |
| `{{KNOWLEDGE_BASE}}` | Q3 | ナレッジベース（Notion, Obsidian, Logseq 等） |
| `{{CLOUD_STORAGE}}` | Q4 | クラウドストレージ（Google Drive, Dropbox 等） |
| `{{CREATED_DATE}}` | 自動 | 組織構築日（YYYY-MM-DD） |
| `{{DEPARTMENT_TREE}}` | 全部署（固定） | 研究トラック全 9 部署のディレクトリツリー（インデント済） |
| `{{DEPARTMENT_TABLE_ROWS}}` | 全部署（固定） | 研究トラック全 9 部署のテーブル行 |
| `{{PERSONALIZATION_NOTES}}` | Q1〜Q4 から派生 | 研究分野と使用ツールに応じた運用ヒント |

---

## 部署 → ツリー / テーブル マッピング

全 9 部署を `{{DEPARTMENT_TREE}}` と `{{DEPARTMENT_TABLE_ROWS}}` に反映するための対応表（研究トラックは全部署を常に作成）：

| 部署 ID | ツリー行 | テーブル行 |
|---|---|---|
| research | `├── research/` | `\| 文献部 \| research \| 文献検索、要約、ナレッジ DB 化 \|` |
| engineering | `├── engineering/` | `\| 開発部 \| engineering \| Python ツール、計算入力ジェネレータ、CLI \|` |
| computation | `├── computation/` | `\| 計算管理部 \| computation \| 計算ジョブの管理（量子化学・MD・FEM・数値計算 等）+ Playbook \|` |
| experiment | `├── experiment/` | `\| 実験部 \| experiment \| 実験の段取り・電子ノート・試料/試薬の在庫・安全 \|` |
| analysis | `├── analysis/` | `\| データ解析部 \| analysis \| 手法非依存の解析コンパニオン（fit・定量・可視化） \|` |
| writing | `├── writing/` | `\| 論文執筆部 \| writing \| LaTeX / Word 原稿、図表、参考文献 \|` |
| review | `├── review/` | `\| レビュー部 \| review \| コード品質、計算妥当性の確認 \|` |
| presentation | `└── presentation/` | `\| プレゼン部 \| presentation \| スライド生成（SVG-first → native pptx） \|` |

最後の部署のツリー行は `└──` を使う（順序：research → engineering → computation → experiment → analysis → writing → review → presentation）。

---

## パーソナライズメモ生成ガイド

`{{PERSONALIZATION_NOTES}}` には、Q1〜Q4 の組み合わせから派生する運用上の助言を入れる。分野ごとの決まりごと（単位・命名・誤差）は `{{FIELD_RULES}}` が担うので、ここには**その人の研究に固有のこと**だけを書く。

### 例: 研究分野 = 有機化学 + 計算カテゴリ = 量子化学

```
- 有機化学 + 量子化学計算（Gaussian/ORCA 等）の組み合わせ。反応機構解析、TS 探索、遷移状態最適化などのワークフローを想定
- computation 部署の playbook（gaussian.md 等）に「DFT 汎関数選択」「収束対策」「IRC 解析」のノウハウを蓄積していく
- 計算結果の解析・可視化は analysis 部署を併用すると良い
```

### 例: 研究分野 = 結晶化学 + 計算カテゴリ = 周期系 DFT

```
- 結晶化学 + 周期系 DFT（CP2K/VASP 等）の組み合わせ。結晶構造最適化、相転移解析、band structure などのワークフローを想定
- 実験データ（XRD パターン等）との突き合わせは analysis 部署を併用
- 結晶相反応の MD 検証は古典 MD 部署と組み合わせるケースもある
```

### 例: 研究分野 = 物理化学 + 計算ソフトは使わない / 主に実験中心

```
- 物理化学 + 実験中心の構成。NMR / IR / UV-Vis / 蛍光分光など測定データの管理と解析を想定
- engineering 部署で測定データ処理スクリプトを蓄積、analysis 部署で可視化・統計
- computation 部署は不要だが、後から DFT 計算を始める場合に追加できる
```

### 例: 研究分野 = 凝縮系物理 + 計算ソフトは使わない / 主に実験中心

```
- 凝縮系物理 + 実験中心の構成。輸送測定・磁化・比熱など温度・磁場を掃引する測定の管理と解析を想定
- 掃引の条件（温度・磁場・掃引速度）を測定ファイル名かメタデータに残し、analysis 部署で fit・相図化
- 理論曲線との比較は engineering 部署で数値計算スクリプトとして蓄積する
```

### 例: 研究分野 = 構造生物学 + 計算カテゴリ = 構造予測・MD

```
- 構造生物学 + 構造予測（AlphaFold 等）と MD（GROMACS 等）の組み合わせ。予測構造の評価・変異体の比較・動的挙動の解析を想定
- 予測の信頼度（pLDDT・PAE）と実験構造（PDB）の突き合わせは analysis 部署を併用
- 配列・構造の ID（UniProt・PDB）を文献部の要約とジョブ記録の両方に残す
```

### 例: 研究分野 = 機械工学（流体） + 計算カテゴリ = CFD

```
- 機械工学 + CFD（OpenFOAM 等）の組み合わせ。形状・境界条件を変えた比較計算と、実験（PIV・圧力測定）との突き合わせを想定
- computation 部署の playbook（openfoam.md 等）にメッシュの作り方・乱流モデルの選択・収束の判定を蓄積していく
- 設計値・計算値・実測値は analysis 部署で同じ図に重ねるとき凡例で区別する
```
