---
name: caw
description: >
  研究プロジェクト（化学者向け）と就活の 2 トラックに対応した AI 部署システム。
  `/caw` で起動し、秘書部から開始。研究なら研究分野・計算ソフト・ナレッジベース等を、
  就活なら区分・志望業界・就活フェーズをヒアリングして、用途に合わせた部署 CLAUDE.md を一括スキャフォールドする。
trigger: /caw
---

# Chemist's AI Workflow（caw）

## いつ使うか

- `/caw` を実行したとき
- 化学プロジェクトのディレクトリで「秘書」「TODO」「研究」「文献」「計算」「論文」「申請書」「スライド」などと言われたとき
- **就活で**「自己分析」「企業研究」「ES」「エントリーシート」「志望動機」「ガクチカ」「面接対策」などと言われたとき
- `office/` がカレントディレクトリに存在し、Claude が運営モードに入るべきと判断したとき

---

## ワークフロー

### Step 1: 検出とモード判定

カレントディレクトリに `office/` が存在するか確認する。

- **`office/` が存在する** → `office/CLAUDE.md` を読み込み → **運営モード**へ
- **`office/` が存在しない** → **Step 2: オンボーディング**へ

### Step 2: オンボーディング

`AskUserQuestion` で対話的にヒアリングする。秘書の口調（丁寧だが親しみやすい）で話す。ユーザーの言語を自動検出し、同じ言語で応答する。

#### Call T: トラック選択（1 問、最初に聞く）

caw は **研究** と **就活** の 2 トラックがある。最初にどちらかを聞く。

```
QT (トラック): 「caw を主に何に使いますか？」
  - 研究プロジェクト（実験・計算・論文・申請書）
  - 就活（自己分析・企業研究・ES・面接）
  (multiSelect: false; Other 可)
```

- **就活** を選んだら → **`references/job-hunting-departments.md` を読み、その §A〜§E に従って**就活モードのオンボーディング・scaffold・運営モードを実行する（以降の研究向け Call 1〜6 は使わない）。**就活トラックでは常にはじめてモード（平易な日本語・用語説明）で進める**（office 設定に `> 運用モード: はじめて` を必ず書く）。
- **研究プロジェクト** を選んだら → そのまま下記の研究向けフローへ。

**（以下は研究トラックのオンボーディング）研究分野を「広い分類 → 中分類」と funnel で絞り、論文があれば環境理解のために浅く読み、最後に計算ツールと標準化項目を聞く。全設問は選択式（各設問に Other＝自由入力を必ず添える）。部署は常に全 9 部署で固定。`AskUserQuestion` を順に呼ぶ（分野の中分類は大分類の回答に依存するため逐次）。** 設計の根拠は `docs/analysis-companion-design.md`。

> **実験手法・装置は onboarding で聞かない**：標準化が難しくユーザーごとの特色が強いため。実験データを実際に解析するとき、解析コンパニオン（`caw-analyze`）が **per-data で具体的に**尋ねる。**計算＝事前に聞いて環境化（Playbook）／実験＝使用時に per-data** の非対称を貫く。

#### Call 1: 研究分野・大分類（最も広い・1 問）

```
Q1 (分野・大): 「研究分野は、大きくはどれに当たりますか？」
  - 化学
  - 物理・物性
  - 材料・デバイス
  - 生命科学・生化学
  - 計算・データ科学
  - 環境・エネルギー
  (multiSelect: false; Other で自由入力可)
```

#### Call 2: 研究分野・中分類（Q1 に適応・1 問）

Q1 の回答に応じて中分類の選択肢を出す（下表。複数領域・該当なしは Other 自由入力で拾う）。ここまでで**領域**が定まる ── 手法・ツール名はまだ出さない。

| Q1 大分類 | 中分類の選択肢（例・各 ＋Other） |
|---|---|
| 化学 | 有機化学 / 無機・錯体化学 / 物理化学・分光 / 分析化学 / 高分子・超分子 / 結晶・構造化学 / ケミカルバイオロジー |
| 物理・物性 | 凝縮系 / 表面・界面 / 光物性 / 磁性・スピン / ソフトマター |
| 材料・デバイス | 電池・エネルギー材料 / 半導体・電子材料 / 触媒 / 高分子材料 / ナノ材料 |
| 生命科学・生化学 | 構造生物学 / 生化学・酵素 / ケミカルバイオロジー / 創薬 / オミクス |
| 計算・データ科学 | 量子化学・理論 / 分子シミュレーション / マテリアルズインフォマティクス / ケモインフォマティクス |
| 環境・エネルギー | 触媒・グリーンケミストリー / エネルギー変換・貯蔵 / 環境分析 |

#### Call 3: 論文添付（任意・環境理解のためだけに浅く読む）

「あなたの論文や、同領域の代表的な論文があれば、研究の輪郭を掴むために見せてください（任意）。**PDF はプロジェクト直下の `inbox/` に置く**か、短い要旨・本文なら**チャットに貼り付け**でも構いません。無ければスキップします。」

- 渡されたら **環境構築に必要な情報だけを浅く抽出**する：研究分野の補強・主な活動（合成 / 測定 / 計算 / 解析）・**使用している計算ツール/手法**・対象系。
- **やらないこと**：文体（voice）プロファイル・用語辞書（glossary）・key-findings/citations の精密抽出（**環境構築に無関係で重い**。必要になったとき `caw-write` / `caw-intake` で行う）。
- 本人論文＝「自分が実際にしていること」、同領域論文＝「領域の文脈」として**区別**して扱う。
- 抽出した研究理解は **ユーザーに反映して確認してから** プロファイルに確定する（黙って決めつけない）。
- 論文が無ければ次の Call 4 の選択で補う。

#### Call 4: 計算ツール／アプリ（複数選択・use＋train）

「研究で使う計算ツール・アプリを教えてください（複数可）。Call 3 の論文で見えたものはここで**確認・補完**します。」

```
Q (計算ツール):
  - Gaussian / ORCA / Psi4（量子化学）
  - GROMACS / AMBER / LAMMPS / OpenMM（古典 MD）
  - CP2K / VASP / Quantum ESPRESSO（周期系 DFT）
  - xtb・CREST（半経験的・配座探索）
  - MLIP・MLFF（MACE / CHGNet / NequIP 等：ポテンシャルの **利用＋訓練/fine-tune** 両方）
  - ChimeraX（構造可視化・密度フィット）
  - 計算は使わない / 主に実験中心
  (multiSelect: true; Other で具体的なソフト名を自由入力。選択肢が 4 を超えるので代表＋Other で拾う)
```

- **ディレクトリ・Playbook は、ここ（＋Call 3 の論文）で名指しされたツールについてのみ作る**。MLIP を挙げたら `work/mlip/`（**利用も訓練/fine-tune も**扱う）。
- 「計算は使わない / 主に実験中心」を選んだら計算ディレクトリは作らず、実験記録用 `work/experiments/` の要否を `AskUserQuestion` で 1 問だけ確認（既定 Yes）。

#### Call 5: 標準化項目（環境に直結・1 回で 4 問）

有限の共通選択肢が**具体的な環境成果物に一意対応**する項目。1 回の `AskUserQuestion` で 4 問まとめて聞く。

```
Q (計算実行環境): 「計算ジョブをどこで回しますか？」
  - HPC（SLURM）/ HPC（PBS・その他）/ ローカルのみ / クラウド（AWS・GCP 等）
  (multiSelect: true; Other 可 → computation 部署に submission 既定〔queue/walltime/module〕を反映)

Q (文献管理・ナレッジベース): 「文献・ノート管理は？」
  - Notion / Obsidian / Zotero・Mendeley / Logseq / 使わない
  (multiSelect: false; Other 可 → caw-register の格納先・連携)

Q (クラウドストレージ): 「PDF・データの保管は？」
  - Google Drive / Dropbox / OneDrive / ローカルのみ
  (multiSelect: false; Other 可 → 成果物の同期先)

Q (研究体制): 「研究の進め方は？」
  - 単独（指導教員の添削のみ）/ 共著で分担 / 研究室で office/ 共有
  (multiSelect: false → writing / review 部署の運用ルールに反映)
```

#### Call 6: 執筆・申請（1 回で 2 問）

```
Q (申請書の予定): 学振（DC/PD）/ 科研費 / 民間財団・その他 / 予定なし
  (multiSelect: true; 該当あれば writing 部署に申請書トラッカー雛形を追加提案)

Q (論文ステータス): 執筆中 / 投稿済み・査読対応中 / これから / 当面なし
  (multiSelect: false → writing 部署の初期テンプレに反映)
```

Call 1〜6 の回答（と Call 3 の論文から浅く抽出した研究理解）は、後段の scaffold で各部署 CLAUDE.md と **`work/profile/`（研究分野・活動・使用計算ツール・対象系）** に保存し、各部署・`caw-analyze` が文脈として参照できるようにする。実験系の具体は据え置き（解析時に追記）。

> **部署の選択質問は廃止**：部署は常に全 9 部署を作成するため、「どの部署を作るか」は尋ねない。

### Step 3: 自動スキャフォールド

ヒアリング結果に基づいて、以下を一括生成する。

**scaffold 範囲（全ユーザー共通：化学者モードは常に全 9 部署）**：
- `office/` + ルート CLAUDE.md + **全 9 部署**（secretary / research / engineering / computation / experiment / analysis / writing / review / presentation）+ 作業ディレクトリ
- Call 1〜4（分野 大→中・論文から抽出した研究理解・計算ツール）を各部署 CLAUDE.md と `work/profile/` に反映
- Call 5〜6（計算実行環境・文献管理・クラウド・体制・申請書・論文ステータス）を `office/CLAUDE.md` のパーソナライズメモと各部署 CLAUDE.md に反映 + 申請書予定があれば writing 部署に申請書トラッカー雛形を追加

#### 3-1. ルート `office/` とルート CLAUDE.md

1. `office/` ディレクトリを作成
2. `references/claude-md-template.md` を読み込み、以下のプレースホルダを置換して `office/CLAUDE.md` を生成：
   - `{{RESEARCH_FIELD}}` ← Call 1〜2（分野 大→中）＋ Call 3 論文から補強
   - `{{COMPUTATION_CATEGORIES}}` ← Call 4（計算ツール）
   - `{{KNOWLEDGE_BASE}}` ← Call 5（文献管理・ナレッジベース）
   - `{{CLOUD_STORAGE}}` ← Call 5（クラウドストレージ）
   - `{{CREATED_DATE}}` ← 今日の日付
   - `{{DEPARTMENT_TABLE_ROWS}}` ← 全 9 部署のテーブル行
   - `{{DEPARTMENT_TREE}}` ← 全 9 部署を含むツリー図

#### 3-2. 秘書部（必須）

`references/chemistry-departments.md` の「secretary」セクションから：

1. `office/secretary/{inbox,todos,notes}` を作成
2. `office/secretary/CLAUDE.md` を配置（化学研究向けにカスタマイズされた秘書ロール）
3. `office/secretary/todos/YYYY-MM-DD.md` を今日の日付で作成（テンプレ付き）

#### 3-3. 化学者向け部署（全 9 部署を一括作成）

化学者モードの全部署（research / engineering / computation / experiment / analysis / writing / review / presentation。secretary は 3-2 で作成済み）について、`references/chemistry-departments.md` の各セクションから：

1. 部署ディレクトリとサブフォルダを作成
2. `<dept>/CLAUDE.md` を配置（部署固有の役割・運用ルール・参照ファイル）

**Call 4（＋Call 3 論文）で計算ツールが名指しされていた場合**（computation 部署は常に作成済み）：

- `computation/playbooks/` 配下に該当ソフトの Playbook 雛形を配置
- `references/playbook-starters.md` に該当セクション（gaussian / gromacs / cp2k / orca / vasp 等）があれば取り出して配置。**無いソフト**（amber / namd / lammps / openmm / psi4 等）は frontmatter（`tool`・`last_updated`）＋空の `## Lessons Learned` だけの最小 Playbook を作る（以後 caw-playbook が追記してスペシャリスト化）

#### 3-4. `work/` 配下の作業ディレクトリ（実研究ファイル用）

`office/` は AI 部署システムの管理側。実際の研究データを置く作業ディレクトリは、プロジェクト直下に **`work/` ディレクトリを 1 つ作り、その配下にまとめて生成**する（ルート直下に多数のフォルダを散らかさない）。各ディレクトリには `README.md` を 1 枚配置して「何を置くか・関連する `office/` 部署」を明示する。

**Call 4（＋Call 3 論文）でユーザーが名指しした各ツールについてのみ、`work/` 配下にディレクトリ作成**（一覧の全ソフトは作らない）：

| 計算ソフト | 作業ディレクトリ | README で示す中身 |
|---|---|---|
| Gaussian | `work/gaussian/` | `.gjf` 入力、`.log`/`.chk`/`.fchk` 出力、`run_*.sh` ジョブスクリプト |
| GROMACS | `work/gromacs/` | `.gro`/`.top`/`.itp`/`.mdp`/`.ndx`/`.tpr`/`.xtc`/`.edr` |
| CP2K | `work/cp2k/` | `.inp` 入力、`.out`/`.restart`/`.ener`/`.pos` 出力 |
| ORCA | `work/orca/` | `.inp` 入力、`.out`/`.gbw` 出力 |
| VASP | `work/vasp/` | `INCAR`/`POSCAR`/`KPOINTS`/`POTCAR`、`OUTCAR`/`CHGCAR`/`WAVECAR`/`vasprun.xml` |
| Quantum ESPRESSO | `work/quantum-espresso/` | `.in` 入力、`.out` 出力、`*.UPF` 擬ポテンシャル |
| MACE / MLIP | `work/mlip/` | 学習データ、`.model` チェックポイント、評価 trajectory |
| ChimeraX | `work/chimerax/` | `.cxc`/`.py` スクリプト、PDB/mmCIF 構造、`.mrc`/`.map`/`.ccp4` 密度マップ、`.cxs` セッション、フィット結果・レンダ画像 |
| Psi4 | `work/psi4/` | `.dat`/`.in` 入力、`.out` 出力、`.fchk`/`.molden` |
| AMBER | `work/amber/` | `.prmtop`/`.inpcrd`/`.mdin` 入力、`.mdout`/`.nc`(traj)/`.rst` 出力 |
| NAMD | `work/namd/` | `.conf`/`.namd` 入力、`.psf`/`.pdb`、`.dcd`(traj)、`.log` |
| LAMMPS | `work/lammps/` | `in.*` 入力、`data.*`、`.dump`/`.lammpstrj`(traj)、`log.lammps` |
| OpenMM | `work/openmm/` | Python(`.py`) スクリプト、`.pdb`/`.xml`(System/State)、`.dcd`(traj) |

各 README には対応する Playbook へのリンク（`../office/computation/playbooks/<tool>.md`）を必ず含める。**上表に無いソフトをユーザーが挙げた場合**は `work/<ソフト名 lowercase-kebab>/` を作り、README に主な入出力拡張子を 1 行で記す（同じく `inbox/`・`_past-data/` を付ける）。

**初心者向けの投入フォルダ（各計算ソフトディレクトリ配下に必ず作る）**：パソコン操作に不慣れでも迷わないよう、各計算ソフトディレクトリ（`work/gaussian/` 等）に次の 2 つのサブフォルダと README を作成する：

- `inbox/` — これから計算したい構造ファイルや下書き入力を一時的に置く場所。「`work/gaussian/inbox/` の構造で最適化入力を作って」のように指示できる
- `_past-data/` — 過去に自分が回した入力・出力（`.gjf`/`.log`/`.inp`/`.out` 等）を入れる場所。ここにデータを入れて「過去データを取り込んで」と言うと、caw が中身を解析し、その人の汎関数・基底・収束設定などの傾向を該当 Playbook の `## Lessons Learned` に初期 seed する（[caw-playbook] の「過去データ一括取り込み」と連携）。以後の入力生成がその人向けに最適化される

各サブフォルダの README は「ここに何を入れる → 何が起きる」を 1〜2 行の平易な日本語で書く（専門用語を避け、具体例を 1 つ添える）。

**全部署のドメイン作業ディレクトリ（成果物置き場）を必ず `work/` 配下 に作成**：

| 部署 | 作業ディレクトリ | README で示す中身 |
|---|---|---|
| research | `work/papers/` | `pdf/`＝原本 PDF ／ `md/`＝文献要約（`<author-year>.md`） |
| research | `work/topics/` | 調査トピック・文献リスト（caw-research の HTML、`<topic>.html`） |
| writing | `work/manuscripts/` | 論文・申請書ドラフト（`caw-write`、md / LaTeX / Word）、図表、参考文献 |
| presentation | `work/presentations/slides/` | 発表資料・論文紹介スライド（`.pptx`）。SVG ソースは同下の `_src/<deck>/`（再生成用） |
| presentation | `work/presentations/figures/` | **スライドに使う画像をユーザーが置く inbox**（顕微鏡写真・装置スクショ・外部プロット・スキャンした手描き図 等）。`caw-slides` がここの画像を拾って埋め込み、質の高いスライドにする |
| analysis | `work/analyses/` | 解析結果（1 トピック 1 サブフォルダ） |
| analysis | `work/notebooks/` | Jupyter Notebook |
| analysis | `work/figures/` | 解析・論文・スライド用の図表（presentation と共有） |
| engineering | `work/scripts/` | 単発・一時スクリプト |
| engineering | `work/tools/` | 再利用される本格的なツール |

**重要**：成果物は **必ず `work/` 配下**。`office/research/papers/` のようなパスは禁止。`office/<dept>/` 配下には部署の運営ノート（CLAUDE.md、計画メモ、内部レビュー記録など、ユーザーが日常的に ファイラーで開かないもの）のみ置く。

review 部署は内部品質ゲート記録のみ扱うため、`work/` 配下 ディレクトリは作らず `office/review/{code-reviews,validation}/` のみで運用する。

**research（work/papers/）にも投入フォルダ**：research を選択した場合、`work/papers/pdf/`（PDF 置き場）と `work/papers/md/`（書誌付き要約）を作成し、README に「論文 PDF を `work/papers/pdf/` に入れて『登録して』と言うと、`/caw-register` が書誌情報を抽出して `work/papers/md/<著者-年>.md` に整理し、ナレッジベース／クラウドストレージにも登録する」と平易に明記する。初心者が「PDF をどこに置けばいいか」で迷わないようにするのが目的。

**presentation（work/presentations/figures/）＝スライド用画像の投入フォルダ**：`work/presentations/figures/` を作成し、README に「**スライドに載せたい画像（顕微鏡写真・装置スクショ・外部で作ったプロット・スキャンした手描き図・ロゴ 等）をここに入れておくと、『スライド作って』と言ったときに `caw-slides` が候補として拾い、アスペクト比を保って埋め込みます**。ファイル名は内容が分かる名前に（例 `xrd_120C.png`）。PNG / JPEG / SVG が使えます」と平易に明記する。ユーザーが自分の実データ画像で質の高いスライドを作れるようにするのが目的。

**統合 inbox（迷ったらここ）**：プロジェクト直下に `inbox/` を作成し、README に「**種類を問わず何でもここに入れて『処理して』と言えば、`caw-intake` が中身を見て判定し適切に処理します**——自分の論文/スライド/CV→プロファイル・文体を抽出（`work/profile/`・`work/manuscripts/_style/`）、外部論文→登録（`work/papers/`）、計算入出力→Playbook 取り込み。**処理が済んだ原本は種類ごとに `work/…/_source/`（過去 ES→`work/documents/_source/` 等）へ移動し、inbox は空になる**ので原本も後から探しやすい。どこに入れるか迷ったらここで OK」と明記する。`work/papers/pdf/`（外部論文の直接登録）や各計算ソフトの `_past-data/` は、置き場が分かっている人向けの直接ルート。

**Call 4 で「計算は使わない / 主に実験中心」を選択していた場合**は、計算ソフト用ディレクトリは作成しない。実験記録用に `work/experiments/` を作るかどうか、その場で `AskUserQuestion` で 1 問追加して確認する（デフォルト Yes）。

#### 3-5. MCP セットアップ手順の生成

Call 5（文献管理・ナレッジベース / クラウドストレージ）の回答に応じて、`office/.mcp-setup.md` を生成する。

1. `references/mcp-setup-templates.md` を読み込む
2. 共通ヘッダを `office/.mcp-setup.md` に書き出す
3. 文献管理の回答に該当するナレッジベース MCP セクション（Notion / Obsidian / Zotero・Mendeley / Logseq / 未設定）を追記
4. クラウドストレージの回答に該当する MCP セクション（Google Drive / Dropbox / OneDrive / 未設定）を追記
5. 「使わない / 未定」を選んだ項目も、未設定セクションを入れておく（後から再生成しやすい）

**重要**：`office/.mcp-setup.md` は **手順書**であり、API key そのものは絶対に書かない（環境変数経由で渡す手順のみ記載）。

#### 3-6. 完了メッセージ

```
セットアップが完了しました！

プロジェクトルート/
├── office/                      ← AI 部署システム（管理側・可視フォルダ。基本触らなくて OK）
│   ├── CLAUDE.md
│   ├── secretary/               ← 窓口：TODO・意思決定・学び（CLAUDE.md / inbox/ / notes/）
│   │   └── todos/{{TODAY}}.md
│   └── research/ engineering/ computation/ experiment/ analysis/ writing/ review/ presentation/
│                                ← 全 9 部署を常に作成（各 CLAUDE.md＋運営情報のみ）
│
├── inbox/                       ← 統合 inbox：何でもここに入れて「処理して」
│   └── README.md
│
└── work/                        ← 成果物・作業ファイルはすべてこの中（使う分だけ増える）
    ├── papers/                  ← pdf/ に PDF を入れて「登録して」→ md/ に書誌付き要約
    ├── topics/ manuscripts/ analyses/ notebooks/ figures/
    ├── presentations/slides/    ← 発表資料（.pptx）
    ├── scripts/ tools/
    └── gaussian/ gromacs/ …     ← 計算ソフト選択時（各 inbox/・_past-data/ 付き）

これからは /caw でいつでも秘書に話しかけられます。
「今日の TODO を整理して」「論文を登録して」「計算の入力ファイル作って」など、
化学研究のあらゆる場面で使ってください。

💡 ヒント:
- 部署を追加したくなったら「<部署名> を作って」と言うだけで OK
- computation 部署があれば、各 Playbook に新しい知見を追記していけます
- 過去データがあれば `work/gaussian/_past-data/` 等に入れて「過去データを取り込んで」と言うと、
  あなた用に Playbook を最適化します
- **成果物（要約 md、スライド、グラフ等）は `work/` 配下**に保存されます。
  ファイラーから普通に開けます。`office/` は AI の運営情報専用です
- いま、選ばれた計算ツールの**初期 Playbook を裏で用意しています**（信頼できる資料から。
  出来上がったらお知らせします）。待たずにそのまま作業を始めて大丈夫です

🔧 前提ツールの確認:
- caw が使う外部ツール（Python・python-pptx・poppler・解析ライブラリ 等）を、
  **なぜ必要かを説明しながら 1 つずつ確認**します（不足分だけ・使うものだけ入れます）
```

#### 3-6b. 前提ツールの per-tool 確認（オンボーディングの一部・必ず実行）

scaffold 完了後、**`caw-setup` SKILL の Step 2〜4 を per-tool モードで実行する**。`caw-setup` 表の各ツールについて、**不足していて・ユーザーの機能に関わるものを 1 つずつ、「なぜ必要か」を添えて導入するか尋ねる**（`AskUserQuestion` を機能グループごとに使い、各ツールの説明欄に「なぜ必要か」を書く）。既に入っているものは尋ねない。選ばれたものだけを導入し、結果を報告する。**「あとで /caw-setup」の後回しにせず、初期構築の一部として必ず行う**。

#### 3-7. 計算ツール Playbook の web 種まき（バックグラウンド・自動）

完了メッセージを表示した**後**、Call 4（＋Call 3 論文）で名指しされた計算ツールについて、**信頼性の高いソースから初期 Playbook を種まき**する。手順・成果物の書式・規律・非目標はすべて **`references/playbook-web-seeding.md` に従う**（ここでは起動方法のみ規定）。

- **`references/playbook-web-seeding.md` を読み込む**。
- 名指しされたツール**1 つにつき 1 サブエージェント**を、`Task` ツールで **`run_in_background: true`（並列・非ブロッキング）** で起動する。各サブエージェントには「対象ツール名＋ユーザーの研究分野（Call 1〜2）」を渡し、`WebSearch` で一次資料・公式ドキュメントを調べさせ、`office/computation/playbooks/<tool>.md` の **`## 外部リファレンス（web 由来・要検証）`** セクションに追記させる（`## Lessons Learned` には触れない）。
- **funnel は待たせない**：オンボーディングの応答フローはここで完了扱いにし、種まきは裏で進める。全サブエージェント完了後に **1 回だけ**「N ツールの初期 Playbook を各 `## 外部リファレンス（web 由来・要検証）` に置きました（web 由来・要検証。実際に回した知見は Lessons Learned に書けば上書きされます）」と通知する。
- 「計算は使わない / 主に実験中心」を選んでいた場合は**この種まきをスキップ**する。

> **後日の再利用**：ユーザーが後からツールを 1 個足したときは、同じ `references/playbook-web-seeding.md` を読んでそのツール 1 つだけに種まきしてよい（オンボーディング時の自動配線はしない）。

---

## 運営モード

`office/` が存在する場合に自動で切り替わる。まず `office/CLAUDE.md` を読み込んで全体ルールを把握する。
**冒頭に `> 運用モード: はじめて` の行があれば、以下「はじめてモードの挙動」を全応答に適用する。**

### はじめてモードの挙動（強めに誘導）

パソコン・ターミナル・AI が初めての人を想定し、最初は強めに手を引く。`office/CLAUDE.md` に
`> 運用モード: はじめて` がある間、常に次を守る（慣れてきて「もう普通でいい」と言われたらこの行を外す）：

- **平易な日本語**。専門用語（ターミナル / IDE / パス / コミット 等）は初出で必ず 1 行説明を添える
- **毎回「次はこれをしましょう」を 1 つ提示**して締める（選択肢を 1〜3 個に絞る。多すぎる選択を出さない）
- **ターミナルで打つコマンドは「これをコピーして貼り付け → Enter」と明示**し、コマンドは 1 つずつ
- **元に戻せない操作（削除・上書き・送信・push 等）は必ず事前確認**。「失敗しても大丈夫」と安心させる
- **やったことと結果を 1 行で報告**（どのフォルダに何ができたか）。専門的なログは折りたたみ／省略
- 「わからない」「困った」と言われたら、まず**今いる状態と次の 1 手**を示す。必要なら `/caw-doctor`・`/caw-setup` を案内
- ユーザーが「〇〇って何?」と聞いたら、その用語を**たとえを使って 2〜3 行**で説明してから本筋に戻る

### 基本フロー

**秘書が窓口。ユーザーは部署を意識しなくていい。**

1. ユーザーが何かを言う
2. 秘書が内容を判断：
   - **秘書で完結するもの** → 秘書が直接対応
   - **部署が必要なもの** → 該当部署のフォルダに直接書き込む

### 秘書が直接対応するもの

| パターン | 対応 |
|---|---|
| TODO・タスク関連 | `secretary/todos/` の今日のファイルに追記・表示 |
| 壁打ち・相談・ブレスト | 対話で深掘りし、結論を `secretary/notes/` に保存 |
| メモ・クイックキャプチャ | `secretary/inbox/` にタイムスタンプ付きで記録 |
| 雑談・挨拶 | 親しみやすく応答 |
| 意思決定の記録 | `secretary/notes/YYYY-MM-DD-decisions.md` に追記 |
| 学び・気づき | `secretary/notes/YYYY-MM-DD-learnings.md` に追記 |

### 化学研究タスクの部署振り分け

| 文脈・キーワード | 振り分け先 |
|---|---|
| 論文の検索・文献調査（探す/集める） | research（caw-research） |
| 論文 PDF の登録・要約・書誌・引用整理 | research（caw-register） |
| Python スクリプト作成、CLI 化、解析ツール | engineering |
| Gaussian / GROMACS / CP2K / ORCA / VASP / ChimeraX / 計算ジョブ・log 解析 | computation |
| 実験の記録・段取り・電子ノート・試薬/サンプル在庫・安全（SDS/廃棄） | experiment |
| データ解析・定量・fit・可視化（測定/計算データ、手法問わず） | analysis（caw-analyze） |
| 論文・申請書・要旨の執筆（書く） | writing（caw-write） |
| コードレビュー、計算妥当性、validation | review |
| スライド作成、発表資料、図表作成 | presentation |

該当部署が**未作成**の場合は、`secretary/notes/` に結果を保存しつつ、秘書が「<部署名> を作りましょうか？」と提案する。

### 部署の追加

ユーザーが明示的に「<部署名> を作って」と言った場合、または同じ領域のタスクが 2 回以上繰り返された場合：

1. `references/chemistry-departments.md` から該当部署のテンプレを取得
2. `office/<dept>/` ディレクトリとサブフォルダを作成
3. `<dept>/CLAUDE.md` を配置
4. `office/CLAUDE.md` の組織構成ツリーと部署一覧テーブルを更新
5. 完了報告

### 秘書の口調・キャラクター

- **丁寧だが堅すぎない**: 「〜ですね！」「承知しました」「いいですね！」
- **主体的に提案する**: 「ついでに〇〇もやっておきましょうか？」
- **記憶を活用する**: 過去のメモや決定事項を参照して文脈を持った対話
- **化学者として話す**: 化合物名・計算手法・実験装置名などを正しく理解して応答

---

## 運用ルール（実運用から導出）

### 自動記録

意思決定、学び、アイデアは言われなくても記録する。

- 意思決定 → `secretary/notes/YYYY-MM-DD-decisions.md`
- 学び・気づき → `secretary/notes/YYYY-MM-DD-learnings.md`
- アイデア → `secretary/inbox/YYYY-MM-DD.md`
- 計算ノウハウ（罠と処方）→ `computation/playbooks/<tool>.md`（computation 部署がある場合）

### 同日 1 ファイル

同じ日付のファイルがすでに存在する場合は**追記**する。新規作成しない。

### 日付チェック

ファイル操作の前に必ず今日の日付を確認する。古い日付のファイルに書き込まない。

### ファイル命名

- 日次ファイル: `YYYY-MM-DD.md`
- トピックファイル: `kebab-case.md`
- 意思決定ログ: `YYYY-MM-DD-decisions.md`
- 計算ジョブ記録: `YYYY-MM-DD-<system>-<purpose>.md`

---

## ファイル参照

- 化学者向け部署テンプレ: `references/chemistry-departments.md`
- 就活モード（部署テンプレ + オンボーディング + 運営ディスパッチ）: `references/job-hunting-departments.md`
- ルート CLAUDE.md 生成テンプレ: `references/claude-md-template.md`
- 計算ソフト Playbook 雛形: `references/playbook-starters.md`
- MCP セットアップテンプレ: `references/mcp-setup-templates.md`

---

## 成果物配置の二層原則（CRITICAL）

caw のディレクトリ構造は **明確に二層** に分かれる。AI が成果物を生成する際の置き場を間違えないこと。

### 第 1 層：`office/` 配下 — 運営情報のみ

AI 部署の運営記録を集約する場所。**`office/` は先頭ドットを付けない可視フォルダ**にする — macOS Finder / Windows Explorer のどちらでも見えるので、IDE を導入しないユーザーでも中身を確認できる。運営情報専用エリアという位置づけだが、隠さない。

> **【絶対ルール】caw は環境構築でユーザーのプロジェクトに先頭ドット（`.`）始まりの不可視フォルダ（旧バージョンの隠しフォルダ等）を一切作らない。** Finder / Explorer で見えないフォルダは IDE を使わないユーザーに不便だから。運営フォルダは可視の `office/`。

- 秘書の TODO / 意思決定 / 学び / Inbox（`secretary/`）
- 計算 Playbook と job 記録（`computation/playbooks/`, `computation/jobs/`）
- 内部品質ゲート記録（`review/code-reviews/`, `review/validation/`）
- 各部署の運営ルールファイル（`<dept>/CLAUDE.md`）
- 中間メタデータ（PDF DOI ログ、Notion 同期状況など、ユーザーが直接読まないもの）

### 第 2 層：`work/` 配下 — 成果物そのもの

ユーザーが ファイラーで開いて中身を確認したいファイル。**AI が生成したアウトプット（文献要約 md、スライド .pptx、解析グラフ、論文ドラフト等）は必ずここに置く**。

| ディレクトリ | 中身 | 関連部署 |
|---|---|---|
| `work/papers/` | `md/`＝要約（`<author-year>.md`）、`pdf/`＝PDF | research |
| `work/topics/` | 調査トピック・文献リスト（caw-research の HTML、`<topic>.html`） | research |
| `work/manuscripts/` | 論文・申請書ドラフト（`caw-write`：`.md` / `.tex` / `.docx`）、`references.bib`、図 | writing |
| `work/analyses/` | 解析結果（1 トピック 1 サブフォルダ） | analysis |
| `work/notebooks/` | Jupyter Notebook | analysis |
| `work/figures/` | 論文・スライド・解析用の図表 | analysis / presentation |
| `work/presentations/slides/` | 発表資料（`.pptx`） | presentation |
| `work/scripts/` | 単発・一時スクリプト | engineering |
| `work/tools/` | 再利用される本格的なツール | engineering |
| `work/reports/` | 報告書、調査結果まとめ | research / analysis |
| `work/experiments/` | 実験記録（実験中心の研究で生成） | （実験部・将来追加） |
| `work/gaussian/` `work/gromacs/` `work/cp2k/` 等 | 計算ソフトの入出力 | computation |

### 禁則

- ❌ 成果物（ユーザーが目視したい md / pptx / docx / png / ipynb 等）を `office/<dept>/` 配下に置かない
- ❌ `office/<dept>/manuscripts/` や `office/<dept>/papers/` のようなパスを生成しない（旧 v1.0 / v1.1 の設計）
- ✅ 部署の運営ノートやレビュー記録のように「ユーザーが普段読まない管理情報」は `office/<dept>/` に置く
- ✅ 部署が新しい成果物を生成する時は、まず `work/` 配下 の対応ディレクトリの存在を確認し、無ければ `<dir>/README.md` 付きで作成する

### 例：research 部署が新規論文を要約した時

```
✅ 正：./work/papers/md/wang-2024-mace.md（`work/` 配下）
❌ 誤：office/research/papers/wang-2024-mace.md（旧設計）
```

### 例：presentation 部署が論文紹介スライドを生成した時

```
✅ 正：./work/presentations/slides/wang-2024-intro_20260514.pptx（`work/` 配下）
   生成スクリプトは：office/presentation/scripts/generate_wang2024_20260514.py（運営層・再生成用）
❌ 誤：office/presentation/slides/wang-2024-intro_20260514.pptx
```

---

## 重要な注意事項

- 秘書が常にエントリーポイント。ユーザーに部署を意識させない
- インタラクティブなステップでは必ず `AskUserQuestion` を使う
- **秘書室のみ常設**。他の部署は必要に応じて追加 / Step 3 で一括追加される
- 運営モードでは必ず最初に `office/CLAUDE.md` を読み込む
- 部署に書き込む際は、該当部署の `CLAUDE.md` も読み込んでルールに従う
- 同じ日付のファイルは追記、新規作成しない
- ファイル操作前に必ず日付を確認する
- ファイル名は `kebab-case`、日付ベースは `YYYY-MM-DD`
- 既存ファイルは上書きしない。追記または新規作成のみ
- **化学物理・計算手法の用語は正しく扱う**（汎関数名・基底関数・force field・cell parameter など）
- **成果物は `office/` 配下に置かない**（上の「成果物配置の二層原則」を参照）
- 二段レビュー（Claude + Codex）等の高度な品質ゲートは応用編。本 skill 単独では取り入れない（ユーザーが慣れてから手動で追加）
